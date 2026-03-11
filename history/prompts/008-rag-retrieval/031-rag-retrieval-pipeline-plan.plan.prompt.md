---
id: 031
title: RAG Retrieval Pipeline Plan
stage: plan
date: 2026-03-10
surface: agent
model: claude-sonnet-4-6
feature: 008-rag-retrieval
branch: 008-rag-retrieval
user: hp
command: /sp.plan
labels: ["plan","rag","retrieval","qdrant","cohere","retrieve.py"]
links:
  spec: specs/008-rag-retrieval/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-rag-retrieval/plan.md
  - specs/008-rag-retrieval/research.md
  - specs/008-rag-retrieval/data-model.md
  - specs/008-rag-retrieval/quickstart.md
  - specs/008-rag-retrieval/contracts/retrieval-cli.md
tests:
  - n/a (plan stage)
---

## Prompt

/sp.plan
Spec-2: Retrieval & Pipeline Validation
- Create a single file retrieve.py in the root
- Connect to Qdrant and load existing vector collections
- Accept a test query and perform top-k similarity search
- Validate results using returned text, metadata, and source URLs

## Response snapshot

Generated full implementation plan for `008-rag-retrieval` feature. All planning artifacts written:

- **plan.md**: Technical context (Python 3.14.2, cohere ClientV2, qdrant-client 1.17), Constitution Check (all 5 principles pass), project structure (`backend/retrieve.py`), implementation checklist (7 functions), risks & follow-ups.
- **research.md**: 7 research items resolved — Qdrant `query_points()` API pattern, Cohere ClientV2 `input_type="search_query"`, server-side score_threshold filtering, exit code taxonomy (0/1/2/3), default query list, UTF-8 stdout Windows fix, file location (`backend/` not repo root).
- **data-model.md**: Config entity (7 fields, validation rules), Query, RetrievalResult (8 fields), ValidationReport (5 fields), state transition diagram.
- **contracts/retrieval-cli.md**: Full CLI contract — invocation syntax, env vars table, stdout format, exit codes table, error messages table, FR→function mapping.
- **quickstart.md**: 5-step guide, success criteria verification table, troubleshooting table.

Key architectural decisions:
- `client.query_points()` (not `search()`) — qdrant-client 1.17 API
- `cohere.ClientV2` + `input_type="search_query"` for query embedding
- Script lives in `backend/retrieve.py`, shares `.env` and `pyproject.toml` from Spec-1
- No new Python dependencies required

## Outcome

- ✅ Impact: 5 planning artifacts written; all NEEDS CLARIFICATION resolved; Constitution Check passes; ready for /sp.tasks
- 🧪 Tests: n/a (plan stage)
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/retrieval-cli.md
- 🔁 Next prompts: /sp.tasks then /sp.implement
- 🧠 Reflection: File location clarified (backend/ not repo root per spec Assumptions); exit code taxonomy adds CI-friendly non-zero codes for 3 distinct failure modes

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): Constitution Check all PASS
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
