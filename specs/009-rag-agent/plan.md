# Implementation Plan: AI-Powered Book Q&A Agent

**Branch**: `009-rag-agent` | **Date**: 2026-03-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-rag-agent/spec.md`

## Summary

Build `agent.py` at the project root — a single-file conversational agent that:
1. Loads credentials from `backend/.env` (OPENAI_API_KEY, COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME).
2. Defines a `retrieve_book_content` tool using the `@function_tool` decorator (OpenAI Agents SDK).
3. The tool calls the existing Cohere + Qdrant retrieval logic from Spec-2 (embed → query_points).
4. Initialises an `Agent` with a strict grounding system prompt: answer only from retrieved content.
5. Runs an interactive REPL loop: user types a question → agent calls retrieval tool → agent answers.
6. Passes `result.to_input_list()` + new user message each turn for multi-turn context.

Depends on Spec-1 (007-embedding-pipeline) for populated vectors and reuses Spec-2 (008-rag-retrieval) retrieval logic inline. Adds one new dependency: `openai-agents`.

---

## Technical Context

**Language/Version**: Python 3.14.2 (managed with `uv` in `backend/`)
**Primary Dependencies**:
- `openai-agents` — NEW dep, added to `backend/pyproject.toml` via `uv add openai-agents`
- `cohere` (ClientV2), `qdrant-client==1.17.0`, `python-dotenv` — existing from Spec-1/2
**New Env Var**: `OPENAI_API_KEY` — required by OpenAI Agents SDK
**Storage**: Qdrant Cloud (read-only) — same collection `book-embeddings` from Spec-1
**Testing**: Manual REPL interaction
**Target Platform**: Developer workstation CLI (Windows/Linux)
**Project Type**: Single-file script at repo root, run via `cd backend && uv run python ../agent.py`
**Performance Goals**: First response under 15 seconds (SC-005)
**Constraints**: Grounding-only — agent MUST NOT answer from training knowledge alone (FR-003)
**Scale/Scope**: Single developer session, interactive REPL

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Accuracy & Technical Correctness | ✅ PASS | Agent grounded exclusively on retrieved book passages; FR-003 enforces no hallucination |
| II. Clarity & Readability | ✅ PASS | Single file, REPL interface, clear system prompt |
| III. Reproducibility of Workflows | ✅ PASS | All config via `backend/.env`; `uv run` invocation reproducible |
| IV. Modularity & Maintainable Architecture | ✅ PASS | Smallest viable change — single file; retrieval logic is inlined from existing retrieve.py |
| V. Transparency in AI-Generated Content | ✅ PASS | Agent grounding enforced by system prompt; source URLs displayed for every cited passage |

**Gate result: ALL PASS — no violations to justify.**

---

## Project Structure

### Documentation (this feature)

```text
specs/009-rag-agent/
├── plan.md              ✅ This file
├── research.md          ✅ Phase 0 output
├── data-model.md        ✅ Phase 1 output
├── quickstart.md        ✅ Phase 1 output
├── contracts/
│   └── agent-cli.md     ✅ Phase 1 output
└── tasks.md             (Phase 2 — /sp.tasks command)
```

### Source Code (repository)

```text
agent.py                 # NEW: RAG agent REPL (this feature, at project root)

backend/
├── main.py              # Spec-1: embedding pipeline (unchanged)
├── retrieve.py          # Spec-2: retrieval validation (unchanged)
├── .env                 # Shared credentials (gitignored) — agent.py loads from here
└── pyproject.toml       # uv project — add openai-agents here
```

**Structure Decision**: `agent.py` at project root per user specification. Run via `cd backend && uv run python ../agent.py` so it uses the backend uv virtual environment, pyproject.toml (with `openai-agents`), and `backend/.env`.

---

## Phase 0: Research Findings

See [research.md](research.md). Key decisions:

| Decision | Rationale |
|----------|-----------|
| `openai-agents` SDK (`Agent`, `Runner`, `@function_tool`) | Per user specification; built-in tool dispatch, multi-turn via `to_input_list()`, async runner |
| `result.to_input_list()` for multi-turn history | Official SDK pattern; works with any model; no server-side storage |
| Inline retrieval logic (embed_query + retrieve from retrieve.py) | Keeps agent.py self-contained; avoids sys.path manipulation |
| `gpt-4o` as agent model | Best general-purpose OpenAI model |
| `load_dotenv("backend/.env")` from project root | Shares existing credential file; no duplication |
| Grounding system prompt | FR-003 and FR-006 enforcement at LLM prompt level |

---

## Phase 1: Design

### Data Model

See [data-model.md](data-model.md). Summary:
- **Config**: loaded from `backend/.env`; adds `OPENAI_API_KEY` as new required key
- **RetrievalInput**: `query: str` — the tool's input
- **RetrievalOutput**: formatted string with ranked passages (rank, score, URL, title, snippet)
- **ConversationHistory**: `list[TResponseInputItem]` — SDK's native format via `to_input_list()`

### CLI Contract

See [contracts/agent-cli.md](contracts/agent-cli.md). Interface summary:
```
cd backend && uv run python ../agent.py
[QDRANT]  Connected — 'book-embeddings' has 75 vector(s)
[AGENT]   BookAgent ready. Ask a question about the book. Type 'quit' to exit.

> What is ROS2?
[agent calls retrieve_book_content tool]
Assistant: Based on the retrieved passages, ROS2 (Robot Operating System 2) is...
Sources: https://hackathon-book.../docs/module-1-ros2/chapter-1

> quit
Goodbye!
```

---

## Implementation Checklist

- [ ] Add `openai-agents` to `backend/pyproject.toml` via `uv add openai-agents`
- [ ] Add `OPENAI_API_KEY` to `backend/.env` and `backend/.env.example`
- [ ] `load_config()` — loads `backend/.env`, validates including `OPENAI_API_KEY`, returns dict
- [ ] `init_qdrant()` — connect and verify collection non-empty (same as retrieve.py)
- [ ] `embed_query()` — Cohere ClientV2 search_query embedding (same as retrieve.py)
- [ ] `retrieve_from_qdrant()` — query_points with top_k + threshold (same as retrieve.py)
- [ ] `format_passages()` — format ScoredPoint list → readable string for tool return
- [ ] `@function_tool retrieve_book_content(query)` — wraps embed + retrieve + format; returns str
- [ ] `build_agent(config)` — creates `Agent` with grounding system prompt and retrieval tool
- [ ] `run_repl(agent)` — async REPL loop with `to_input_list()` history management
- [ ] `main()` — orchestrates load_config → init_qdrant → asyncio.run(run_repl)
- [ ] UTF-8 stdout fix (Windows, same as main.py and retrieve.py)

---

## Risks & Follow-ups

1. **OPENAI_API_KEY not in backend/.env**: User must add it manually before running; quickstart.md documents this explicitly.
2. **`openai-agents` requires `openai >=2.26.0`**: `uv add openai-agents` pulls this automatically; no conflict expected.
3. **Next**: Run `/sp.tasks` to generate granular task list, then `/sp.implement` to build `agent.py`.
