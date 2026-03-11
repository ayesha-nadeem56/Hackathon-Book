"""
RAG Book Q&A Agent
==================
An interactive conversational agent that answers questions about the book
by retrieving relevant passages from the Qdrant vector store and grounding
its answers exclusively in that retrieved content.

Usage:
    cd backend && uv run python ../agent.py

Environment variables (from backend/.env):
    Required: GROQ_API_KEY, QDRANT_URL, QDRANT_API_KEY,
              COLLECTION_NAME, COHERE_API_KEY
    Optional: COHERE_MODEL     (default: embed-english-v3.0)
              TOP_K            (default: 3)
              SCORE_THRESHOLD  (default: none)
              AGENT_MODEL      (default: llama-3.3-70b-versatile)

Exit codes:
    0  normal exit (user typed quit or Ctrl-C)
    1  missing required environment variable
    2  Qdrant connection failed or collection not found
    3  collection exists but has zero vectors
"""

# =============================================================================
# T002 — UTF-8 stdout fix (Windows cp1252 compatibility)
# =============================================================================
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Standard library
import asyncio
import os
import pathlib

# Path to backend/.env, resolved relative to this file (works from any CWD)
_ENV_PATH = pathlib.Path(__file__).parent / "backend" / ".env"

# Third-party
import cohere
from agents import Agent, MultiProvider, RunConfig, Runner, function_tool, set_tracing_disabled
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# =============================================================================
# T009 — Grounding system prompt (FR-003, FR-006)
# =============================================================================
_GROUNDING_PROMPT = (
    "You are a helpful assistant that answers questions about this book's content.\n"
    "You MUST call the retrieve_book_content tool for every question to find relevant passages.\n"
    "Only answer based on what the tool returns. "
    "Do not use your training knowledge to answer factual questions about the book's topics.\n"
    "If the tool returns no relevant passages, say exactly: "
    "\"I don't have relevant information in the book to answer that question.\"\n"
    "Always cite the source URLs from the retrieved passages at the end of your answer."
)

# Required fields every retrieved payload must have
_REQUIRED_FIELDS = ["url", "title", "chunk_index", "text"]


# =============================================================================
# T003 + T013 — Config loading
# =============================================================================

def load_config() -> dict:
    """
    Load agent configuration from backend/.env.

    Required: OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, COHERE_API_KEY
    Optional: COHERE_MODEL (default embed-english-v3.0), AGENT_MODEL (default gpt-4o),
              TOP_K (positive int, default 3), SCORE_THRESHOLD (float [0,1] or None)

    Exits with code 1 on any missing required key or invalid optional value.
    """
    load_dotenv(_ENV_PATH)

    required_keys = [
        "GROQ_API_KEY",
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "COLLECTION_NAME",
        "COHERE_API_KEY",
    ]
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
        print("Add the missing key(s) to backend/.env and retry.", file=sys.stderr)
        sys.exit(1)

    cfg["cohere_model"] = os.getenv("COHERE_MODEL", "embed-english-v3.0").strip()
    cfg["agent_model"] = os.getenv("AGENT_MODEL", "llama-3.3-70b-versatile").strip()

    # T013 — TOP_K: positive integer
    top_k_raw = os.getenv("TOP_K", "3").strip()
    try:
        top_k = int(top_k_raw)
        if top_k < 1:
            raise ValueError("must be >= 1")
    except ValueError:
        print(f"ERROR: TOP_K must be a positive integer, got: {top_k_raw!r}", file=sys.stderr)
        sys.exit(1)
    cfg["top_k"] = top_k

    # T013 — SCORE_THRESHOLD: float in [0.0, 1.0] or None
    threshold_raw = os.getenv("SCORE_THRESHOLD", "").strip()
    if threshold_raw:
        try:
            threshold = float(threshold_raw)
            if not (0.0 <= threshold <= 1.0):
                raise ValueError("out of range [0.0, 1.0]")
        except ValueError as exc:
            print(
                f"ERROR: SCORE_THRESHOLD must be a float in [0.0, 1.0], "
                f"got: {threshold_raw!r} ({exc})",
                file=sys.stderr,
            )
            sys.exit(1)
        cfg["score_threshold"] = threshold
    else:
        cfg["score_threshold"] = None

    return cfg


# =============================================================================
# T004 — Qdrant connection and collection verification
# =============================================================================

