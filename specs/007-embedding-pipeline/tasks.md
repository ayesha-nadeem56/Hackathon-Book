---
description: "Task list for Book Content Embedding Pipeline"
---

# Tasks: Book Content Embedding Pipeline

**Input**: Design documents from `/specs/007-embedding-pipeline/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅ | quickstart.md ✅

**Tests**: Not requested in spec — no test tasks generated.

**Organization**: Tasks grouped by user story. All pipeline code lives in `backend/main.py`. Files in other locations (`.env.example`, `pyproject.toml`, `.gitignore`) are marked `[P]` where independent of `main.py` work.

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: Can be done in any order relative to other `[P]`-marked tasks in the same phase (different files or logically independent)
- **[Story]**: Maps to user story from spec.md

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create the `backend/` project structure, initialize `uv`, and wire up configuration files.

- [x] T001 Create `backend/` directory at repo root and run `uv init --no-workspace` inside it to generate `pyproject.toml` and `uv.lock`
- [x] T00X Add all runtime dependencies via `uv add httpx beautifulsoup4 lxml cohere qdrant-client python-dotenv tqdm` from inside `backend/`
- [x] T00X [P] Create `backend/.env.example` with all 10 config keys (4 required, 6 optional with defaults) per contract in `specs/007-embedding-pipeline/contracts/ingestion-pipeline.md`
- [x] T00X [P] Add `backend/.env` to the root `.gitignore` (or create `backend/.gitignore` containing `.env`)
- [x] T00X Create `backend/main.py` with module-level docstring, import block (`os`, `uuid`, `xml.etree`, `dataclasses`, `datetime`, `httpx`, `bs4`, `cohere`, `qdrant_client`, `dotenv`, `tqdm`), and section comments for each pipeline stage

**Checkpoint**: `uv run python main.py` should import without error (empty `main()` stub is fine)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core dataclasses and configuration loader that every pipeline stage depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T00X Implement all four dataclasses (`Config`, `Page`, `Chunk`, `EmbeddedChunk`) in `backend/main.py` per `specs/007-embedding-pipeline/data-model.md` — include the `point_id` property on `Chunk` using `uuid.uuid5(uuid.NAMESPACE_URL, f"{self.page_url}#{self.chunk_index}")`
- [x] T00X Implement `load_config() -> Config` in `backend/main.py` — call `load_dotenv()`, read all 10 env vars, raise `ValueError` with a clear message for each missing required field (`BASE_URL`, `COHERE_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`), cast optional int fields (`CHUNK_SIZE`, `CHUNK_OVERLAP`, `EMBED_BATCH_SIZE`, `MIN_CHUNK_CHARS`) with `int(os.getenv(..., default))`
- [x] T00X Add a `log(stage: str, msg: str) -> None` helper in `backend/main.py` that prints `[STAGE]  msg` to stdout — used by all pipeline stages for consistent progress output

**Checkpoint**: `load_config()` should raise `ValueError` when env vars are missing, and return a valid `Config` when all required vars are set

---

## Phase 3: User Story 1 — Ingest Full Book into Retrievable Store (Priority: P1) 🎯 MVP

**Goal**: Crawl all public pages, clean and chunk text, generate embeddings, and store in Qdrant — end-to-end via `main()`.

**Independent Test**: Set all 4 required env vars, run `uv run python main.py`, confirm Qdrant collection has points and stdout shows page/chunk/vector counts.

- [x] T00X [P] [US1] Implement `fetch_sitemap(base_url: str) -> list[str]` in `backend/main.py` — GET `{base_url}/sitemap.xml`, parse `<loc>` tags with `xml.etree.ElementTree`, filter to same-domain URLs only (matching `base_url` scheme+host), return deduplicated list; return `[]` on any failure (non-200, parse error, timeout)
- [x] T010 [P] [US1] Implement `crawl_links(base_url: str) -> list[str]` in `backend/main.py` — recursively discover URLs via `<a href>` with `httpx` + `BeautifulSoup`; keep same-domain links only; exclude paths ending in `.js`, `.css`, `.json`, `.png`, `.svg`, `.ico`, `/static/`, `/assets/`; use a `visited: set[str]` to prevent re-visiting; return deduplicated list
- [x] T011 [US1] Implement `fetch_page(url: str) -> Page | None` in `backend/main.py` — `httpx.get(url, follow_redirects=True, timeout=15)`; if status != 2xx log and return `None`; call `clean_html(response.text, url)` and build `Page(url, title, text, status_code, datetime.utcnow())`; return `None` if cleaned text is empty
- [x] T012 [US1] Implement `clean_html(html: str, url: str) -> tuple[str, str]` in `backend/main.py` — parse with `BeautifulSoup(html, "lxml")`; extract title from `<title>` tag or first `<h1>`, fallback to URL; remove tags: `nav`, `footer`, `header`, `script`, `style`, `[class*="navbar"]`, `[class*="sidebar"]`, `[class*="pagination"]`, `[aria-label="breadcrumb"]`; call `.get_text(separator=" ", strip=True)` on the remaining `<article>` or `<main>` or `<body>`; return `(title, clean_text)`
- [x] T013 [US1] Implement `chunk_text(page: Page, chunk_size: int, overlap: int, min_chars: int) -> list[Chunk]` in `backend/main.py` — sliding window over `page.text`; at each candidate split point (`start + chunk_size`), walk back up to 100 chars to find nearest `.`, `!`, `?`, or `\n`; if found snap there, else use hard cut; next window starts at `split_point - overlap`; discard chunks where `len(text) < min_chars`; return list of `Chunk` dataclasses with `chunk_index` set to 0-based position
- [x] T014 [US1] Implement `embed_chunks(chunks: list[Chunk], co: cohere.ClientV2, model: str, batch_size: int) -> list[EmbeddedChunk]` in `backend/main.py` — split chunks into batches of `batch_size`; call `co.embed(texts=[c.text for c in batch], model=model, input_type="search_document")`; collect `response.embeddings`; wrap each in `EmbeddedChunk(chunk=c, vector=v)`; show progress with `tqdm`; preserve input order in output
- [x] T015 [US1] Implement `init_qdrant(cfg: Config) -> QdrantClient` in `backend/main.py` — create `QdrantClient(url=cfg.qdrant_url, api_key=cfg.qdrant_api_key)`; check if collection exists with `client.collection_exists(cfg.collection_name)`; if not, call `client.create_collection(collection_name=cfg.collection_name, vectors_config=VectorParams(size=1024, distance=Distance.COSINE))`; log result; return client
- [x] T016 [US1] Implement `store_embeddings(embedded_chunks: list[EmbeddedChunk], client: QdrantClient, collection_name: str) -> int` in `backend/main.py` — build `PointStruct` list with `id=ec.chunk.point_id`, `vector=ec.vector`, `payload={"url": ..., "title": ..., "chunk_index": ..., "text": ..., "char_count": ...}`; call `client.upsert(collection_name=collection_name, points=points)` in batches of 100; show `tqdm` progress; return total count upserted
- [x] T017 [US1] Implement `main() -> None` in `backend/main.py` — call `load_config()`; call `fetch_sitemap(cfg.base_url)` and fall back to `crawl_links(cfg.base_url)` if result is empty; log URL count; loop URLs calling `fetch_page()`, collect non-None `Page` objects; loop pages calling `chunk_text()`, flatten all `Chunk` lists; call `embed_chunks()`; call `init_qdrant()` then `store_embeddings()`; print final summary line `[DONE]  {n_pages} pages | {n_chunks} chunks | {n_stored} vectors stored`; add `if __name__ == "__main__": main()` guard at module bottom

**Checkpoint**: `uv run python main.py` with valid `.env` completes without error, Qdrant collection has nonzero point count matching stdout output

---

## Phase 4: User Story 2 — Verify Retrieval Quality via Test Queries (Priority: P2)

**Goal**: After ingestion, embed sample queries and print top-3 results per query to confirm semantic retrieval works end-to-end.

**Independent Test**: With Qdrant collection populated, run `uv run python main.py` and confirm 3 query result blocks appear at the end of stdout, each showing a URL and snippet from the correct topic area.

**Depends on**: Phase 3 complete (US1 must be ingested for retrieval to have data)

- [x] T018 [US2] Implement `test_retrieval(queries: list[str], client: QdrantClient, co: cohere.ClientV2, cfg: Config) -> None` in `backend/main.py` — for each query: call `co.embed(texts=[query], model=cfg.cohere_model, input_type="search_query")`; call `client.search(collection_name=cfg.collection_name, query_vector=vector, limit=3, with_payload=True)`; print `[VERIFY] Query: "{query}"`; for each result print `  {rank}. (score={r.score:.2f}) {r.payload["url"]}\n     "{r.payload["text"][:120]}..."`
- [x] T019 [US2] Add `test_retrieval()` call at the end of `main()` in `backend/main.py` with 3 domain-relevant sample queries: `"What is ROS 2 and how does it work?"`, `"How does a digital twin model a physical system?"`, `"What is a Vision-Language-Action model?"` — these cover the three main book modules

**Checkpoint**: Running `uv run python main.py` after a successful ingestion shows 3 formatted query result blocks with nonzero scores and relevant snippets

---

## Phase 5: User Story 3 — Configure Pipeline Without Code Changes (Priority: P3)

**Goal**: All 10 pipeline parameters are driveable from `.env` / environment variables — no code edits needed to retarget the pipeline.

**Independent Test**: Change `BASE_URL` in `.env` to a different URL and re-run — confirm pipeline targets the new URL without touching `main.py`. Change `COLLECTION_NAME` — confirm new collection is created in Qdrant.

**Depends on**: Phase 2 complete (`load_config()` must exist)

- [x] T020 [P] [US3] Verify `backend/.env.example` has all 10 variables defined with inline comments explaining each — required vs optional, expected format, and the default value for all optional keys (matches contract in `specs/007-embedding-pipeline/contracts/ingestion-pipeline.md`)
- [x] T021 [US3] Harden `load_config()` in `backend/main.py` — add explicit `ValueError` for any optional int field that is set but non-numeric (e.g., `CHUNK_SIZE=abc` should fail with a clear message rather than a cryptic `int()` traceback); strip whitespace from all string env var values before use

**Checkpoint**: Setting `COLLECTION_NAME=test-collection` in `.env` and running `uv run python main.py` creates a new Qdrant collection with that name; changing `CHUNK_SIZE=500` produces roughly double the chunk count vs default 1000

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge case robustness, output clarity, and developer experience.

- [x] T022 [P] Add redirect deduplication to `fetch_sitemap()` and `crawl_links()` in `backend/main.py` — after collecting all URLs, resolve any trailing-slash variants to a canonical form (strip trailing `/` or consistently add it based on `BASE_URL` pattern) to prevent duplicate pages from being ingested twice
- [x] T023 Add graceful timeout handling to `fetch_page()` in `backend/main.py` — catch `httpx.TimeoutException` and `httpx.ConnectError` separately, log the specific error type and URL, return `None` and continue
- [x] T024 [P] Validate `backend/quickstart.md` against the actual project by running each command block (`uv init`, `uv add`, `uv run python main.py`) and confirming expected output format matches — update any discrepancies in `specs/007-embedding-pipeline/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — BLOCKS all user story work
- **Phase 3 (US1 — Ingest)**: Depends on Phase 2 — core pipeline, must complete before US2
- **Phase 4 (US2 — Verify)**: Depends on Phase 3 — retrieval requires ingested data
- **Phase 5 (US3 — Config)**: Depends on Phase 2 — `load_config()` must exist; can start after Phase 2 in parallel with Phase 3
- **Phase 6 (Polish)**: Depends on Phases 3–5 being complete

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|-----------|----------------------|
| US1 (Ingest) | Phase 2 complete | US3 (after Phase 2) |
| US2 (Verify) | US1 complete (needs data in Qdrant) | None — sequential after US1 |
| US3 (Configure) | Phase 2 complete | US1 (different aspects of `main.py`) |

