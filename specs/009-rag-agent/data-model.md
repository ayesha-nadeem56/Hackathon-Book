# Data Model: AI-Powered Book Q&A Agent

**Feature**: 009-rag-agent | **Date**: 2026-03-10

---

## Entities

### Config

Loaded from `backend/.env` at startup. All required fields validated; `SystemExit(1)` on missing.

| Field | Type | Env Var | Required | Default | Notes |
|-------|------|---------|----------|---------|-------|
| `openai_api_key` | `str` | `OPENAI_API_KEY` | ✅ | — | OpenAI API key for agent model |
| `cohere_api_key` | `str` | `COHERE_API_KEY` | ✅ | — | Cohere key for query embedding |
| `qdrant_url` | `str` | `QDRANT_URL` | ✅ | — | Qdrant Cloud cluster endpoint |
| `qdrant_api_key` | `str` | `QDRANT_API_KEY` | ✅ | — | Qdrant authentication key |
| `collection_name` | `str` | `COLLECTION_NAME` | ✅ | — | Must match Spec-1 collection |
| `cohere_model` | `str` | `COHERE_MODEL` | ❌ | `embed-english-v3.0` | Must match Spec-1 model |
| `top_k` | `int` | `TOP_K` | ❌ | `3` | Max passages per retrieval call |
| `score_threshold` | `float\|None` | `SCORE_THRESHOLD` | ❌ | `None` | Min relevance score filter |
| `agent_model` | `str` | `AGENT_MODEL` | ❌ | `gpt-4o` | OpenAI model for the agent |

**New in this spec vs Spec-2**: `openai_api_key`, `agent_model`.

---

### RetrievalInput

The `@function_tool`'s input. Auto-generated from function type hint.

| Field | Type | Constraints |
|-------|------|-------------|
| `query` | `str` | Non-empty; passed directly to Cohere embed |

---

### RetrievedPassage (internal)

A single Qdrant ScoredPoint mapped to a readable struct before formatting.

| Field | Type | Source |
|-------|------|--------|
| `rank` | `int` | 1-based position in results |
| `score` | `float` | `ScoredPoint.score` |
| `url` | `str` | `payload["url"]` |
| `title` | `str` | `payload["title"]` |
| `chunk_index` | `int` | `payload["chunk_index"]` |
| `snippet` | `str` | `payload["text"][:200]` |

---

### RetrievalOutput (tool return)

Formatted `str` returned by `retrieve_book_content()` to the agent.

```
[Passage 1] score=0.65
Title: Chapter 1: NVIDIA Isaac Sim
URL: https://hackathon-book-uogx.vercel.app/docs/module-3-isaac-brain/chapter-1-isaac-sim
Text: "NVIDIA Isaac Sim is a high-fidelity robot simulation platform built on top of..."

[Passage 2] score=0.58
Title: Chapter 2: Cognitive Planning with LLMs
URL: https://hackathon-book-uogx.vercel.app/docs/module-4-vla/chapter-2-llm-planner
Text: "The LLM planner takes a natural-language instruction and produces..."

No relevant passages found.  ← (when results list is empty)
```

---

### ConversationHistory

The in-memory multi-turn state. Managed by the OpenAI Agents SDK.

| Field | Type | Source |
|-------|------|--------|
| `items` | `list[TResponseInputItem]` | `result.to_input_list()` after each turn |

**State transitions**:
```
Session Start
    │
    ▼
history = []  (empty, first turn uses plain str)
    │
    ▼
Turn N: result = await Runner.run(agent, history_or_str)
    │
    ▼
history = result.to_input_list()
    │
    ▼
history.append({"role": "user", "content": next_question})
    │
    ▼  (repeat for Turn N+1)
    └─────────────────────────────────┐
                                      ▼
                               user types 'quit' → break
```

---

## Relationships

- `Config` is created once per session; passed to `init_qdrant()` and embedded inside the `retrieve_book_content` closure.
- `RetrievalInput` is constructed by the agent SDK automatically from the user's question.
- `RetrievedPassage` objects are created inside the tool function from Qdrant results.
- `RetrievalOutput` (str) is returned to the agent and included in `ConversationHistory`.
- `ConversationHistory` grows by 2+ items per turn (user message + assistant response + tool call/result items).
- `agent.py` shares the same `backend/.env` as `main.py` (Spec-1) and `retrieve.py` (Spec-2).
