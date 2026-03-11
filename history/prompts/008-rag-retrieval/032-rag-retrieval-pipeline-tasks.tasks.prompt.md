---
id: 032
title: RAG Retrieval Pipeline Tasks
stage: tasks
date: 2026-03-10
surface: agent
model: claude-sonnet-4-6
feature: 008-rag-retrieval
branch: 008-rag-retrieval
user: hp
command: /sp.tasks
labels: ["tasks","rag","retrieval","qdrant","cohere","retrieve.py"]
links:
  spec: specs/008-rag-retrieval/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-rag-retrieval/tasks.md
tests:
  - n/a (tasks stage — no test tasks generated, tests not requested)
---

## Prompt

/sp.tasks

## Response snapshot

Generated `specs/008-rag-retrieval/tasks.md` with 14 tasks across 6 phases for `backend/retrieve.py`:

- **Phase 1 — Setup (T001)**: Create retrieve.py skeleton with UTF-8 fix, imports, DEFAULT_QUERIES
- **Phase 2 — Foundational (T002–T003)**: load_config() with required key validation + SystemExit(1); init_qdrant() with collection existence + empty check + SystemExit(2/3)
- **Phase 3 — US1/P1 MVP (T004–T007)**: embed_query() Cohere ClientV2 search_query, retrieve() query_points(), print_results() formatter, main() query loop
- **Phase 4 — US2/P2 (T008–T010)**: validate_payload() field checker with WARNING logs, integration into main() loop, ValidationReport summary printer
- **Phase 5 — US3/P3 (T011–T012)**: TOP_K int parsing + SCORE_THRESHOLD float-or-None in load_config(), wire both into query_points() call in retrieve()
- **Phase 6 — Polish (T013–T014)**: Cohere API error handling, end-to-end quickstart.md validation

Parallel opportunities: T004/T005/T006 (Phase 3), T011/T012 (Phase 5).
MVP scope: Phases 1–3 (T001–T007) → functional retrieve.py that returns ranked results.

## Outcome

- ✅ Impact: 14 tasks; all 3 user stories covered; MVP = T001–T007; ready for /sp.implement
- 🧪 Tests: n/a (not requested)
- 📁 Files: specs/008-rag-retrieval/tasks.md
- 🔁 Next prompts: /sp.implement
- 🧠 Reflection: Single-file structure limits true parallelism but T004/T005/T006 are genuinely independent functions; US3 cleanly extends Phase 2/3 stubs rather than requiring new phases

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): format validation PASS — all 14 tasks have checkbox + ID + story label (where required) + file path
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
