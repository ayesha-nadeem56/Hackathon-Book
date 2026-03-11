# Research: RAG Retrieval Validation Pipeline

**Feature**: 008-rag-retrieval | **Date**: 2026-03-10
**Status**: Complete — all NEEDS CLARIFICATION resolved

---

## R-001: Qdrant Client API (v1.17)

**Question**: Which query API to use after `client.search()` was removed?

**Decision**: Use `client.query_points(collection_name, query=vector, limit=k, with_payload=True)`

**Rationale**: `search()` was deprecated and removed in qdrant-client ≥ 1.14. The replacement is `query_points()`, which accepts a `query` argument (raw float list treated as a dense vector query). Result objects have `.id`, `.score`, and `.payload` attributes. Already verified working in Spec-1 `main.py::test_retrieval()`.

**Alternatives considered**: `search()` — removed; `recommend()` — requires existing point IDs, not a query vector.

**Code pattern** (verified in Spec-1):
```python
results = client.query_points(
    collection_name=collection_name,
    query=query_vector,          # list[float], length 1024
    limit=top_k,                 # int
    with_payload=True,
    score_threshold=score_threshold,  # float | None
).points
# Each result: result.score (float), result.payload (dict)
```

---

## R-002: Cohere ClientV2 — Search Query Embedding

**Question**: Which `input_type` and client class to use for query embedding?

**Decision**: `cohere.ClientV2(api_key).embed(texts=[query], model="embed-english-v3.0", input_type="search_query", embedding_types=["float"])`

**Rationale**: Cohere v5+ SDK uses `ClientV2` (not `Client`). For retrieval, queries must use `input_type="search_query"` while documents use `"search_document"`. This asymmetry is required for cosine similarity to correctly rank relevance. Already verified in Spec-1 ingestion side.

**Alternatives considered**: `cohere.Client` — legacy v4 API, deprecated in v5+.

**Code pattern**:
```python
import cohere
co = cohere.ClientV2(api_key=cohere_api_key)
response = co.embed(
    texts=[query_text],
    model="embed-english-v3.0",
    input_type="search_query",
    embedding_types=["float"],
)
query_vector = response.embeddings.float[0]  # list[float], len=1024
```

---

## R-003: Score Threshold Filtering

**Question**: Does Qdrant's `query_points()` support server-side score filtering, or must filtering be done client-side?

**Decision**: Use `score_threshold` parameter in `query_points()` for server-side filtering when `SCORE_THRESHOLD` is set; default to `None` (no filtering).

**Rationale**: `query_points()` accepts an optional `score_threshold: float | None` parameter. When set, Qdrant only returns points with score ≥ threshold, reducing network payload. When `None`, all top-K results are returned regardless of score.

**Alternatives considered**: Client-side filtering with `[r for r in results if r.score >= threshold]` — less efficient, returns extra results over the wire.

---

## R-004: Exit Code Taxonomy

**Question**: Which exit codes should the script use for each failure mode?

**Decision**:

| Code | Meaning |
|------|---------|
| 0 | All queries completed successfully |
| 1 | Missing required configuration (env vars) |
| 2 | Qdrant connection failed or collection not found |
| 3 | Collection exists but has zero vectors |

**Rationale**: Distinct exit codes make CI integration and debugging unambiguous. Follows UNIX conventions (0=success, non-zero=error, lower codes=config, higher=runtime).

---

## R-005: Default Queries

**Question**: What default queries should be included for quick sanity-check runs?

**Decision**: Use 5 queries covering main book topics:
1. `"What is prompt engineering?"`
2. `"How do AI agents work?"`
3. `"What are embeddings and vector databases?"`
4. `"How to evaluate LLM outputs?"`
5. `"What is retrieval-augmented generation?"`

**Rationale**: These cover the known chapters from Spec-1's 12 local docs. They are broad enough to return relevant results with score > 0.5 against the `book-embeddings` collection.

---

## R-006: UTF-8 Stdout on Windows

**Question**: Does `retrieve.py` need the same Windows UTF-8 fix as `main.py`?

**Decision**: Yes — add `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at the top of the script, same pattern as Spec-1.

**Rationale**: Book text may contain non-ASCII characters (quotes, dashes, Unicode). Windows cp1252 stdout will raise `UnicodeEncodeError` without this fix. Already proven necessary in Spec-1.

---

## R-007: File Location

**Question**: User said "create retrieve.py in the root" — should it go in repo root or `backend/`?

**Decision**: `backend/retrieve.py` — same directory as `main.py`.

**Rationale**: The spec (Assumptions section) explicitly states "The retrieval script lives in backend/ and shares the .env file and uv project from Spec-1." Placing it in `backend/` gives it automatic access to the `.venv`, `pyproject.toml`, and `.env` without any path manipulation.
