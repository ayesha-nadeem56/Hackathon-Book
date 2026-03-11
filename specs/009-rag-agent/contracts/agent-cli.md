# Contract: Agent CLI REPL

**Feature**: 009-rag-agent | **Date**: 2026-03-10
**Artifact**: `agent.py` (project root)

---

## Invocation

```bash
# From backend/ directory (uses backend uv environment):
cd backend && uv run python ../agent.py
```

---

## Session Flow

Turn 1 (initial question):
- User types question at `> ` prompt
- Agent calls `retrieve_book_content(query)` tool
- Agent prints answer with source URLs cited
- Prompt returns

Turn 2+ (follow-up):
- Prior conversation history maintained in memory via `to_input_list()`
- User types follow-up; agent interprets context from history
- Same retrieve-then-answer cycle

Exit:
- User types `quit`, `exit`, or `q` → prints "Goodbye!" and exits 0
- Ctrl-C → caught with KeyboardInterrupt → prints "Goodbye!" and exits 0

---

## Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `OPENAI_API_KEY` | ✅ | — | OpenAI API key (NEW for this feature) |
| `COHERE_API_KEY` | ✅ | — | For query embedding |
| `QDRANT_URL` | ✅ | — | Qdrant Cloud endpoint |
| `QDRANT_API_KEY` | ✅ | — | Qdrant auth key |
| `COLLECTION_NAME` | ✅ | — | Vector collection name |
| `COHERE_MODEL` | ❌ | `embed-english-v3.0` | Must match ingestion model |
| `TOP_K` | ❌ | `3` | Max passages per retrieval |
| `SCORE_THRESHOLD` | ❌ | `None` | Min relevance score |
| `AGENT_MODEL` | ❌ | `gpt-4o` | OpenAI model name |

All loaded from `backend/.env` via `load_dotenv("backend/.env")`.

---

## Exit Codes

| Code | Condition |
|------|-----------|
| `0` | Normal exit (user typed quit or Ctrl-C) |
| `1` | Missing required environment variable |
| `2` | Qdrant connection failed or collection not found |
| `3` | Qdrant collection exists but has 0 vectors |

---

## Tool Contract: retrieve_book_content

**Input**: `query: str` — natural-language question or search phrase

**Output** (str, returned to agent):
```
[Passage 1] score=0.65
Title: Chapter 1: NVIDIA Isaac Sim
URL: https://hackathon-book-uogx.vercel.app/docs/module-3-isaac-brain/chapter-1-isaac-sim
Text: "NVIDIA Isaac Sim is a high-fidelity robot simulation platform..."

[Passage 2] score=0.58
...
```

**If no results**: Returns `"No relevant passages found in the book for this query."`

---

## System Prompt (grounding contract)

The agent's `instructions` field enforces FR-003 (grounding-only):

```
You are a helpful assistant that answers questions about this book's content.
You MUST call the retrieve_book_content tool for every question to find relevant passages.
Only answer based on what the tool returns. Do not use your training knowledge to
answer factual questions about the book's topics.
If the tool returns no relevant passages, say:
"I don't have relevant information in the book to answer that question."
Always cite the source URLs from the retrieved passages at the end of your answer.
```

---

## Functional Requirement Mapping

| FR | Implemented By |
|----|----------------|
| FR-001 Accept natural-language questions | `run_repl()` input() loop |
| FR-002 Invoke retrieval tool per question | `@function_tool retrieve_book_content` |
| FR-003 Ground answers in retrieved content | System prompt grounding instruction |
| FR-004 Display source URLs | `format_passages()` includes URLs; system prompt instructs citation |
| FR-005 Maintain session context | `result.to_input_list()` history management |
| FR-006 Communicate when no content found | Tool returns "No relevant passages found"; system prompt instructs agent to say so |
| FR-007 Configurable TOP_K + SCORE_THRESHOLD | `load_config()` + `retrieve_from_qdrant()` |
| FR-008 Graceful error handling | `init_qdrant()` SystemExit codes; Ctrl-C handler |
| FR-009 Config from environment | `load_dotenv("backend/.env")` |
