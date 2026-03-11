---
id: "040"
title: fastapi-rag-integration-plan
stage: plan
date: 2026-03-11
surface: agent
model: claude-sonnet-4-6
feature: 010-fastapi-rag-integration
branch: 010-fastapi-rag-integration
user: hp
command: /sp.plan
labels: ["plan","fastapi","rag","docusaurus","chatwidget","backend","frontend"]
links:
  spec: specs/010-fastapi-rag-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/010-fastapi-rag-integration/plan.md
  - specs/010-fastapi-rag-integration/research.md
  - specs/010-fastapi-rag-integration/data-model.md
  - specs/010-fastapi-rag-integration/quickstart.md
  - specs/010-fastapi-rag-integration/contracts/openapi.yaml
tests:
  - Constitution Check: all 7 gates PASS
  - Agent context updated via update-agent-context.ps1
---

## Prompt

Spec-4: Frontend-Backend Integration with FastAPI
Confirm existing chatbot UI in 'book_frontend/ (Docusaurus) is used as-is
Build chatbot UI to display across the entire book frontend
Create 'api.py at project backend and set up FastAPI server
Expose a query endpoint that calls the agent from 'agent.py
Return agent responses to the frontend via JSON

## Response snapshot

Generated full implementation plan for feature 010 at `specs/010-fastapi-rag-integration/plan.md`.

**Key architectural decisions**:
1. Agent singleton via FastAPI `lifespan` (QdrantClient + Agent created once at startup, stored in `app.state`)
2. `await Runner.run()` in async FastAPI endpoint; sources extracted from `result.to_input_list()` tool output messages
3. Docusaurus Root swizzle at `book/src/theme/Root.js` for global chat widget injection
4. CORS: allow localhost:3000 + Vercel production URL
5. `api.py` lives in `backend/`; imports `agent.py` functions via sys.path

**Note**: `book_frontend/` confirmed as `book/` — no `book_frontend/` directory exists. Docusaurus config used as-is.

**Artifacts generated**:
- `plan.md` — full implementation plan with architecture decisions
- `research.md` — 6 decisions resolved (singleton, async pattern, Root swizzle, CORS, deps, frontend dir)
- `data-model.md` — 5 entities (QueryRequest, QueryResponse, SourceReference, ErrorResponse, HealthStatus)
- `contracts/openapi.yaml` — full OpenAPI 3.1 spec for POST /query + GET /health
- `quickstart.md` — step-by-step local dev guide with troubleshooting

**Constitution check**: All 7 gates PASS.

**ADR suggestion**: Backend production hosting strategy (Vercel functions vs dedicated server).

## Outcome

- ✅ Impact: Complete implementation plan ready; all design decisions resolved; contracts defined; frontend injection strategy confirmed
- 🧪 Tests: Constitution Check 7/7 PASS; agent context updated
- 📁 Files: plan.md, research.md, data-model.md, quickstart.md, contracts/openapi.yaml
- 🔁 Next prompts: /sp.tasks to generate implementation tasks; optionally /sp.adr fastapi-production-hosting
- 🧠 Reflection: book_frontend/ was an alias for book/ — clarified in research.md R-006; source extraction approach (to_input_list parse) avoids any changes to agent.py tool definition

## Evaluation notes (flywheel)

- Failure modes observed: None — all scripts ran successfully
- Graders run and results (PASS/FAIL): Constitution Check PASS (7/7)
- Prompt variant (if applicable): null
- Next experiment: Confirm agent.py can be imported from backend/api.py without circular imports before implementing