def init_qdrant(config: dict) -> QdrantClient:
    """
    Create a QdrantClient and verify the target collection is ready.

    Exits with 2 if connection fails or collection not found.
    Exits with 3 if collection has zero vectors.
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
                "Run backend/main.py first to populate embeddings.",
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
            "Re-run backend/main.py to populate embeddings.",
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
# T005 — Query embedding (Cohere ClientV2, search_query)
# =============================================================================

def embed_query(text: str, config: dict) -> list:
    """
    Embed a single query string using Cohere with input_type='search_query'.

    Returns a list of 1024 floats. Raises on API failure.
    """
    co = cohere.ClientV2(api_key=config["cohere_api_key"])
    response = co.embed(
        texts=[text],
        model=config["cohere_model"],
        input_type="search_query",
        embedding_types=["float"],
    )
    return response.embeddings.float_[0]


# =============================================================================
# T006 + T014 — Vector retrieval (qdrant-client 1.17 API)
# =============================================================================

def retrieve_from_qdrant(client: QdrantClient, query_vector: list, config: dict) -> list:
    """
    Retrieve top-K most similar chunks from Qdrant.

    Uses query_points() (search() was removed in qdrant-client 1.14+).
    Applies SCORE_THRESHOLD server-side when configured.
    Returns list of ScoredPoint objects.
    """
    return client.query_points(
        collection_name=config["collection_name"],
        query=query_vector,
        limit=config["top_k"],
        with_payload=True,
        score_threshold=config["score_threshold"],
    ).points


# =============================================================================
# T007 — Passage formatting
# =============================================================================

def format_passages(results: list) -> str:
    """
    Format a list of ScoredPoint objects into a readable string for the agent.

    Returns "No relevant passages found..." when results is empty.
    """
    if not results:
        return "No relevant passages found in the book for this query."

    lines = []
    for rank, result in enumerate(results, start=1):
        payload = result.payload or {}
        url = payload.get("url", "(no url)")
        title = payload.get("title", "(no title)")
        snippet = (payload.get("text") or "")[:200].replace("\n", " ")

        lines.append(f"[Passage {rank}] score={result.score:.2f}")
        lines.append(f"Title: {title}")
        lines.append(f"URL: {url}")
        lines.append(f'Text: "{snippet}..."')
        lines.append("")

    return "\n".join(lines).strip()


# =============================================================================
# T008 + T009 — Agent construction with @function_tool and grounding prompt
# =============================================================================

def build_agent(config: dict, client: QdrantClient) -> Agent:
    """
    Build the BookAgent with a retrieval tool and strict grounding instructions.

    The retrieve_book_content tool is defined as a closure capturing config and client,
    ensuring it has access to credentials and the active Qdrant connection.
    """

    @function_tool
    def retrieve_book_content(query: str) -> str:
        """Retrieve relevant passages from the book for a given question.

        Args:
            query: The natural-language search query to find relevant passages.
        """
        try:
            query_vector = embed_query(query, config)
            results = retrieve_from_qdrant(client, query_vector, config)
        except Exception as exc:
            return f"Error retrieving passages: {exc}"
        return format_passages(results)

    agent = Agent(
        name="BookAgent",
        instructions=_GROUNDING_PROMPT,
        model=config["agent_model"],
        tools=[retrieve_book_content],
    )

    run_config = RunConfig(
        model_provider=MultiProvider(
            openai_base_url="https://api.groq.com/openai/v1",
            openai_api_key=config["groq_api_key"],
            openai_use_responses=False,
        )
    )

    return agent, run_config


# =============================================================================
# T010 + T012 + T015 — REPL loop with multi-turn history and graceful exit
# =============================================================================

async def run_repl(agent: Agent, run_config: RunConfig) -> None:
    """
    Interactive REPL loop for the book Q&A agent.

    - T010: Basic question → answer flow
    - T012: Multi-turn history via result.to_input_list()
    - T015: KeyboardInterrupt and normal quit handling
    """
    print("[AGENT]   BookAgent ready. Ask a question about the book. Type 'quit' to exit.\n")

    history = None  # None = first turn; list = subsequent turns (to_input_list)

    try:
        while True:
            try:
                user_input = input("> ").strip()
            except EOFError:
                print("\nGoodbye!")
                break

            if not user_input:
                print("(Please type a question.)")
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            # T012 — Build runner input: first turn = str, subsequent = history list
            if history is None:
                runner_input = user_input
            else:
                history.append({"role": "user", "content": user_input})
                runner_input = history

            try:
                result = await Runner.run(agent, runner_input, run_config=run_config)
            except Exception as exc:
                print(f"\nERROR: Agent call failed: {exc}\n")
                continue

            print(f"\n{result.final_output}\n")

            # T012 — Save history for next turn (to_input_list includes all messages)
            history = result.to_input_list()

    except KeyboardInterrupt:
        print("\nGoodbye!")

    sys.exit(0)


# =============================================================================
# T011 — main() entry point
# =============================================================================

def main() -> None:
    """
    Orchestrate the RAG agent pipeline:
      1. load_config()      — validate env vars
      2. init_qdrant()      — connect and verify collection
      3. build_agent()      — create Agent with retrieval tool + grounding prompt
      4. asyncio.run(...)   — start interactive REPL
    """
    set_tracing_disabled(True)
    config = load_config()
    client = init_qdrant(config)
    agent, run_config = build_agent(config, client)
    asyncio.run(run_repl(agent, run_config))


if __name__ == "__main__":
    main()