### Within Each Phase

- `fetch_sitemap` (T009) and `crawl_links` (T010) are logically independent — implement in either order
- `init_qdrant` (T015) is independent of chunking/embedding — can be implemented any time after Phase 2
- All Phase 5 tasks can be interleaved with Phase 3 since they modify `load_config()` (already written) not the stage functions

### Parallel Opportunities

```
Phase 1:
  T003 (.env.example) ──┐
  T004 (.gitignore)   ──┤  parallel with each other
  T001 + T002 + T005  ──┘  sequential (uv init first)

Phase 3 (US1):
  T009 (fetch_sitemap) ──┐
  T010 (crawl_links)   ──┤  parallel (logically independent functions)
  T015 (init_qdrant)   ──┘  parallel (no dependency on crawl)
  T011 → T012 → T013 → T014 → T016 → T017  (sequential pipeline chain)

Phase 5 (US3):
  T020 (.env.example verify) ──┐  parallel
  T021 (load_config hardening) ──┘
```

---

## Implementation Strategy

### MVP (User Story 1 Only) — Minimum Viable Pipeline

1. Complete **Phase 1** (Setup) — T001–T005
2. Complete **Phase 2** (Foundational) — T006–T008
3. Complete **Phase 3** (US1) — T009–T017
4. **STOP and VALIDATE**: `uv run python main.py` — confirm vectors in Qdrant
5. This delivers a fully working ingestion pipeline

