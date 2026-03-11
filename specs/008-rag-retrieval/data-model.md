# Data Model: RAG Retrieval Validation Pipeline

**Feature**: 008-rag-retrieval | **Date**: 2026-03-10

---

## Entities

### Config

Loaded at startup from `.env` via `python-dotenv`. All fields validated; missing required fields raise `SystemExit(1)`.

| Field | Type | Source | Required | Default | Notes |
|-------|------|--------|----------|---------|-------|
| `qdrant_url` | `str` | `QDRANT_URL` | ✅ | — | Qdrant Cloud cluster endpoint |
| `qdrant_api_key` | `str` | `QDRANT_API_KEY` | ✅ | — | JWT bearer token |
| `collection_name` | `str` | `COLLECTION_NAME` | ✅ | — | Must match Spec-1 ingestion collection |
| `cohere_api_key` | `str` | `COHERE_API_KEY` | ✅ | — | Cohere production key |
| `cohere_model` | `str` | `COHERE_MODEL` | ❌ | `"embed-english-v3.0"` | Must match Spec-1 model |
| `top_k` | `int` | `TOP_K` | ❌ | `3` | Max results per query |
| `score_threshold` | `float \| None` | `SCORE_THRESHOLD` | ❌ | `None` | Minimum score filter; None = no filter |

**Validation rules**:
- `qdrant_url`, `qdrant_api_key`, `collection_name`, `cohere_api_key` must be non-empty strings.
- `top_k` must be a positive integer (≥ 1).
- `score_threshold` must be a float in [0.0, 1.0] if provided; `None` is valid.

---

### Query

A natural-language string to embed and retrieve against.

| Field | Type | Constraints |
|-------|------|-------------|
| `text` | `str` | Non-empty, non-whitespace-only |

**Validation**: Empty or whitespace-only queries are skipped with a printed warning; they do not cause script failure.

---

### RetrievalResult

A single point returned by Qdrant, augmented with validation status.

| Field | Type | Source | Required |
|-------|------|--------|----------|
| `rank` | `int` | computed (1-based) | ✅ |
| `score` | `float` | `ScoredPoint.score` | ✅ |
| `url` | `str` | `payload["url"]` | ✅ |
| `title` | `str` | `payload["title"]` | ✅ |
| `chunk_index` | `int` | `payload["chunk_index"]` | ✅ |
| `text` | `str` | `payload["text"]` | ✅ |
| `valid` | `bool` | computed from payload validation | ✅ |
| `missing_fields` | `list[str]` | computed | ✅ |

**Payload field requirements** (from FR-005):
- `url`: non-empty string
- `title`: non-empty string
- `chunk_index`: integer ≥ 0
- `text`: non-empty string (≥ 1 character)

---

### ValidationReport

Summary of a full retrieval run across all queries.

| Field | Type | Description |
|-------|------|-------------|
| `query_count` | `int` | Total queries attempted |
| `result_count` | `int` | Total results retrieved across all queries |
| `valid_count` | `int` | Results with all required payload fields present |
| `invalid_count` | `int` | Results with one or more missing fields |
| `overall_pass` | `bool` | True if `invalid_count == 0` and `query_count > 0` |

---

## State Transitions

```
Script Start
    │
    ▼
load_config() ──── missing required key ──→ SystemExit(1)
    │
    ▼
init_qdrant() ──── connection failed ──────→ SystemExit(2)
    │           └─ collection missing ─────→ SystemExit(2)
    │           └─ collection empty ───────→ SystemExit(3)
    │
    ▼
For each query:
    embed_query() ──── Cohere error ───────→ print error + continue (or raise)
        │
        ▼
    retrieve() ────── returns [] if no match (valid, not an error)
        │
        ▼
    validate_payload() ── missing fields ──→ log WARNING per field
        │
        ▼
    print_results()
    │
    ▼
print ValidationReport summary
    │
    ▼
SystemExit(0)
```

---

## Relationships

- `Config` is created once per script run and passed to all functions.
- `Query` (0..N) are processed sequentially; each produces 0..TOP_K `RetrievalResult` objects.
- `ValidationReport` aggregates all `RetrievalResult` objects from all queries.
- `retrieve.py` shares `.env` with `main.py` (Spec-1); `Config` reads the same keys.
