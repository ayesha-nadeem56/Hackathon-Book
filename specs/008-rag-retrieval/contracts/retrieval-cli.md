# Contract: Retrieval CLI Script

**Feature**: 008-rag-retrieval | **Date**: 2026-03-10
**Artifact**: `backend/retrieve.py`

---

## CLI Interface

### Invocation

```bash
# From backend/ directory:
uv run python retrieve.py [query1] [query2] ...

# Examples:
uv run python retrieve.py
uv run python retrieve.py "What is prompt engineering?"
uv run python retrieve.py "How do AI agents work?" "What are embeddings?"
```

### Arguments

| Argument | Type | Required | Default |
|----------|------|----------|---------|
| `query1..N` | positional strings | ❌ | 5 hardcoded default queries |

If no CLI arguments are provided, the script runs the default query list defined at the top of the file.

---

## Environment Variables (all loaded from `backend/.env`)

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `QDRANT_URL` | str | ✅ | — | Qdrant Cloud endpoint |
| `QDRANT_API_KEY` | str | ✅ | — | Qdrant API key |
| `COLLECTION_NAME` | str | ✅ | — | Vector collection name |
| `COHERE_API_KEY` | str | ✅ | — | Cohere API key |
| `COHERE_MODEL` | str | ❌ | `embed-english-v3.0` | Embedding model name |
| `TOP_K` | int | ❌ | `3` | Max results per query |
| `SCORE_THRESHOLD` | float | ❌ | None | Min similarity score filter |

---

## Output Format (stdout)

```
============================================================
Query 1: "What is prompt engineering?"
------------------------------------------------------------
  #1  score=0.68  url=https://hackathon-book-uogx.vercel.app/docs/chapter-1
      title: Chapter 1 — Introduction to Prompt Engineering
      chunk: 0
      text: "Prompt engineering is the practice of designing inputs to guide..."

  #2  score=0.61  url=https://hackathon-book-uogx.vercel.app/docs/chapter-2
      title: Chapter 2 — Advanced Prompting Techniques
      chunk: 3
      text: "Few-shot prompting provides examples within the prompt to..."

  #3  score=0.55  url=https://hackathon-book-uogx.vercel.app/docs/chapter-1
      title: Chapter 1 — Introduction to Prompt Engineering
      chunk: 2
      text: "The goal of prompt engineering is to maximize the relevance..."

============================================================
...

------------------------------------------------------------
Validation Report
------------------------------------------------------------
Queries run    : 5
Results found  : 15
Metadata valid : 15 / 15
Overall        : PASS
------------------------------------------------------------
```

---

## Exit Codes

| Code | Condition |
|------|-----------|
| `0` | All queries completed; validation report printed |
| `1` | Missing required environment variable(s) |
| `2` | Qdrant connection failed or collection not found |
| `3` | Qdrant collection exists but contains 0 vectors |

---

## Error Messages (stderr)

| Condition | Message |
|-----------|---------|
| Missing env var | `ERROR: Required environment variable 'QDRANT_URL' is not set.` |
| Qdrant unreachable | `ERROR: Cannot connect to Qdrant at <url>. Check QDRANT_URL and QDRANT_API_KEY.` |
| Collection not found | `ERROR: Collection 'book-embeddings' not found. Run main.py first to populate embeddings.` |
| Empty collection | `ERROR: Collection 'book-embeddings' exists but contains 0 vectors. Re-run main.py.` |
| Missing payload field | `WARNING: Result #<n> for query "<q>" is missing field '<field>'.` |
| Empty query | `WARNING: Skipping empty query at position <i>.` |

---

## Functional Requirement Mapping

| FR | Implemented By |
|----|----------------|
| FR-001: Connect and verify collection | `init_qdrant()` |
| FR-002: Embed query with Cohere search_query | `embed_query()` |
| FR-003: Retrieve top-K chunks | `retrieve()` via `client.query_points()` |
| FR-004: Display rank/score/URL/snippet | `print_results()` |
| FR-005: Validate payload fields; log WARNING | `validate_payload()` |
| FR-006: TOP_K and SCORE_THRESHOLD from env | `load_config()` |
| FR-007: Default queries + CLI args | `main()` using `sys.argv[1:]` |
| FR-008: Exit codes 0/non-zero | `main()` |
| FR-009: All config from .env | `load_config()` with `python-dotenv` |
