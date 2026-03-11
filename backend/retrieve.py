"""
RAG Retrieval Validation Script
================================
Connects to the Qdrant collection populated by main.py (Spec-1: 007-embedding-pipeline),
embeds natural-language queries with Cohere, retrieves the top-K most similar chunks,
validates metadata integrity of every result, and prints a summary ValidationReport.

Usage:
    uv run python retrieve.py                    # runs 5 default queries
    uv run python retrieve.py "query1" "query2"  # custom queries

Environment variables (all from .env):
    Required: QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, COHERE_API_KEY
    Optional: COHERE_MODEL        (default: embed-english-v3.0)
              TOP_K               (default: 3)
              SCORE_THRESHOLD     (default: none — no filtering)

Exit codes:
    0  success — all queries completed
    1  missing required environment variable, or invalid optional value
    2  Qdrant connection failed or collection not found
    3  collection exists but contains 0 vectors
"""

# =============================================================================
# T001 — UTF-8 stdout fix (Windows cp1252 compatibility, same as main.py)
# =============================================================================
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Standard library
import os

# Third-party (all already in backend/pyproject.toml from Spec-1 — no new deps)
import cohere
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# =============================================================================
# T001 — Default queries (5 known book topics)
# =============================================================================
DEFAULT_QUERIES = [
    "What is prompt engineering?",
    "How do AI agents work?",
    "What are embeddings and vector databases?",
    "How to evaluate LLM outputs?",
    "What is retrieval-augmented generation?",
]

# Payload fields that every retrieved chunk MUST have (FR-005)
_REQUIRED_FIELDS = ["url", "title", "chunk_index", "text"]


# =============================================================================
# T002 + T011 — Config loading
# =============================================================================

def load_config() -> dict:
    """
    Load retrieval configuration from environment variables.

    Required: QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, COHERE_API_KEY
    Optional: COHERE_MODEL (default embed-english-v3.0)
              TOP_K (positive int, default 3)
              SCORE_THRESHOLD (float in [0.0, 1.0], default None)

    Raises SystemExit(1) on any missing required key or invalid optional value.
    """
    load_dotenv()

    # Required keys
    required_keys = ["QDRANT_URL", "QDRANT_API_KEY", "COLLECTION_NAME", "COHERE_API_KEY"]
    cfg: dict = {}
    missing = []

    for key in required_keys:
        value = os.getenv(key, "").strip()
        if not value:
            missing.append(key)
        else:
            cfg[key.lower()] = value

    if missing:
        for key in missing:
            print(f"ERROR: Required environment variable '{key}' is not set.", file=sys.stderr)
        print("Copy .env.example to .env and fill in your credentials.", file=sys.stderr)
        sys.exit(1)

    # Optional: Cohere model
    cfg["cohere_model"] = os.getenv("COHERE_MODEL", "embed-english-v3.0").strip()

    # Optional: TOP_K — must be a positive integer (FR-006)
    top_k_raw = os.getenv("TOP_K", "3").strip()
    try:
        top_k = int(top_k_raw)
        if top_k < 1:
            raise ValueError("must be >= 1")
    except ValueError:
        print(f"ERROR: TOP_K must be a positive integer, got: {top_k_raw!r}", file=sys.stderr)
        sys.exit(1)
    cfg["top_k"] = top_k

    # Optional: SCORE_THRESHOLD — float in [0.0, 1.0] or None (FR-006)
    threshold_raw = os.getenv("SCORE_THRESHOLD", "").strip()
    if threshold_raw:
        try:
            threshold = float(threshold_raw)
            if not (0.0 <= threshold <= 1.0):
                raise ValueError("out of range [0.0, 1.0]")
        except ValueError as exc:
            print(
                f"ERROR: SCORE_THRESHOLD must be a float in [0.0, 1.0], got: {threshold_raw!r} ({exc})",
                file=sys.stderr,
            )
            sys.exit(1)
        cfg["score_threshold"] = threshold
    else:
        cfg["score_threshold"] = None

    return cfg


# =============================================================================
# T003 — Qdrant connection and collection verification
# =============================================================================

def init_qdrant(config: dict) -> QdrantClient:
    """
    Create a QdrantClient and verify the target collection is ready.

    Raises SystemExit(2) if connection fails or collection not found.
    Raises SystemExit(3) if collection exists but has zero vectors.
    Returns a connected QdrantClient on success.
    """
    try:
        client = QdrantClient(
            url=config["qdrant_url"],
            api_key=config["qdrant_api_key"],
        )
        collection_info = client.get_collection(config["collection_name"])
    except Exception as exc:
        err = str(exc).lower()
        if "not found" in err or "doesn't exist" in err or "404" in err:
            print(
                f"ERROR: Collection '{config['collection_name']}' not found. "
                "Run main.py first to populate embeddings.",
                file=sys.stderr,
            )
        else:
            print(
                f"ERROR: Cannot connect to Qdrant at {config['qdrant_url']}. "
                f"Check QDRANT_URL and QDRANT_API_KEY. ({type(exc).__name__}: {exc})",
                file=sys.stderr,
            )
        sys.exit(2)

    points_count = collection_info.points_count or 0
    if points_count == 0:
        print(
            f"ERROR: Collection '{config['collection_name']}' exists but contains 0 vectors. "
            "Re-run main.py to populate embeddings.",
            file=sys.stderr,
        )
        sys.exit(3)

    print(
        f"[QDRANT]  Connected — "
        f"'{config['collection_name']}' has {points_count} vector(s)  "
        f"top_k={config['top_k']}  "
        f"threshold={config['score_threshold']}"
    )
    return client


# =============================================================================
# T004 + T013 — Query embedding
# =============================================================================

