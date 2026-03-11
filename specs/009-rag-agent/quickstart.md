# Quickstart: RAG Agent

**Feature**: 009-rag-agent | **Date**: 2026-03-10

---

## Prerequisites

- [ ] Spec-1 (007-embedding-pipeline) has been run — `book-embeddings` collection is populated.
- [ ] Spec-2 (008-rag-retrieval) confirmed working — `uv run python retrieve.py` returns results.
- [ ] `backend/.env` exists with all Spec-1/2 credentials.
- [ ] Python 3.11+ and `uv` installed. (`python -m uv` if `uv` not in PATH.)
- [ ] OpenAI API key obtained from https://platform.openai.com/api-keys

---

## Step 1: Add OPENAI_API_KEY to backend/.env

Open `backend/.env` and add:

```
OPENAI_API_KEY=sk-...your-key-here...
```

Also add to `backend/.env.example` (with placeholder):

```
OPENAI_API_KEY=your-openai-api-key-here
```

---

## Step 2: Install openai-agents dependency

```bash
cd backend
uv add openai-agents
```

Expected: `pyproject.toml` updated with `openai-agents` and `openai>=2.26.0`.

---

## Step 3: Run the agent

```bash
cd backend
uv run python ../agent.py
```

Expected startup output:
```
[QDRANT]  Connected - 'book-embeddings' has 75 vector(s)  top_k=3  threshold=None
[AGENT]   BookAgent ready. Ask a question about the book. Type 'quit' to exit.
```

---

## Step 4: Ask a question (US1 — grounded answer)

```
> What is NVIDIA Isaac Sim used for?
```

Expected: The agent calls `retrieve_book_content`, prints an answer grounded in retrieved content, and cites at least one source URL.

---

## Step 5: Ask a follow-up (US2 — context retention)

```
> Can you give me a specific example from the book?
```

Expected: The agent correctly interprets "it" as referring to Isaac Sim from the prior turn and retrieves relevant additional content.

---

## Step 6: Test out-of-scope question (FR-006 — no hallucination)

```
> What is the GDP of France?
```

Expected: The agent responds with something like "I don't have relevant information in the book to answer that question" — it does NOT fabricate an answer.

---

## Step 7: Test configurable retrieval (US3)

```bash
TOP_K=1 SCORE_THRESHOLD=0.5 uv run python ../agent.py
```

Then ask a known-topic question. Confirm only 1 passage is cited.

---

## Step 8: Exit gracefully

Type `quit` at the prompt. Expected: `Goodbye!` printed, exit code 0.

---

## Success Criteria Verification

| SC | How to verify |
|----|--------------|
| SC-001: grounded answer with source URL | Steps 4 — inspect answer for URL citation |
| SC-002: no hallucination for out-of-scope | Step 6 — agent says "no relevant information" |
| SC-003: follow-up context works | Step 5 — agent understands "it" without repetition |
| SC-004: TOP_K + SCORE_THRESHOLD via env | Step 7 — one passage returned |
| SC-005: response under 15 seconds | Time Step 4 with `time` command |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ERROR: Required environment variable 'OPENAI_API_KEY' is not set` | Add key to `backend/.env` |
| `ERROR: Cannot connect to Qdrant` | Verify QDRANT_URL and QDRANT_API_KEY |
| `ERROR: Collection 'book-embeddings' not found` | Re-run `uv run python main.py` |
| `ModuleNotFoundError: agents` | Run `uv add openai-agents` from `backend/` |
| Agent hallucinating (ignoring grounding) | Check system prompt in `build_agent()` is unchanged |
| `UnicodeEncodeError` on Windows | Script includes UTF-8 fix at top |
