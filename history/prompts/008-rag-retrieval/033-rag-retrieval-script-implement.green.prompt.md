---
id: 033
title: RAG Retrieval Script Implement
stage: green
date: 2026-03-10
surface: agent
model: claude-sonnet-4-6
feature: 008-rag-retrieval
branch: 008-rag-retrieval
user: hp
command: /sp.implement
labels: ["green","rag","retrieval","qdrant","cohere","retrieve.py","implementation"]
links:
  spec: specs/008-rag-retrieval/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/retrieve.py
  - specs/008-rag-retrieval/tasks.md
tests:
  - uv run python retrieve.py (5 default queries, 15 results, PASS)
  - uv run python retrieve.py "How do AI agents work?" (exit code 0)
  - TOP_K=1 SCORE_THRESHOLD=0.4 uv run python retrieve.py "..." (1 result filtered correctly)
---

## Prompt

/sp.implement

## Response snapshot

Implemented `backend/retrieve.py` (230 lines) completing all 14 tasks across 6 phases:

**Phase 1 (T001)**: File created with UTF-8 stdout fix, imports (cohere, qdrant_client, dotenv, sys, os), DEFAULT_QUERIES list of 5 book topics.

**Phase 2 (T002–T003)**: `load_config()` validates 4 required keys, parses TOP_K (int, ≥1) and SCORE_THRESHOLD (float 0–1 or None), exits 1 on missing/invalid. `init_qdrant()` connects with QdrantClient, verifies collection exists and non-empty, exits 2/3 on failure.

**Phase 3 (T004–T007)**: `embed_query()` uses `cohere.ClientV2` + `input_type="search_query"` + `.embeddings.float_[0]`. `retrieve()` calls `client.query_points()` with top_k limit and score_threshold. `print_results()` formats rank/score/URL/title/chunk/snippet. `main()` wires all with sys.argv[1:] or DEFAULT_QUERIES.

**Phase 4 (T008–T010)**: `validate_payload()` checks url/title/chunk_index/text, prints WARNING for missing. Integrated into main() loop with counters. `print_validation_report()` prints summary with Overall PASS/FAIL.

**Phase 5 (T011–T012)**: TOP_K and SCORE_THRESHOLD fully wired from load_config() into retrieve() via query_points() parameters.

**Phase 6 (T013–T014)**: Cohere error handling with try/except + re-raise. End-to-end validation confirmed.

**Validation results**:
- Default run: 75 vectors in collection, 5 queries, 15 results, Metadata valid: 15/15, Overall: PASS, exit 0
- Custom query: 1 query, 3 results, PASS, exit 0
- TOP_K=1 SCORE_THRESHOLD=0.4: correctly filtered results (scores all < 0.4 for "prompt engineering"), exit 0

Key fix: Used `response.embeddings.float_` (underscore) as seen in main.py, not `float` (no underscore).

## Outcome

- ✅ Impact: backend/retrieve.py fully functional; all 14 tasks marked [x]; all 3 user stories verified; all 9 FRs implemented; exit codes 0/1/2/3 correct
- 🧪 Tests: 3 manual runs all passed — default queries, custom query, env var override
- 📁 Files: backend/retrieve.py (new), specs/008-rag-retrieval/tasks.md (all [x])
- 🔁 Next prompts: /sp.git.commit_pr or feature complete
- 🧠 Reflection: Book content is about robotics (ROS2, Isaac Sim, VLA) not generic AI topics — default query scores (0.28–0.43) reflect topic mismatch not a pipeline bug; metadata 100% valid confirms Spec-1 ingestion stored complete payloads

## Evaluation notes (flywheel)

- Failure modes observed: none — ran successfully on first attempt
- Graders run and results (PASS/FAIL): ValidationReport Overall PASS; exit code 0 confirmed
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Update DEFAULT_QUERIES to match book topics (ROS2, digital twins, VLA, Isaac Sim) to get higher retrieval scores
