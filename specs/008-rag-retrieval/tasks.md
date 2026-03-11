# Tasks: RAG Retrieval Validation Pipeline

**Input**: Design documents from `/specs/008-rag-retrieval/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/retrieval-cli.md ✅, quickstart.md ✅
**Target file**: `backend/retrieve.py` (single-file script)

**Tests**: Not requested — no test tasks generated.

**Organization**: Tasks grouped by user story to enable independent verification of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks in same story)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Script Skeleton)

**Purpose**: Create the file and establish shared infrastructure used by all phases.

- [x] T001 Create `backend/retrieve.py` — UTF-8 stdout fix (`sys.stdout.reconfigure` if needed), all imports (`cohere`, `qdrant_client`, `dotenv`, `sys`, `os`), and `DEFAULT_QUERIES` list of 5 known book topics

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Config loading and Qdrant connection — MUST be complete before any user story.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T002 Implement `load_config()` in `backend/retrieve.py` — calls `load_dotenv()`, reads `QDRANT_URL`, `QDRANT_API_KEY`, `COLLECTION_NAME`, `COHERE_API_KEY` (all required), reads `COHERE_MODEL` (default `embed-english-v3.0`), returns config dict; raises `SystemExit(1)` with `ERROR:` message for any missing required key
- [x] T003 Implement `init_qdrant(config)` in `backend/retrieve.py` — creates `QdrantClient(url, api_key)`, calls `client.get_collection(collection_name)` to verify it exists (`SystemExit(2)` on failure), checks `points_count > 0` (`SystemExit(3)` if empty), returns client

**Checkpoint**: Config validated and Qdrant connection verified — user story implementation can begin.

---

## Phase 3: User Story 1 — Query and Retrieve Top-K Chunks (Priority: P1) 🎯 MVP

**Goal**: Embed a natural-language query and retrieve the top-K most similar chunks from Qdrant, printing rank, score, URL, and text snippet.

**Independent Test**: Run `uv run python retrieve.py` from `backend/`. Confirm 5 queries × 3 results each are printed, each with a score, URL, and text snippet. At least one result per known-topic query must have score > 0.5.

### Implementation for User Story 1

- [x] T004 [US1] Implement `embed_query(text, config)` in `backend/retrieve.py` — creates `cohere.ClientV2(api_key)`, calls `.embed(texts=[text], model=cohere_model, input_type="search_query", embedding_types=["float"])`, returns `response.embeddings.float[0]` (list of 1024 floats)
- [x] T005 [US1] Implement `retrieve(client, query_vector, config)` in `backend/retrieve.py` — calls `client.query_points(collection_name=collection_name, query=query_vector, limit=top_k, with_payload=True)`, returns `.points` list of `ScoredPoint` objects
- [x] T006 [US1] Implement `print_results(query_text, results)` in `backend/retrieve.py` — prints separator line, query string, then for each result: rank (#N), score (2 d.p.), source URL, title, chunk_index, text snippet (first 150 chars)
- [x] T007 [US1] Implement `main()` skeleton in `backend/retrieve.py` — calls `load_config()` and `init_qdrant(config)`, determines query list from `sys.argv[1:]` or `DEFAULT_QUERIES`, loops through each query calling `embed_query → retrieve → print_results`, exits `sys.exit(0)` after all queries complete

**Checkpoint**: US1 fully functional — run with default queries to see 15 results with scores, URLs, and snippets.

---

## Phase 4: User Story 2 — Validate Metadata Integrity (Priority: P2)

**Goal**: Inspect every retrieved result's payload and confirm all required fields (url, title, chunk_index, text) are present and non-empty; print a ValidationReport summary.

**Independent Test**: Run `uv run python retrieve.py` from `backend/`. After results, confirm a `Validation Report` block prints showing `Metadata valid: N / N` and `Overall: PASS`. If any field is missing, a `WARNING:` line must appear.

### Implementation for User Story 2

- [x] T008 [US2] Implement `validate_payload(result, rank, query_text)` in `backend/retrieve.py` — checks `result.payload` for keys `url`, `title`, `chunk_index`, `text`; verifies each is non-empty; prints `WARNING: Result #<rank> ...` for any missing or empty field; returns `(is_valid: bool, missing: list[str])`
- [x] T009 [US2] Integrate `validate_payload()` into the query loop in `main()` in `backend/retrieve.py` — call after `retrieve()` for each result; accumulate `total_results`, `valid_count`, `invalid_count` counters across all queries
- [x] T010 [US2] Add `print_validation_report(query_count, total_results, valid_count, invalid_count)` to `backend/retrieve.py` — prints separator, `Validation Report` header, query/result/valid/invalid counts, and `Overall: PASS` or `Overall: FAIL`; call from `main()` after all queries