def embed_query(text: str, config: dict) -> list:
    """
    Embed a single query string using Cohere with input_type='search_query'.

    Returns a list of 1024 floats.
    Uses input_type='search_query' (asymmetric search — must differ from ingestion's
    'search_document' to produce correct cosine similarity rankings).
    Raises on Cohere API failure (T013 error wrapper).
    """
    co = cohere.ClientV2(api_key=config["cohere_api_key"])
    try:
        response = co.embed(
            texts=[text],
            model=config["cohere_model"],
            input_type="search_query",
            embedding_types=["float"],
        )
    except Exception as exc:
        print(f"ERROR: Cohere API call failed: {exc}", file=sys.stderr)
        raise
    return response.embeddings.float_[0]


# =============================================================================
# T005 + T012 — Vector retrieval
# =============================================================================

def retrieve(client: QdrantClient, query_vector: list, config: dict) -> list:
    """
    Retrieve the top-K most similar chunks from Qdrant for a given query vector.

    Applies SCORE_THRESHOLD server-side when configured (FR-006).
    Uses query_points() — the current qdrant-client 1.17 API (search() removed).
    Returns a list of ScoredPoint objects.
    """
    return client.query_points(
        collection_name=config["collection_name"],
        query=query_vector,
        limit=config["top_k"],
        with_payload=True,
        score_threshold=config["score_threshold"],
    ).points


# =============================================================================
# T006 — Result printing
# =============================================================================

def print_results(query_text: str, results: list) -> None:
    """
    Print ranked retrieval results to stdout.

    Each result shows: rank, score, source URL, page title, chunk index, text snippet.
    """
    print("=" * 60)
    print(f'Query: "{query_text}"')
    print("-" * 60)

    if not results:
        print("  (no results returned)")
        return

    for rank, result in enumerate(results, start=1):
        payload = result.payload or {}
        url = payload.get("url", "(no url)")
        title = payload.get("title", "(no title)")
        chunk_index = payload.get("chunk_index", "?")
        snippet = (payload.get("text") or "")[:150].replace("\n", " ")

        print(f"  #{rank}  score={result.score:.2f}  {url}")
        print(f"       title: {title}")
        print(f"       chunk: {chunk_index}")
        print(f"       text:  \"{snippet}...\"")
        print()


# =============================================================================
# T008 — Payload validation
# =============================================================================

def validate_payload(result, rank: int, query_text: str) -> tuple:
    """
    Validate that a ScoredPoint payload contains all required fields.

    Checks: url, title, chunk_index, text — each must be present and non-empty.
    Prints a WARNING line to stdout for each missing or empty field (FR-005).
    Returns (is_valid: bool, missing_fields: list[str]).
    """
    payload = result.payload or {}
    missing = []

    for field in _REQUIRED_FIELDS:
        value = payload.get(field)
        is_empty = (
            value is None
            or (isinstance(value, str) and not value.strip())
        )
        if is_empty:
            print(
                f"WARNING: Result #{rank} for query \"{query_text[:40]}\" "
                f"is missing field '{field}'."
            )
            missing.append(field)

    return (len(missing) == 0, missing)


# =============================================================================
# T010 — Validation report
# =============================================================================

def print_validation_report(
    query_count: int,
    total_results: int,
    valid_count: int,
    invalid_count: int,
) -> None:
    """Print a ValidationReport summary after all queries have been processed."""
    overall = "PASS" if invalid_count == 0 and query_count > 0 else "FAIL"
    print("-" * 60)
    print("Validation Report")
    print("-" * 60)
    print(f"Queries run    : {query_count}")
    print(f"Results found  : {total_results}")
    print(f"Metadata valid : {valid_count} / {total_results}")
    if invalid_count > 0:
        print(f"Metadata FAIL  : {invalid_count} result(s) have missing fields")
    print(f"Overall        : {overall}")
    print("-" * 60)


# =============================================================================
# T007 + T009 — main() orchestrator
# =============================================================================

def main() -> None:
    """
    Retrieval validation pipeline:
      1. load_config()       — validate env vars, parse TOP_K / SCORE_THRESHOLD
      2. init_qdrant()       — connect and verify collection is non-empty
      3. For each query:
           embed_query()     — Cohere ClientV2 search_query embedding
           retrieve()        — top-K ScoredPoints from Qdrant
           print_results()   — human-readable ranked output
           validate_payload()— check url/title/chunk_index/text per result
      4. print_validation_report() — summary with PASS/FAIL
      5. sys.exit(0)
    """
    config = load_config()

    # FR-007: accept queries from CLI args or fall back to hardcoded defaults
    raw_queries = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_QUERIES

    # Warn and skip empty/whitespace-only queries
    queries = []
    for i, q in enumerate(raw_queries):
        if q.strip():
            queries.append(q.strip())
        else:
            print(f"WARNING: Skipping empty query at position {i}.")

    if not queries:
        print("ERROR: No valid queries to run.", file=sys.stderr)
        sys.exit(1)

    client = init_qdrant(config)
    print()

    # Accumulate ValidationReport counters (T009)
    total_results = 0
    valid_count = 0
    invalid_count = 0

    for query_text in queries:
        # Embed
        try:
            query_vector = embed_query(query_text, config)
        except Exception:
            print(f"Skipping query due to embedding error: \"{query_text}\"")
            continue

        # Retrieve
        results = retrieve(client, query_vector, config)

        # Print
        print_results(query_text, results)

        # Validate payload for each result (T008 + T009)
        for rank, result in enumerate(results, start=1):
            total_results += 1
            is_valid, _ = validate_payload(result, rank, query_text)
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

    # T010 — ValidationReport
    print()
    print_validation_report(len(queries), total_results, valid_count, invalid_count)

    sys.exit(0)


if __name__ == "__main__":
    main()
