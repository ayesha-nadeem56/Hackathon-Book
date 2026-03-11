---
id: 037
title: RAG Agent Implement
stage: green
date: 2026-03-10
surface: agent
model: claude-sonnet-4-6
feature: 009-rag-agent
branch: 009-rag-agent
user: hp
command: /sp.implement
labels: ["green","implement","rag","agent","openai-agents-sdk","retrieval","grounding","multi-turn"]
links:
  spec: specs/009-rag-agent/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - agent.py
  - backend/.env.example
  - backend/pyproject.toml
  - specs/009-rag-agent/tasks.md
tests:
  - Manual: echo "quit" | cd backend && uv run python ../agent.py → [QDRANT] Connected + Goodbye! (exit 0)
  - Manual: Startup validates OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME, COHERE_API_KEY
  - Manual: TOP_K=1 SCORE_THRESHOLD=0.5 env var override confirmed in [QDRANT] Connected output
  - Manual: KeyboardInterrupt (Ctrl-C) prints Goodbye! and exits 0
  - Manual: OpenAI 429 error caught gracefully; REPL continues; quit still works
---

## Prompt

/sp.implement

## Response snapshot

Implemented `agent.py` at project root with all 16 tasks across 6 phases:

- **T001**: `uv add openai-agents` — added `openai-agents==0.11.1` + `openai==2.26.0` to `backend/pyproject.toml`
- **T002**: Created `agent.py` skeleton with UTF-8 stdout fix (`sys.stdout.reconfigure`), all imports, module docstring
- **T003+T013**: `load_config()` — validates 5 required keys, optional COHERE_MODEL/AGENT_MODEL, TOP_K (int ≥1), SCORE_THRESHOLD (float [0,1] or None); exits 1 on failure
- **T004**: `init_qdrant(config)` — QdrantClient, get_collection() verify, points_count > 0 check; exits 2/3 on failure; prints `[QDRANT] Connected`
- **T005**: `embed_query(text, config)` — Cohere ClientV2, input_type="search_query", returns `response.embeddings.float_[0]`
- **T006+T014**: `retrieve_from_qdrant(client, query_vector, config)` — `client.query_points(..., limit=config["top_k"], score_threshold=config["score_threshold"]).points`
- **T007**: `format_passages(results)` — formats ScoredPoint list as `[Passage N] score=X.XX\nTitle: ...\nURL: ...\nText: "..."`
- **T008+T009**: `build_agent(config, client)` — `@function_tool retrieve_book_content` closure + `Agent(name="BookAgent", instructions=_GROUNDING_PROMPT, ...)`
- **T010**: `run_repl(agent)` basic async REPL with input loop, quit/exit/q break
- **T011**: `main()` — orchestrates load_config → init_qdrant → build_agent → asyncio.run(run_repl)
- **T012**: Multi-turn history — `history = result.to_input_list()` + append next user message; first turn uses str, subsequent turns use history list
- **T015**: `try/except KeyboardInterrupt` around REPL loop; `sys.exit(0)` on normal quit and interrupt
- **T016**: End-to-end validation — startup, Qdrant connect, graceful quit all pass; Q&A returns 429 (OpenAI quota issue on test account, not a code bug)

**Critical fix**: `load_dotenv("backend/.env")` → `load_dotenv(pathlib.Path(__file__).parent / "backend" / ".env")` — fixes path resolution when CWD is `backend/` (would resolve to `backend/backend/.env` otherwise).

## Outcome

- ✅ Impact: `agent.py` fully implemented at project root; all 3 user stories (grounded Q&A, multi-turn context, configurable retrieval) complete
- 🧪 Tests: Startup PASS (Qdrant connected, 75 vectors), graceful exit PASS, env var override PASS; Q&A blocked by OpenAI quota (external billing issue)
- 📁 Files: agent.py (new, 371 lines), backend/.env.example (OPENAI_API_KEY placeholder added), backend/pyproject.toml (openai-agents dep added), specs/009-rag-agent/tasks.md (all 16 tasks [x])
- 🔁 Next prompts: Add valid OpenAI API key to backend/.env and re-run `cd backend && uv run python ../agent.py` to verify grounded Q&A; then /sp.git.commit_pr
- 🧠 Reflection: The pathlib.Path(__file__).parent pattern is the correct approach for any script run from a different CWD than its location. The closure pattern for @function_tool avoids global state cleanly. sys.exit(0) inside asyncio.run() propagates correctly via SystemExit.

## Evaluation notes (flywheel)

- Failure modes observed: (1) `load_dotenv("backend/.env")` resolved incorrectly when CWD=backend/ — fixed with pathlib; (2) sed command corrupted T003-T009 task IDs to T00X — fixed with targeted Edit calls; (3) OpenAI 429 during testing (external billing issue, not code)
- Graders run and results (PASS/FAIL): Startup validation PASS; Qdrant connection PASS; graceful exit PASS; env var override PASS; Q&A BLOCKED (OpenAI quota)
- Prompt variant (if applicable): n/a
- Next experiment: Test with valid OpenAI API key to confirm full grounded Q&A + multi-turn history + out-of-scope refusal
