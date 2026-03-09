# Implementation Plan: Book Content Embedding Pipeline

**Branch**: `007-embedding-pipeline` | **Date**: 2026-03-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-embedding-pipeline/spec.md`

## Summary

Build a single-file Python pipeline (`backend/main.py`) that crawls all public pages of the deployed Docusaurus book site (`https://hackathon-book-uogx.vercel.app/`), cleans and chunks the text, generates vector embeddings via Cohere, and upserts them with metadata into a Qdrant Cloud collection. A `main()` function orchestrates all stages end-to-end. The project is managed with `uv` and all secrets are externalised to `.env`.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `httpx` (HTTP crawling), `beautifulsoup4` + `lxml` (HTML parsing), `cohere` (embeddings), `qdrant-client` (vector store), `python-dotenv` (config), `tqdm` (progress)
**Storage**: Qdrant Cloud (Free Tier) — cosine similarity collection, 1024-dimension vectors
**Testing**: `pytest` — unit tests for cleaner/chunker; integration test for full pipeline
**Target Platform**: Local developer machine / Linux (any OS with Python 3.11+)
**Project Type**: Single-file script managed with `uv`
**Performance Goals**: Full ingestion in < 10 minutes for ~50–200 pages; Cohere batch calls of 96 chunks max
**Constraints**: Free-tier Qdrant (~1GB storage, sufficient for ~250k 1024-dim float32 vectors); no hardcoded secrets; single `main.py` with clear function separation
**Scale/Scope**: ~50–200 Docusaurus pages; ~500–3000 chunks total; well within free-tier limits

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Status |
|-----------|-------|--------|
| I. Accuracy & Technical Correctness | Pipeline uses official Cohere + Qdrant SDKs; embeddings are reproducible; model version is pinned | ✅ PASS |
| II. Clarity & Readability | Single `main.py` with named stages, docstrings, and inline comments | ✅ PASS |
| III. Reproducibility | `uv.lock` pins all deps; `.env.example` documents every required variable | ✅ PASS |
| IV. Modularity & Maintainable Architecture | Each stage is a pure function; `main()` is a thin orchestrator; smallest viable diff | ✅ PASS |
| V. Transparency in AI-Generated Content | Pipeline ingests only existing book content; no AI generation; no hallucination risk | ✅ PASS |

**No violations — complexity tracking table not required.**

## Project Structure

### Documentation (this feature)

```text
specs/007-embedding-pipeline/
├── plan.md              # This file
├── research.md          # Phase 0 — technology decisions
├── data-model.md        # Phase 1 — Python types and Qdrant payload schema
├── quickstart.md        # Phase 1 — setup and run guide
├── contracts/
│   └── ingestion-pipeline.md   # Phase 1 — function signatures and contracts
└── tasks.md             # Phase 2 — /sp.tasks output (NOT created here)
```

### Source Code (repository root)

```text
backend/
├── main.py           # Single pipeline script — all stages in one file
├── pyproject.toml    # uv project metadata and dependencies
├── uv.lock           # Pinned lockfile (committed)
├── .env              # Runtime secrets — GITIGNORED
└── .env.example      # Template for .env — committed
```

**Structure Decision**: Single-project layout under `backend/` as explicitly requested. `main.py` is the sole source file; no sub-packages. Functions are grouped by pipeline stage within the file. This satisfies the "smallest viable change" principle while meeting all functional requirements.

## Phase 0: Research Summary

See [`research.md`](./research.md) for full findings. Key decisions:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Crawling strategy | Sitemap-first, recursive fallback | Docusaurus v2 generates `/sitemap.xml`; most reliable source of all public URLs |
| Embedding model | `embed-english-v3.0` | Latest Cohere English model; 1024 dims; best quality; free tier available |
| Vector distance | Cosine | Industry standard for semantic text similarity |
| Chunk size | 1000 chars, 200 overlap | Balances context window and retrieval granularity; configurable |
| Batch size | 96 chunks/call | Cohere API limit for `embed-english-v3.0` |
| Upsert strategy | Upsert (overwrite) | Idempotent re-runs; no versioning required per spec |
| Point ID scheme | Deterministic UUID from `url + chunk_index` | Allows upsert to overwrite existing chunks cleanly |

## Phase 1: Design

### Pipeline Architecture

```
BASE_URL
   │
   ▼
[1. CRAWL]  sitemap.xml → list of page URLs (same-domain only)
   │         └─ fallback: recursive link extraction from BASE_URL
   ▼
[2. FETCH]  httpx GET each URL → (url, title, raw HTML, status)
   │         └─ skip 4xx/5xx, log and continue
   ▼
[3. CLEAN]  BeautifulSoup → strip nav/footer/code/scripts → plain text
   │         └─ skip pages with < MIN_CHARS cleaned text
   ▼
[4. CHUNK]  sliding window (CHUNK_SIZE chars, CHUNK_OVERLAP overlap)
   │         └─ split at sentence boundary near window edge
   ▼
[5. EMBED]  Cohere embed-english-v3.0 in batches of EMBED_BATCH_SIZE
   │         input_type="search_document"
   ▼
[6. STORE]  Qdrant upsert — vector + payload per chunk
   │         create collection if not exists
   ▼
[7. VERIFY] embed 3 test queries (input_type="search_query")
            → Qdrant search → print top-3 results per query
```

### Configuration (Environment Variables)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BASE_URL` | YES | — | Root URL of the Docusaurus site |
| `COHERE_API_KEY` | YES | — | Cohere API key |
| `QDRANT_URL` | YES | — | Qdrant Cloud cluster endpoint |
| `QDRANT_API_KEY` | YES | — | Qdrant API key |
| `COLLECTION_NAME` | no | `book-embeddings` | Qdrant collection name |
| `COHERE_MODEL` | no | `embed-english-v3.0` | Cohere embedding model |
| `CHUNK_SIZE` | no | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | no | `200` | Overlap between adjacent chunks |
| `EMBED_BATCH_SIZE` | no | `96` | Chunks per Cohere API call |
| `MIN_CHUNK_CHARS` | no | `100` | Minimum characters to form a valid chunk |

### Error Handling Strategy

| Failure | Behaviour |
|---------|-----------|
| Page fetch error (4xx/5xx/timeout) | Log URL + error, skip page, continue |
| Empty/navigation-only page | Log URL, skip page, continue |
| Cohere API error | Raise immediately — pipeline halts (re-run safe via upsert) |
| Qdrant write error | Raise immediately — pipeline halts (re-run safe via upsert) |
| Missing required env var | Raise `ValueError` at startup before any network calls |

### Qdrant Collection Schema

```
Collection: book-embeddings (configurable)
Vector:
  size: 1024
  distance: Cosine

Payload per point:
  url:         str   — source page URL
  title:       str   — page <title> or <h1>
  chunk_index: int   — 0-based position within page
  text:        str   — verbatim chunk text (for display in retrieval)
  char_count:  int   — length of text field

Point ID: deterministic UUID5 derived from (url + chunk_index)
           → upsert is idempotent; re-runs overwrite cleanly
```

## Complexity Tracking

No violations — table not applicable.
