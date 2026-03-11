---
id: 035
title: RAG Agent Plan
stage: plan
date: 2026-03-10
surface: agent
model: claude-sonnet-4-6
feature: 009-rag-agent
branch: 009-rag-agent
user: hp
command: /sp.plan
labels: ["plan","rag","agent","openai-agents-sdk","qdrant","cohere","grounding"]
links:
  spec: specs/009-rag-agent/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-rag-agent/plan.md
  - specs/009-rag-agent/research.md
  - specs/009-rag-agent/data-model.md
  - specs/009-rag-agent/quickstart.md
  - specs/009-rag-agent/contracts/agent-cli.md
tests:
  - n/a (plan stage)
---

## Prompt

/sp.plan
Spec-3: Agent with Retrieval
Create a single 'agent.py file at the project root
Initialize an agent using the OpenAI Agents SDK
Integrate retrieval by calling the existing Qdrant search logic
Ensure the agent responds using retrieved book content only

## Response snapshot

Generated full implementation plan for `009-rag-agent`. All planning artifacts written:

- **plan.md**: Technical context (openai-agents new dep, gpt-4o, project root placement), Constitution Check (all 5 pass), project structure, implementation checklist (12 items), risks.
- **research.md**: 7 research items resolved via OpenAI Agents SDK deep research — `@function_tool`, `to_input_list()` multi-turn pattern, `Runner.run()` async API, grounding system prompt design, file location decision (project root per user spec), new `openai-agents` dep via `uv add`, REPL loop design.
- **data-model.md**: Config (9 fields, adds OPENAI_API_KEY), RetrievalInput, RetrievedPassage, RetrievalOutput format, ConversationHistory state transitions.
- **contracts/agent-cli.md**: Invocation syntax, env vars table, session flow, exit codes, tool contract (retrieve_book_content input/output), system prompt (grounding enforcement), FR→function mapping.
- **quickstart.md**: 8-step guide (add OPENAI_API_KEY, install dep, run, test grounded Q&A, test follow-up, test out-of-scope, test configurable retrieval, exit), SC verification table, troubleshooting.

Key architectural decisions:
- `agent.py` at project root (per user spec); run via `cd backend && uv run python ../agent.py`
- Retrieval logic inlined from retrieve.py (no sys.path manipulation)
- `to_input_list()` for multi-turn history management
- Grounding enforced via system prompt (only mechanism available without fine-tuning)
- `openai-agents` + `openai>=2.26.0` added to backend/pyproject.toml

## Outcome

- 5 planning artifacts written; all NEEDS CLARIFICATION resolved; Constitution Check passes; ready for /sp.tasks
- n/a (plan stage)
- Files: plan.md, research.md, data-model.md, quickstart.md, contracts/agent-cli.md
- Next: /sp.tasks then /sp.implement

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders: Constitution Check all PASS
- Prompt variant: n/a
- Next experiment: n/a
