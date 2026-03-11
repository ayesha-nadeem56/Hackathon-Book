# Tasks: AI-Powered Book Q&A Agent

**Input**: Design documents from `/specs/009-rag-agent/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/agent-cli.md ✅, quickstart.md ✅
**Target file**: `agent.py` (project root)

**Tests**: Not requested — no test tasks generated.

**Organization**: Tasks grouped by user story to enable independent verification of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files or independent functions)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup (Dependency + Skeleton)

**Purpose**: Install the new dependency and create the file structure all phases share.

- [x] T001 Add `openai-agents` dependency — run `uv add openai-agents` from `backend/`; confirm `backend/pyproject.toml` gains `openai-agents` and `openai>=2.26.0`
- [x] T002 Create `agent.py` at project root — UTF-8 stdout fix (`sys.stdout.reconfigure` if needed), all imports (`agents`, `cohere`, `qdrant_client`, `dotenv`, `asyncio`, `os`, `sys`), docstring matching the module's purpose

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Config loading, Qdrant connection, and retrieval primitives — MUST be complete before any user story.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Implement `load_config()` in `agent.py` — calls `load_dotenv("backend/.env")`, validates 5 required keys (`OPENAI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `COLLECTION_NAME`, `COHERE_API_KEY`), reads optional `COHERE_MODEL` (default `embed-english-v3.0`) and `AGENT_MODEL` (default `gpt-4o`), exits `SystemExit(1)` with `ERROR:` message per missing key; returns config dict
- [x] T004 Implement `init_qdrant(config)` in `agent.py` — creates `QdrantClient(url, api_key)`, calls `get_collection()` to verify exists (exits 2 on failure), checks `points_count > 0` (exits 3 if empty), prints `[QDRANT] Connected` line, returns client
- [x] T005 [P] Implement `embed_query(text, config)` in `agent.py` — `cohere.ClientV2(api_key)`, `.embed(texts=[text], model, input_type="search_query", embedding_types=["float"])`, returns `response.embeddings.float_[0]` (list of 1024 floats)
- [x] T006 [P] Implement `retrieve_from_qdrant(client, query_vector, config)` in `agent.py` — `client.query_points(collection_name, query=query_vector, limit=config["top_k"], with_payload=True, score_threshold=config["score_threshold"]).points`; returns list of ScoredPoint objects

**Note**: T005 and T006 [P] can be written in parallel — they are independent functions.

**Checkpoint**: Config validated, Qdrant connected, retrieval primitives ready — user story implementation can begin.

---

## Phase 3: User Story 1 — Ask a Question, Receive a Grounded Answer (Priority: P1) 🎯 MVP

**Goal**: User types a question, agent calls the retrieval tool, returns a grounded answer with source URLs.

**Independent Test**: Run `cd backend && uv run python ../agent.py`. Ask "What is NVIDIA Isaac Sim?". Confirm the agent responds with content from the book and cites a source URL. Confirm no fabricated information appears.

### Implementation for User Story 1

- [x] T007 [US1] Implement `format_passages(results)` in `agent.py` — iterates ScoredPoint list, formats each as `[Passage N] score=X.XX\nTitle: ...\nURL: ...\nText: "..."`, returns formatted string; returns `"No relevant passages found in the book for this query."` when results list is empty
- [x] T008 [US1] Implement `@function_tool retrieve_book_content(query: str)` in `agent.py` — decorated with `@function_tool`, uses Google-style docstring with Args section; calls `embed_query(query, config)` → `retrieve_from_qdrant(client, vector, config)` → `format_passages(results)`, returns the formatted string; `config` and `client` captured via closure from outer scope
- [x] T009 [US1] Implement `build_agent(config)` in `agent.py` — creates `Agent(name="BookAgent", instructions=GROUNDING_PROMPT, model=config["agent_model"], tools=[retrieve_book_content])` where `GROUNDING_PROMPT` instructs: use the tool for every question, answer only from retrieved passages, say "I don't have relevant information" when no passages found, cite source URLs
- [x] T010 [US1] Implement `run_repl(agent)` basic version in `agent.py` — `async def run_repl(agent)`: prints `[AGENT]  BookAgent ready. Ask a question. Type 'quit' to exit.`; while-loop reads `input("\n> ")`, skips empty/whitespace with warning, breaks on `quit`/`exit`/`q`, calls `await Runner.run(agent, user_input)`, prints `result.final_output` (each turn stateless — no history yet)
- [x] T011 [US1] Implement `main()` in `agent.py` — calls `load_config()`, `init_qdrant(config)`, `build_agent(config)`, then `asyncio.run(run_repl(agent))`; add `if __name__ == "__main__": main()` guard

**Checkpoint**: US1 fully functional — agent answers grounded questions and refuses out-of-scope questions. Run to validate independently.

---

## Phase 4: User Story 2 — Follow-Up Questions in the Same Session (Priority: P2)

**Goal**: Agent maintains conversational context so follow-up questions (using pronouns, implicit references) work correctly without re-stating earlier context.

