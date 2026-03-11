# Tasks: FastAPI RAG Integration — Backend-Frontend Bridge

**Input**: Design documents from `/specs/010-fastapi-rag-integration/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/openapi.yaml ✅ | quickstart.md ✅

**Tests**: Not explicitly requested — no test tasks generated.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add FastAPI dependency and create the `api.py` skeleton so the project compiles before any endpoint logic is written.

- [x] T001 Add `fastapi` and `"uvicorn[standard]"` to `backend/pyproject.toml` dependencies (run `uv add fastapi "uvicorn[standard]"` from `backend/`)
- [x] T002 Create `backend/api.py` with: UTF-8 stdout fix, `sys.path` insertion for project root (`pathlib.Path(__file__).parent.parent`), and imports of `load_config`, `init_qdrant`, `build_agent` from `agent`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core FastAPI infrastructure that MUST be complete before any user story endpoint can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Implement `lifespan()` async context manager in `backend/api.py` — call `load_config()`, `init_qdrant(cfg)`, `build_agent(cfg, client)` at startup; store `cfg`, `agent`, `run_config`, and `qdrant_client` in `app.state`; call `qdrant_client.close()` on shutdown
- [x] T004 Instantiate `FastAPI(lifespan=lifespan)` in `backend/api.py` and add `CORSMiddleware` allowing origins `["http://localhost:3000", "https://hackathon-book-uogx.vercel.app"]`, methods `["GET", "POST"]`, headers `["Content-Type"]`
- [x] T005 [P] Define Pydantic models in `backend/api.py`: `QueryRequest(query: str)`, `SourceReference(url: str, title: str = "")`, `QueryResponse(answer: str, sources: list[SourceReference])`, `ErrorResponse(error: str)`, `HealthStatus(status: str, dependencies: dict[str, str])`
- [x] T006 [P] Add `run_once(agent, run_config, query: str)` async function to `agent.py` — single `await Runner.run(agent, query, run_config=run_config)` and return result; place after `build_agent()` definition

**Checkpoint**: `uv run uvicorn api:app --reload` starts without errors; `GET /docs` loads FastAPI Swagger UI.

---

## Phase 3: User Story 1 — Developer Queries the RAG Agent via HTTP (Priority: P1) 🎯 MVP

**Goal**: A working `POST /query` endpoint that accepts a JSON question, calls the RAG agent, and returns a grounded answer with source citations as JSON.

**Independent Test**: `curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query":"What is ROS 2?"}' ` returns HTTP 200 with `{"answer": "...", "sources": [...]}`.

### Implementation for User Story 1

- [x] T007 [US1] Implement `parse_sources(result) -> list[SourceReference]` helper in `backend/api.py` — iterate `result.to_input_list()`, find messages with `role == "tool"`, parse lines matching `"URL: <value>"` and `"Title: <value>"` from the content string, return deduplicated `SourceReference` list
- [x] T008 [US1] Implement `POST /query` endpoint in `backend/api.py` — accept `QueryRequest`, validate `query` is non-empty and ≤ 2000 chars (raise `HTTPException(400)` on failure), call `asyncio.wait_for(run_once(app.state.agent, app.state.run_config, req.query), timeout=30.0)`, extract `result.final_output` as `answer`, call `parse_sources(result)` for sources, return `QueryResponse`
- [x] T009 [US1] Add structured error handling to `POST /query` in `backend/api.py` — catch `asyncio.TimeoutError` → `JSONResponse({"error": "Agent response timed out. Please try again."}, status_code=504)`; catch all other `Exception` → `JSONResponse({"error": "Retrieval service unavailable. Please try again shortly."}, status_code=503)`

**Checkpoint**: Server running — `curl -X POST http://localhost:8000/query -d '{"query":"What is ROS 2?"}'` returns HTTP 200 with non-empty `answer` and a `sources` array. Empty query returns HTTP 400. Agent is grounded (answer cites book content).

---