### Incremental Delivery

1. Phase 1 + Phase 2 → Project structure ready
2. Phase 3 (US1) → Full ingestion pipeline working (**MVP**)
3. Phase 4 (US2) → Retrieval verification added
4. Phase 5 (US3) → Config hardened and validated
5. Phase 6 (Polish) → Production-ready edge cases

### Suggested Task Execution for Single Developer

```
T001 → T002 → T005 → [T003, T004] → T006 → T007 → T008
→ [T009, T010, T015] → T011 → T012 → T013 → T014 → T016 → T017
→ T018 → T019
→ [T020, T021]
→ [T022, T023, T024]
```

---

## Task Summary

| Phase | Tasks | User Story | Parallelizable |
|-------|-------|------------|----------------|
| Phase 1: Setup | T001–T005 | — | T003, T004 |
| Phase 2: Foundational | T006–T008 | — | None |
| Phase 3: US1 Ingest | T009–T017 | US1 | T009, T010, T015 |
| Phase 4: US2 Verify | T018–T019 | US2 | None |
| Phase 5: US3 Config | T020–T021 | US3 | T020 |
| Phase 6: Polish | T022–T024 | — | T022, T024 |
| **Total** | **24 tasks** | | **8 parallelizable** |

---

## Notes

- All implementation tasks target `backend/main.py` (single file per plan)
- `[P]` marks tasks safe to do in any order relative to other `[P]` tasks in the same phase
- `[US1]`, `[US2]`, `[US3]` map to user stories in `specs/007-embedding-pipeline/spec.md`
- Re-running `main()` is idempotent — UUID5 point IDs guarantee upsert safety
- Commit after each checkpoint (after Phase 2, Phase 3, Phase 4, Phase 5)
- US1 checkpoint is the MVP delivery gate
