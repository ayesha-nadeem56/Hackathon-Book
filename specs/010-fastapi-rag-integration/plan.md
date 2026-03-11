# Implementation Plan: FastAPI RAG Integration — Backend-Frontend Bridge

**Branch**: `010-fastapi-rag-integration` | **Date**: 2026-03-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-fastapi-rag-integration/spec.md`

---

## Summary

Expose the existing RAG Q&A agent (`agent.py`) as an HTTP service via a FastAPI server (`backend/api.py`), and integrate a floating chat widget into the Docusaurus frontend (`book/`) that communicates with the API. The agent is initialized once at server startup (singleton via `lifespan`) and invoked per request via `Runner.run()`. The frontend widget is injected globally using Docusaurus Root swizzle so it appears on every page without touching any markdown files.

---

## Technical Context

**Language/Version**: Python 3.11+ (backend), JavaScript/React (Docusaurus frontend)
**Primary Dependencies**:
- Backend: `fastapi`, `uvicorn[standard]`, `openai-agents`, `qdrant-client`, `cohere`, `python-dotenv` (all managed by `uv` in `backend/pyproject.toml`)
- Frontend: Docusaurus v3 (existing), React 18 (bundled with Docusaurus)

**Storage**: Qdrant Cloud (existing, already populated by `backend/main.py`)
**Testing**: `pytest` + `httpx` (backend API tests); manual browser walkthrough (frontend)
**Target Platform**: Local development (Windows/macOS/Linux); production via Vercel (frontend) + separate backend host TBD
**Project Type**: Web application (FastAPI backend + Docusaurus frontend)
**Performance Goals**: Query round-trip ≤ 10 seconds (per SC-001); health check response ≤ 2 seconds (per SC-003)
**Constraints**: No session memory across requests; no auth for local dev; no hardcoded secrets; free-tier Qdrant and Groq limits apply
**Scale/Scope**: Local single-user development; not production-hardened in this feature

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked post-design.*

| Principle | Check | Status |
|-----------|-------|--------|
| I. Accuracy & Technical Correctness | Agent grounding enforced; only retrieved content returned; sources cited | ✅ PASS |
| II. Clarity & Readability | API returns structured JSON; chatbot renders answer + source links clearly | ✅ PASS |
| III. Reproducibility of Workflows | `quickstart.md` documents all steps; env vars in `.env.example`; no version-unpinned deps | ✅ PASS |
| IV. Modularity & Maintainable Architecture | FastAPI is the mandated backend; Docusaurus is the mandated frontend; each component replaceable; smallest viable change applied | ✅ PASS |
| V. Transparency in AI-Generated Content | Chatbot clearly labelled as AI; sources cited; no fabrication outside retrieved corpus | ✅ PASS |
| Secrets / No hardcoding | All keys in `backend/.env`; `.env.example` updated | ✅ PASS |
| Stack compliance | Python FastAPI backend + Docusaurus frontend — matches constitution stack exactly | ✅ PASS |

**Gate result: ALL PASS — proceed to implementation.**

---

## Project Structure

### Documentation (this feature)

```text
specs/010-fastapi-rag-integration/
├── plan.md              ← This file
├── spec.md              ← Feature specification
├── research.md          ← Phase 0: resolved decisions
├── data-model.md        ← Phase 1: entities
├── quickstart.md        ← Phase 1: local dev guide
├── contracts/
│   └── openapi.yaml     ← Phase 1: API contract
├── checklists/
│   └── requirements.md  ← Spec quality checklist
└── tasks.md             ← Phase 2 output (/sp.tasks — NOT created here)
```

### Source Code Layout

```text
# Backend (Python, managed by uv)
backend/
├── api.py              ← NEW: FastAPI app (POST /query, GET /health)
├── main.py             ← existing: embedding pipeline (no changes)
├── retrieve.py         ← existing: retrieval helpers (no changes)
└── pyproject.toml      ← MODIFY: add fastapi, uvicorn[standard]

# Project root
agent.py                ← MODIFY: extract run_once() as importable function
backend/.env            ← existing (no changes to keys needed)
backend/.env.example    ← MODIFY: document any new env vars

# Frontend (Docusaurus, Node/React)
book/
└── src/
    ├── theme/
    │   └── Root.js                     ← NEW: global Root swizzle
    └── components/
        └── ChatWidget/
            ├── index.js                ← NEW: floating chat widget
            └── styles.module.css       ← NEW: panel + button styles
```

**Structure Decision**: Web application layout (Option 2). Backend and frontend are separate directories; `backend/api.py` imports from `agent.py` at project root via `sys.path` adjustment. No new top-level directories created.

---

## Architecture Decisions

### A-001: Agent Singleton via FastAPI Lifespan

The `QdrantClient`, `Agent`, and `RunConfig` are created **once** at server startup using FastAPI's `lifespan` context manager and stored in `app.state`. They are reused for all requests.

**Why**: Qdrant maintains a persistent connection pool; reconnecting per request adds ~200-500 ms. The `Agent` and `RunConfig` objects are stateless and thread/coroutine-safe.

**Implementation**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = load_config()
    qdrant_client = init_qdrant(cfg)
    agent, run_config = build_agent(cfg, qdrant_client)
    app.state.cfg = cfg
    app.state.agent = agent
    app.state.run_config = run_config
    yield
    qdrant_client.close()
```

### A-002: Source Extraction via Agent Tool Output

The `retrieve_book_content` tool in `agent.py` already returns formatted passage text including URLs. For structured source extraction in `api.py`, the `build_agent` function will be called from `api.py` with a request-scoped collector list passed via closure.