## Phase 4: User Story 2 — Frontend Sends a Query and Displays the Response (Priority: P2)

**Goal**: A floating chat widget visible on every Docusaurus page that sends user questions to `POST /query` and renders the answer and source links.

**Independent Test**: `cd book && npm run start`, navigate to any docs page, click the chat button, type a question, confirm: loading indicator appears, answer renders, source links appear with clickable URLs. An empty submit shows a validation message.

### Implementation for User Story 2

- [x] T010 [P] [US2] Create `book/src/theme/Root.js` — default export `Root({ children })` that renders `<>{children}<ChatWidget /></>`, importing `ChatWidget` from `@site/src/components/ChatWidget`
- [x] T011 [P] [US2] Create `book/src/components/ChatWidget/styles.module.css` — styles for: `.chatContainer` (fixed bottom-right, z-index 1000), `.toggleButton` (56×56 px circle, background `#2563eb`, white emoji), `.chatPanel` (400×520 px absolute box, white background, shadow, rounded, bottom 70px right 0), `.messages` (flex-grow, overflow-y scroll, padding 12px), `.message` (margin-bottom 8px, border-radius 6px), `.messageUser` (background `#eff6ff`, text-align right), `.messageAssistant` (background `#f9fafb`), `.sources` (font-size 12px, margin-top 6px), `.sources a` (display block, color `#2563eb`), `.inputRow` (padding 10px, display flex, gap 8px), `.inputRow input` (flex 1, border 1px solid `#d1d5db`, border-radius 4px, padding 8px), `.sendBtn` (background `#2563eb`, color white, border none, border-radius 4px, padding 8px 16px, cursor pointer), `.sendBtn:disabled` (opacity 0.5, cursor not-allowed), `.loading` (color `#6b7280`, font-style italic, padding 8px 12px)
- [x] T012 [US2] Create `book/src/components/ChatWidget/index.js` — React functional component using `useState` for `isOpen`, `messages` (array of `{role, text, sources?}`), `inputValue`, `isLoading`; `handleSubmit` validates non-empty `inputValue` (shows validation message if empty), appends user message, sets `isLoading = true`, POSTs `{"query": inputValue}` to `http://localhost:8000/query` with `Content-Type: application/json`, on success appends `{role: "assistant", text: data.answer, sources: data.sources}`, on error appends `{role: "error", text: "Failed to get a response. Please try again."}`, always sets `isLoading = false`; render: fixed container with toggle button, conditional chat panel with scrollable messages list and form input
- [x] T013 [US2] Add source rendering to `ChatWidget` in `book/src/components/ChatWidget/index.js` — for each assistant message, render `sources` array as `<div className={styles.sources}>` containing `<a href={src.url} target="_blank" rel="noopener noreferrer">{src.title || src.url}</a>` for each source; only render the sources block when `sources` array is non-empty

**Checkpoint**: Docusaurus dev server running alongside FastAPI server — floating chat button visible on home page AND all `/docs/*` pages; full question → answer → sources flow works in browser without console errors.

---

## Phase 5: User Story 3 — Health Check Confirms Service Readiness (Priority: P3)

**Goal**: A `GET /health` endpoint that reports the live status of Qdrant and the agent, for CI and frontend graceful degradation.

**Independent Test**: `curl http://localhost:8000/health` returns HTTP 200 `{"status":"ok","dependencies":{"qdrant":"ok","agent":"ok"}}` when server is healthy. Stopping Qdrant or unsetting credentials causes a non-200 response with `"qdrant":"unreachable"`.

### Implementation for User Story 3

- [x] T014 [US3] Implement `GET /health` endpoint in `backend/api.py` — try `app.state.qdrant_client.get_collections()` (1-second timeout via `asyncio.wait_for` wrapping a `asyncio.to_thread` call); set `qdrant_status = "ok"` on success or `"unreachable"` on exception; set `agent_status = "ok"` if `app.state.agent is not None` else `"not_initialized"`; derive `overall = "ok"` if both are `"ok"` else `"degraded"`; return `JSONResponse(HealthStatus(...), status_code=200 if overall == "ok" else 503)`