**Checkpoint**: US1 + US2 fully functional — validation report confirms metadata integrity across all retrieved results.

---

## Phase 5: User Story 3 — Configurable TOP_K and SCORE_THRESHOLD (Priority: P3)

**Goal**: Developers can override the number of results per query (TOP_K) and filter by minimum similarity score (SCORE_THRESHOLD) via environment variables without changing code.

**Independent Test**: Run `TOP_K=1 SCORE_THRESHOLD=0.6 uv run python retrieve.py "What is RAG?"` from `backend/`. Confirm exactly 1 result is returned and its score ≥ 0.60.

### Implementation for User Story 3

- [x] T011 [US3] Add `TOP_K` and `SCORE_THRESHOLD` parsing to `load_config()` in `backend/retrieve.py` — `int(os.getenv("TOP_K", "3"))` for top_k (must be ≥ 1, else `SystemExit(1)`); `float(os.getenv("SCORE_THRESHOLD"))` if set else `None` for score_threshold; store both in returned config dict
- [x] T012 [US3] Pass `score_threshold` and `top_k` from config into `retrieve()` in `backend/retrieve.py` — use `config["top_k"]` as `limit` and `config["score_threshold"]` as `score_threshold` parameter in `client.query_points()` call (replaces hardcoded values from T005)

**Checkpoint**: All 3 user stories functional — TOP_K and SCORE_THRESHOLD override via env vars works end-to-end.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Error resilience and final validation.

- [x] T013 Add Cohere API error handling to `embed_query()` in `backend/retrieve.py` — wrap `co.embed()` in try/except, print `ERROR: Cohere API call failed: <message>` and `raise` to propagate; ensures readable failure message instead of raw stack trace
- [x] T014 Run end-to-end validation per `specs/008-rag-retrieval/quickstart.md` — execute all 5 steps, confirm `Overall: PASS` in validation report, confirm exit code 0, confirm TOP_K/SCORE_THRESHOLD override works

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on T001 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on T002 + T003; T004/T005/T006 can be implemented in parallel, T007 depends on all three
- **US2 (Phase 4)**: Depends on Phase 3 completion (T007 must exist for integration); T008/T009/T010 sequential within phase
- **US3 (Phase 5)**: T011 modifies `load_config()` (extends T002), T012 modifies `retrieve()` (extends T005) — both can be done after Phase 3
- **Polish (Phase 6)**: Depends on all story phases complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependency on US2/US3
- **US2 (P2)**: After US1 (integrates into main() loop built in T007)
- **US3 (P3)**: After Foundational (modifies load_config + retrieve which are built in T002/T005)

### Parallel Opportunities

- T004, T005, T006 within Phase 3 — all implement different functions in same file, no inter-dependency
- T011, T012 within Phase 5 — modify different functions (load_config vs retrieve), can be done in parallel

---

## Parallel Example: User Story 1

```bash
# These 3 functions have no dependency on each other — write all 3 before wiring in T007:
Task T004: "Implement embed_query() in backend/retrieve.py"
Task T005: "Implement retrieve() in backend/retrieve.py"
Task T006: "Implement print_results() in backend/retrieve.py"

# After T004/T005/T006 complete:
Task T007: "Implement main() skeleton — wires all three together"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: T001 — create file
2. Complete Phase 2: T002, T003 — config + Qdrant connection
3. Complete Phase 3: T004, T005, T006, T007 — embed + retrieve + print
4. **STOP and VALIDATE**: `uv run python retrieve.py` returns results with scores > 0.5
5. This is a complete, runnable script

### Incremental Delivery

1. T001–T003 → script connects to Qdrant without error
2. T004–T007 → US1 complete: queries return ranked results with scores
3. T008–T010 → US2 complete: validation report shows metadata integrity
4. T011–T012 → US3 complete: env vars control top_k and score filtering
5. T013–T014 → polish: error handling + end-to-end verification

---

## Notes

- All tasks modify the single file `backend/retrieve.py`
- [P] marks tasks that implement independent functions with no inter-dependency
- US3 extends functions already written in Phase 2/3 — treated as modifications to existing stubs
- No new dependencies needed — `cohere`, `qdrant-client`, `python-dotenv` already in `backend/pyproject.toml`
- Run all tasks from within `backend/` using `uv run python retrieve.py`
