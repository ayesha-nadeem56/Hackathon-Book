# Research: FastAPI RAG Integration

**Feature**: 010-fastapi-rag-integration
**Date**: 2026-03-11
**Status**: Complete — all NEEDS CLARIFICATION resolved

---

## R-001: Agent Singleton Lifecycle in FastAPI

**Question**: Should the QdrantClient + Agent be created once at startup or per request?

**Decision**: Initialize once at server startup using FastAPI `lifespan` context manager; store in `app.state`.

**Rationale**:
- QdrantClient maintains a persistent HTTP connection pool — re-creating it per request wastes TCP handshakes and Qdrant auth overhead.
- The `Agent` object from the OpenAI Agents SDK is stateless (it holds only name, instructions, model, and tools). It is safe to reuse across concurrent requests.
- `RunConfig` (with `MultiProvider`) is also stateless — safe to share.
- FastAPI `lifespan` is the idiomatic pattern for startup/shutdown resource management (replaces deprecated `@app.on_event`).

**Pattern**:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = load_config()
    client = init_qdrant(cfg)
    agent, run_config = build_agent(cfg, client)
    app.state.agent = agent
    app.state.run_config = run_config
    yield
    client.close()

app = FastAPI(lifespan=lifespan)
```

**Alternatives considered**:
- Per-request init: Rejected — reconnects Qdrant on every query, adds ~200-500 ms latency.
- Module-level globals: Rejected — not testable, blocks startup error handling.

---

## R-002: Calling the Async Agent from a FastAPI Endpoint

**Question**: How to call `Runner.run()` (async coroutine) from a FastAPI async endpoint and extract answer + sources?

**Decision**: Directly `await Runner.run()` inside `async def` endpoint; extract sources from tool output messages in `result.to_input_list()`.

**Rationale**:
- FastAPI async endpoints run in the asyncio event loop — `await` on `Runner.run()` works natively without `asyncio.run()` or `run_in_executor`.
- `result.final_output` is the agent's final text response (answer).
- `result.to_input_list()` returns the full conversation including tool call results. The `retrieve_book_content` tool returns formatted passage text including URLs — these can be parsed to extract structured source references.
- A request-scoped collector list (closure variable in the tool function) provides cleaner source extraction than text parsing.

**Pattern for source extraction**:
```python
# In api.py: wrap agent build with a per-request source collector
sources_collector = []

@function_tool
def retrieve_book_content(query: str) -> str:
    results = retrieve_from_qdrant(client, embed_query(query, cfg), cfg)
    for r in results:
        sources_collector.append({
            "url": r.payload.get("url", ""),
            "title": r.payload.get("title", ""),
        })
    return format_passages(results)
```

However, since `build_agent` in `agent.py` defines the tool as a closure, the cleanest approach for `api.py` is to **import and call the agent functions** (`load_config`, `init_qdrant`, `build_agent`) at startup, then define a thin `query_agent()` async function that:
1. Calls `Runner.run(agent, query_text, run_config=run_config)`
2. Returns `result.final_output` as the answer
3. Parses source URLs from `result.to_input_list()` message tool outputs

**Alternatives considered**:
- Subprocess call to `agent.py`: Rejected — high latency, no structured output.
- Text parsing of `final_output` for URLs: Fragile, depends on agent prompt format.
- Re-implementing retrieval in `api.py`: Rejected — duplicates logic, violates DRY.

---

## R-003: Docusaurus Global Chatbot Component Injection

**Question**: How to inject a floating chat widget visible on every page (including all `/docs/*` pages) without modifying each doc file?

**Decision**: Swizzle the `Root` component by creating `book/src/theme/Root.js`. This wraps the entire Docusaurus application and renders on every route.

**Rationale**:
- `Root` is the top-level React component rendered by Docusaurus before any page content. Any component placed here appears site-wide.
- This is the officially documented pattern for adding global UI elements (chat widgets, cookie banners, modals).
- No need to run `docusaurus swizzle` CLI — simply creating `src/theme/Root.js` is sufficient for "unsafe" swizzle (wrapping, not replacing internals).
- Avoids modifying any markdown/MDX files.
- The floating chat widget can be positioned with CSS `position: fixed` to appear over all content.

**Pattern**:
```jsx
// book/src/theme/Root.js
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

**`ChatWidget` component responsibilities**:
- Toggle button (fixed bottom-right)
- Chat panel with message history (React `useState`)
- Input field + submit
- `fetch()` POST to backend query endpoint
- Render answer + source links

**Alternatives considered**:
- Swizzle `Layout`: More invasive; risks breaking layout on non-docs pages.
- `docusaurus-plugin-client-redirects`: Not applicable.
- Client module (`clientModules`): Can inject JS but not React components natively.
- Custom plugin: Overkill for a single component.

---

## R-004: CORS Configuration

**Question**: What origins must be allowed for CORS?

**Decision**: Allow `http://localhost:3000` (Docusaurus dev server) and the production Vercel URL.

**Pattern**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://hackathon-book-uogx.vercel.app",
    ],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
```

**Rationale**: Docusaurus dev server runs on port 3000 by default. The Vercel URL is the production origin. Wildcards (`*`) are avoided since they are incompatible with credentialed requests.

---

## R-005: Dependency Management

**Question**: Where does FastAPI + uvicorn get added?

**Decision**: Add `fastapi` and `uvicorn[standard]` to `backend/pyproject.toml` dependencies alongside existing packages.

**Rationale**: The `backend/` directory already uses `uv` as its package manager with `pyproject.toml`. Adding FastAPI there keeps all backend dependencies in one managed environment. `api.py` will live in `backend/api.py` and import from `agent.py` (at project root) using a relative path adjustment or `sys.path`.

**Import strategy**: `agent.py` is at the project root. From `backend/api.py`, imports use:
```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from agent import load_config, init_qdrant, build_agent, embed_query, retrieve_from_qdrant, format_passages
```

---

## R-006: Frontend Confirmation — No `book_frontend/` Directory

**Question**: User referenced `book_frontend/` — does this directory exist?

**Finding**: No `book_frontend/` directory exists. The Docusaurus site is at `book/`. The user's reference to `book_frontend/` in the command was an alias for the `book/` directory.

**Decision**: All frontend work targets `book/src/` (components) and `book/src/theme/` (swizzle). The existing Docusaurus configuration in `book/docusaurus.config.js` is used as-is — no config changes required.