**Independent Test**: Start the agent. Ask "What is ROS2?" Then ask "How does it work with Isaac Sim?" without mentioning ROS2 again. Confirm the agent correctly interprets "it" as ROS2 from session history.

### Implementation for User Story 2

- [x] T012 [US2] Add multi-turn history management to `run_repl()` in `agent.py` — replace stateless `Runner.run(agent, user_input)` with history-based pattern: initialise `history = None` before loop; first turn: `result = await Runner.run(agent, user_input)`; subsequent turns: `history = result.to_input_list(); history.append({"role": "user", "content": user_input}); result = await Runner.run(agent, history)`

**Checkpoint**: US1 + US2 functional — follow-up questions work correctly without repeating context.

---

## Phase 5: User Story 3 — Configurable Retrieval Depth and Relevance Threshold (Priority: P3)

**Goal**: Developers can override TOP_K (number of passages) and SCORE_THRESHOLD (minimum relevance score) via environment variables without touching source code.

**Independent Test**: Run `TOP_K=1 SCORE_THRESHOLD=0.5 uv run python ../agent.py` from `backend/`. Ask a known-topic question. Confirm at most 1 passage is cited. Run without variables and confirm 3 passages return.

### Implementation for User Story 3

- [x] T013 [US3] Add `TOP_K` and `SCORE_THRESHOLD` parsing to `load_config()` in `agent.py` — `int(os.getenv("TOP_K", "3"))` with ≥1 validation (exits 1 if invalid); `float(os.getenv("SCORE_THRESHOLD"))` if set else `None` with [0.0, 1.0] range validation; add both to returned config dict
- [x] T014 [US3] Confirm `retrieve_from_qdrant()` in `agent.py` uses `config["top_k"]` as `limit` and `config["score_threshold"]` as `score_threshold` in `client.query_points()` — wire env var values end-to-end from load_config → retrieve_from_qdrant → query_points

**Checkpoint**: All 3 user stories functional — TOP_K and SCORE_THRESHOLD control retrieval depth from env vars.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Error resilience, clean exit, and final validation.

- [x] T015 Add `KeyboardInterrupt` handler to `run_repl()` in `agent.py` — wrap the REPL loop in `try/except KeyboardInterrupt`, print `\nGoodbye!` and `sys.exit(0)` on interrupt; also print `Goodbye!` and `sys.exit(0)` on normal `quit`/`exit` break
- [x] T016 Run end-to-end validation per `specs/009-rag-agent/quickstart.md` — execute all 8 steps: install dep, add API key, run agent, grounded Q&A, follow-up, out-of-scope refusal, configurable TOP_K, graceful exit

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on T001+T002 (Phase 1 complete); T005/T006 can run in parallel within Phase 2
- **US1 (Phase 3)**: Depends on T003–T006; T007/T008/T009 can be written in parallel, T010 depends on them, T011 depends on T010
- **US2 (Phase 4)**: Depends on T010+T011 (run_repl + main must exist before modifying run_repl)
- **US3 (Phase 5)**: Depends on T003 (extends load_config) and T006 (modifies retrieve_from_qdrant)
- **Polish (Phase 6)**: Depends on all story phases complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependency on US2/US3
- **US2 (P2)**: After US1 (modifies `run_repl()` built in T010)
- **US3 (P3)**: After Foundational (extends T003/T006 stubs) — can be done concurrently with US2

### Within Each Story

- format_passages (T007), retrieve_book_content tool (T008), build_agent (T009) — all independent, can be written in parallel
- run_repl T010 depends on T007+T008+T009 (all must exist to test)
- main T011 depends on T010

---

## Parallel Example: User Story 1

```bash
# These 3 functions have no dependency on each other — write all 3 before T010:
Task T007: "Implement format_passages() in agent.py"
Task T008: "Implement @function_tool retrieve_book_content() in agent.py"
Task T009: "Implement build_agent() in agent.py"

# After T007/T008/T009 complete — they're all needed by T010:
Task T010: "Implement run_repl() basic version in agent.py"
Task T011: "Implement main() in agent.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: T001, T002 — create file + install dep
2. Phase 2: T003–T006 — config + Qdrant + retrieval primitives
3. Phase 3: T007–T011 — format → tool → agent → repl → main
4. **STOP and VALIDATE**: `cd backend && uv run python ../agent.py` → ask one question → grounded answer with source URL
5. This is a complete, running RAG agent

### Incremental Delivery

1. T001–T006 → file exists, Qdrant connected, retrieval works
2. T007–T011 → US1: single-question grounded Q&A (MVP!)
3. T012 → US2: multi-turn context retention
4. T013–T014 → US3: env var configurable retrieval
5. T015–T016 → polish: graceful exit + end-to-end validation

---

## Notes

- All tasks modify `agent.py` at project root; run via `cd backend && uv run python ../agent.py`
- T001 modifies `backend/pyproject.toml` (only task that touches a different file)
- `retrieve_book_content` must be defined as a closure OR `config`/`client` must be accessible via module-level variables — plan uses closure pattern
- `OPENAI_API_KEY` must be added to `backend/.env` manually before T003 can pass validation
- No new test files — manual REPL interaction validates all user stories