**Alternative approach** (simpler, no agent.py changes): After `Runner.run()`, scan `result.to_input_list()` for messages with role `"tool"` and parse URL/title from the formatted passage text using the known format (`URL: <url>`, `Title: <title>`).

**Decision**: Use the `to_input_list()` parse approach — requires no changes to `agent.py`'s tool definition, and the format is already deterministic.

### A-003: Frontend Injection via Root Swizzle

A floating chat widget is injected at `book/src/theme/Root.js`. This wraps the entire Docusaurus application and renders the `ChatWidget` component on every page. No markdown files are modified.

### A-004: CORS Allow-List

CORS middleware in `api.py` allows `http://localhost:3000` (Docusaurus dev) and `https://hackathon-book-uogx.vercel.app` (production). No wildcard origins.

### A-005: Query Timeout

A 30-second `asyncio.wait_for()` timeout wraps `Runner.run()`. If exceeded, HTTP 504 is returned. This prevents the server from hanging on slow Groq responses.

---

## Implementation Design

### backend/api.py — FastAPI Server

```text
Startup (lifespan):
  1. load_config() from agent.py          → cfg dict
  2. init_qdrant(cfg)                     → qdrant_client stored in app.state
  3. build_agent(cfg, qdrant_client)      → (agent, run_config) stored in app.state

POST /query:
  Input:  { "query": "<string>" }
  1. Validate: query non-empty, ≤ 2000 chars  → 400 on fail
  2. asyncio.wait_for(
       Runner.run(agent, query, run_config=run_config),
       timeout=30
     )                                         → 504 on timeout
  3. Extract answer = result.final_output
  4. Parse sources from result.to_input_list() → scan tool output messages
  5. Return { "answer": ..., "sources": [...] } → 200
  6. On any exception:                          → 503

GET /health:
  1. Ping Qdrant: client.get_collections()
  2. Check app.state.agent is not None
  3. Return { "status": "ok/degraded", "dependencies": {...} }
```

### agent.py — Single Modification

Add a module-level `run_once()` async function that `api.py` can import:

```python
async def run_once(agent: Agent, run_config: RunConfig, query: str) -> "Result":
    """Run the agent for a single query. Used by api.py."""
    return await Runner.run(agent, query, run_config=run_config)
```

This avoids duplicating `Runner.run()` call logic and keeps the REPL loop separate from the HTTP use case.

### book/src/theme/Root.js — Global Wrapper

```jsx
import React from 'react';
import ChatWidget from '@site/src/components/ChatWidget';

export default function Root({ children }) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
```

### book/src/components/ChatWidget/index.js — Chat UI

State: `isOpen` (bool), `messages` (array of `{role, text}`), `inputValue` (string), `isLoading` (bool)

Behavior:
- Toggle button: fixed bottom-right, always visible
- On submit: validate non-empty input → `fetch('http://localhost:8000/query', { method: 'POST', body: JSON.stringify({ query }) })`
- On success: append `{ role: 'assistant', text: answer, sources }` to messages
- On error: append error message
- Render sources as `<a href={url} target="_blank">{title || url}</a>`

---

## Error Handling

| Error condition | HTTP status | Response body |
|---|---|---|
| `query` missing or empty | 400 | `{"error": "query must be a non-empty string"}` |
| `query` > 2000 chars | 400 | `{"error": "query exceeds maximum length of 2000 characters"}` |
| Agent timeout (>30s) | 504 | `{"error": "Agent response timed out. Please try again."}` |
| Qdrant unreachable | 503 | `{"error": "Retrieval service unavailable. Please try again shortly."}` |
| Any unhandled exception | 503 | `{"error": "Internal service error."}` |

---

## Complexity Tracking

No constitution violations. No complexity justification needed.

---

## Phase 0 Output

- [x] `research.md` — All decisions resolved, no NEEDS CLARIFICATION items remain
  - R-001: Agent singleton via lifespan ✅
  - R-002: `await Runner.run()` in async endpoint; sources from `to_input_list()` ✅
  - R-003: Docusaurus Root swizzle at `book/src/theme/Root.js` ✅
  - R-004: CORS for localhost:3000 + Vercel URL ✅
  - R-005: `fastapi` + `uvicorn[standard]` added to `backend/pyproject.toml` ✅
  - R-006: `book_frontend/` → confirmed as `book/` directory ✅

## Phase 1 Output

- [x] `data-model.md` — Entities: QueryRequest, QueryResponse, SourceReference, ErrorResponse, HealthStatus
- [x] `contracts/openapi.yaml` — Full OpenAPI 3.1 contract for POST /query and GET /health
- [x] `quickstart.md` — Local dev setup, test commands, troubleshooting table, file layout

---

## Follow-ups & Risks

1. **Groq rate limits**: The free-tier Groq API has request-per-minute limits. Concurrent frontend users may hit 429 errors — the current plan returns HTTP 503 for all agent errors, which covers this. Rate limiting is out of scope for this feature.
2. **Production backend hosting**: `api.py` is designed for local development only. Deployment to Vercel (Python functions) or a separate host is out of scope and will require an ADR.
3. **agent.py `sys.path` coupling**: `api.py` imports from `agent.py` via `sys.path` injection. If the project structure changes (e.g., moving `agent.py` into `backend/`), the import path must be updated.

📋 Architectural decision detected: Backend API hosting strategy for production (Vercel functions vs. dedicated server vs. Railway/Fly.io). Document reasoning and tradeoffs? Run `/sp.adr fastapi-production-hosting`
