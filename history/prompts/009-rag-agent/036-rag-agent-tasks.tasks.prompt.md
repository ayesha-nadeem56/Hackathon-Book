---
id: 036
title: RAG Agent Tasks
stage: tasks
date: 2026-03-10
surface: agent
model: claude-sonnet-4-6
feature: 009-rag-agent
branch: 009-rag-agent
user: hp
command: /sp.tasks
labels: ["tasks","rag","agent","openai-agents-sdk","retrieval","grounding"]
links:
  spec: specs/009-rag-agent/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-rag-agent/tasks.md
tests:
  - n/a (tasks stage — no test tasks generated, tests not requested)
---

## Prompt

/sp.tasks

## Response snapshot

Generated `specs/009-rag-agent/tasks.md` with 16 tasks across 6 phases for `agent.py` at project root:

- **Phase 1 — Setup (T001–T002)**: Install openai-agents dep via `uv add`; create agent.py skeleton with UTF-8 fix + imports
- **Phase 2 — Foundational (T003–T006)**: load_config() with 5 required keys; init_qdrant() with verification; embed_query() Cohere ClientV2 search_query; retrieve_from_qdrant() query_points (T005/T006 parallelizable)
- **Phase 3 — US1/P1 MVP (T007–T011)**: format_passages(), @function_tool retrieve_book_content(), build_agent() with grounding prompt, run_repl() basic (stateless), main() entry point
- **Phase 4 — US2/P2 (T012)**: Add to_input_list() history management to run_repl() — replaces stateless Runner.run(agent, str) with history-based multi-turn pattern
- **Phase 5 — US3/P3 (T013–T014)**: TOP_K int + SCORE_THRESHOLD float-or-None parsing in load_config(); wire both through to retrieve_from_qdrant() query_points call
- **Phase 6 — Polish (T015–T016)**: KeyboardInterrupt graceful exit; quickstart.md end-to-end validation

Parallel opportunities: T005/T006 (Phase 2), T007/T008/T009 (Phase 3).
MVP scope: Phases 1–3 (T001–T011) → working interactive RAG agent.

## Outcome

- 16 tasks; all 3 user stories covered; MVP = T001–T011; ready for /sp.implement
- n/a (tasks not requested)
- Files: specs/009-rag-agent/tasks.md
- Next: /sp.implement
- Reflection: US2 is a single task (T012) that modifies run_repl() — the to_input_list() pattern is minimal; US3 extends foundational functions as in prior features

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders: format validation PASS — all 16 tasks have checkbox + ID + story label (where required) + file path
- Prompt variant: n/a
- Next experiment: n/a