**Checkpoint**: `curl http://localhost:8000/health` returns `{"status":"ok",...}` with both dependencies healthy.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Env documentation, startup message, and final end-to-end validation.

- [x] T015 [P] Add startup log message to `lifespan()` in `backend/api.py` — after agent is initialized, print `"[API] BookAgent ready. POST /query to ask questions."` so operator knows the server is fully started
- [x] T016 [P] Update `backend/.env.example` — add `API_PORT=8000` and `ALLOWED_ORIGINS=http://localhost:3000,https://hackathon-book-uogx.vercel.app` with comments explaining each
- [ ] T017 Manual end-to-end walkthrough per `specs/010-fastapi-rag-integration/quickstart.md` — complete all 6 steps; confirm 3 distinct questions return grounded answers with sources in the browser chat widget; confirm empty submit is blocked; confirm health endpoint returns ok

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Foundational (Phase 2) — T007 → T008 → T009 in sequence
- **US2 (Phase 4)**: Depends on Foundational (Phase 2); US1 server must be running for browser test
- **US3 (Phase 5)**: Depends on Foundational (Phase 2); can run in parallel with US2
- **Polish (Phase 6)**: Depends on US1 + US2 + US3 complete

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2 only — no dependency on US2 or US3
- **US2 (P2)**: Depends on Phase 2; requires US1 server running for the browser integration test (but US2 implementation tasks are independent)
- **US3 (P3)**: Depends on Phase 2 only — fully independent of US1 and US2

### Within Each User Story

- US1: T007 (parse_sources helper) → T008 (endpoint body) → T009 (error handling)
- US2: T010 + T011 in parallel → T012 → T013
- US3: T014 single task

### Parallel Opportunities

- T005 and T006 (Phase 2) can run in parallel — different files
- T010 and T011 (US2 setup) can run in parallel — different files
- T015 and T016 (Polish) can run in parallel — different files
- US2 (Phase 4) and US3 (Phase 5) can proceed in parallel after Phase 2 completion

---

## Parallel Example: User Story 2

```text
# After Phase 2 is complete, launch in parallel:
Task T010: Create book/src/theme/Root.js (Root swizzle)
Task T011: Create book/src/components/ChatWidget/styles.module.css (CSS)

# After T010 + T011 complete, run sequentially:
Task T012: Create book/src/components/ChatWidget/index.js (component logic)
Task T013: Add source rendering to ChatWidget (extends T012)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only — Backend API)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T006) — CRITICAL gate
3. Complete Phase 3: US1 (T007–T009)
4. **STOP and VALIDATE**: `curl` the endpoint, confirm JSON response shape
5. Backend is independently useful — frontend is optional for MVP

### Incremental Delivery

1. Setup + Foundational → server compiles and starts (Swagger at `/docs`)
2. US1 (POST /query) → curl-testable backend ✅ MVP
3. US2 (ChatWidget) → browser-testable end-to-end ✅ Full integration
4. US3 (GET /health) → CI/monitoring ready ✅ Production-ready
5. Polish → documented and validated ✅ Complete

### Single Developer Sequence

```text
T001 → T002 → T003 → T004 → T005 (+ T006 parallel) → T007 → T008 → T009
→ T010 (+ T011 parallel) → T012 → T013 → T014 → T015 (+ T016 parallel) → T017
```

---

## Notes

- No test tasks generated — tests not explicitly requested in spec
- `[P]` tasks touch different files and have no unresolved dependencies on in-progress tasks
- Each user story phase ends with a concrete checkpoint that verifies the story works independently
- All secrets must remain in `backend/.env` — no hardcoded values in any source file
- Run `uv run uvicorn api:app --reload --port 8000` from `backend/` (not project root)
- Docusaurus `npm run start` must run from `book/` directory
