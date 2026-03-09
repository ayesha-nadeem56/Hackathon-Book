# Contract: Ingestion Pipeline (`backend/main.py`)

**Feature**: `007-embedding-pipeline` | **Date**: 2026-03-09
**Scope**: All public functions in `backend/main.py`

---

## Module-Level Contract

`backend/main.py` is a self-contained pipeline script. It has no external imports beyond the declared dependencies. All state is passed explicitly between functions — no module-level mutable globals except the `Config` singleton loaded at startup.

---

## Function Contracts

### `load_config() -> Config`

Reads all environment variables (via `python-dotenv`), validates required fields, and returns a `Config` dataclass.

**Raises**: `ValueError` if any required field (`BASE_URL`, `COHERE_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`) is missing or empty.
**Side effects**: Calls `load_dotenv()` once.

---

### `fetch_sitemap(base_url: str) -> list[str]`

Fetches `{base_url}/sitemap.xml` and extracts all `<loc>` URLs that belong to the same domain.

**Input**: `base_url` — root URL of the documentation site (e.g., `https://hackathon-book-uogx.vercel.app/`)
**Output**: List of absolute page URLs (strings), deduplicated, same-domain only
**On failure**: If sitemap returns non-200 or is malformed, returns empty list (caller falls back to `crawl_links`)
**Side effects**: One HTTP GET request

---

### `crawl_links(base_url: str) -> list[str]`

Recursively discovers page URLs by following `<a href>` links starting from `base_url`.

**Input**: `base_url` — root URL to start from
**Output**: Deduplicated list of same-domain page URLs (strings)
**Filters**: Excludes asset paths (`/static/`, `/assets/`), fragment-only links, non-HTML files (`.js`, `.css`, `.json`, `.png`, `.svg`, etc.)
**Invariant**: Never visits a URL more than once
**Side effects**: Multiple HTTP GET requests (one per discovered page)

---

### `fetch_page(url: str) -> Page | None`

Fetches a single URL and returns a `Page` with cleaned text.

**Input**: `url` — absolute page URL
**Output**: `Page` dataclass if fetch succeeds (2xx) and cleaned text is non-empty; `None` otherwise
**On error**: Logs URL + error message, returns `None` — caller continues to next page
**Side effects**: One HTTP GET request, stdout log

---

### `clean_html(html: str, url: str) -> tuple[str, str]`

Extracts the page title and clean readable text from raw HTML.

**Inputs**: `html` — raw HTML string; `url` — source URL (for logging only)
**Output**: `(title, clean_text)` — both strings; `title` is from `<title>` tag or first `<h1>`; `clean_text` has tags, nav, footer, scripts stripped
**Idempotent**: Pure function — no side effects

---

### `chunk_text(page: Page, chunk_size: int, overlap: int, min_chars: int) -> list[Chunk]`

Splits page text into overlapping fixed-size character chunks with sentence-boundary snapping.

**Inputs**: `page` — `Page` dataclass; `chunk_size`, `overlap`, `min_chars` — integers from config
**Output**: List of `Chunk` dataclasses; empty list if page text is shorter than `min_chars`
**Invariant**: All returned chunks have `char_count >= min_chars`
**Idempotent**: Pure function — no side effects

---

### `embed_chunks(chunks: list[Chunk], co: cohere.ClientV2, model: str, batch_size: int) -> list[EmbeddedChunk]`

Sends chunks to Cohere in batches and returns embedded chunks.

**Inputs**: `chunks` — list of `Chunk`; `co` — Cohere client; `model` — model name; `batch_size` — max texts per call
**Output**: List of `EmbeddedChunk`, same length and order as input
**Error behaviour**: Raises `cohere.CohereAPIError` on API failure — pipeline halts (re-run is safe due to upsert)
**Side effects**: Cohere API calls (ceil(len(chunks)/batch_size) calls); stdout progress bar

---

### `init_qdrant(cfg: Config) -> QdrantClient`

Creates a Qdrant client and ensures the collection exists with correct parameters.

**Input**: `cfg` — `Config` dataclass
**Output**: Authenticated `QdrantClient` instance
**Behaviour**: Creates collection if it does not exist; does NOT delete existing data if collection exists
**Error behaviour**: Raises `qdrant_client.http.exceptions.UnexpectedResponse` on connection/auth failure
**Side effects**: One Qdrant API call to check/create collection

---

### `store_embeddings(embedded_chunks: list[EmbeddedChunk], client: QdrantClient, collection_name: str) -> int`

Upserts all embedded chunks as Qdrant points.

**Inputs**: `embedded_chunks` — list; `client` — Qdrant client; `collection_name` — string
**Output**: Count of points upserted (int)
**Idempotency**: Uses deterministic UUID5 point IDs — safe to re-run; existing points are overwritten
**Error behaviour**: Raises on Qdrant write failure — pipeline halts
**Side effects**: Qdrant API upsert calls; stdout progress bar

---

### `test_retrieval(queries: list[str], client: QdrantClient, co: cohere.ClientV2, cfg: Config) -> None`

Embeds each query and prints the top-3 retrieval results to stdout.

**Inputs**: `queries` — list of natural-language test strings; `client`, `co`, `cfg` — pipeline resources
**Output**: None (stdout only)
**Purpose**: Validation step — confirms end-to-end pipeline correctness
**Side effects**: Cohere API calls (1 per query) + Qdrant search calls; stdout print

---

### `main() -> None`

Orchestrates all pipeline stages end-to-end with logging.

**Sequence**:
1. `load_config()` → `cfg`
2. `fetch_sitemap(cfg.base_url)` → URLs (or `crawl_links` fallback)
3. `fetch_page(url)` for each URL → `pages`
4. `chunk_text(page, ...)` for each page → `chunks`
5. `embed_chunks(chunks, ...)` → `embedded_chunks`
6. `init_qdrant(cfg)` → `client`
7. `store_embeddings(embedded_chunks, client, ...)` → count
8. `test_retrieval([...], client, co, cfg)`
9. Print completion summary (total pages, chunks, vectors stored)

**Exit codes**: `0` on success; `1` on config error; non-zero on unhandled exception
**Side effects**: All network I/O, all stdout logging

---

## `.env.example` Contract

The file `backend/.env.example` MUST document every variable in this table:

```
# Required
BASE_URL=https://hackathon-book-uogx.vercel.app/
COHERE_API_KEY=your-cohere-api-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Optional (defaults shown)
COLLECTION_NAME=book-embeddings
COHERE_MODEL=embed-english-v3.0
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBED_BATCH_SIZE=96
MIN_CHUNK_CHARS=100
```
