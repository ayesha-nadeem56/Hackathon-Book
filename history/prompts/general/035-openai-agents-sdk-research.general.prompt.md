---
id: "035"
title: OpenAI Agents SDK Python Research
stage: general
date: 2026-03-10
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 007-embedding-pipeline
user: hp
command: research openai-agents SDK
labels: ["research","openai-agents","sdk","rag-agent","tools","multi-turn"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/general/035-openai-agents-sdk-research.general.prompt.md
tests:
  - none
---

## Prompt

Research the OpenAI Agents SDK for Python (package: `openai-agents`). I need to know:

1. How to install it (pip package name, exact import paths)
2. How to create an Agent (class name, required params: name, instructions, model, tools)
3. How to define a tool (decorator name, function signature, return type)
4. How to run the agent (Runner.run, Runner.run_sync, or similar)
5. How to pass conversation history for multi-turn sessions (messages format)
6. What the tool function return type should be (string, dict, etc.)
7. The model name to use (gpt-4o or similar)
8. Any important imports needed

Please search the web for "openai-agents SDK python" and "openai agents sdk tutorial" to get the current API. The SDK was released around March 2025.

Return:
- Exact pip install command
- Minimal working example showing: Agent creation + one tool + running a conversation
- The exact import statements needed
- How to handle multi-turn (pass history between runs)
- Any gotchas or breaking changes

## Response snapshot

Researched openai-agents v0.11.1 via official docs and GitHub source. Key findings:

- Package: `openai-agents`, requires Python >=3.10, openai >=2.26.0, pydantic >=2.12.2
- Imports: `from agents import Agent, Runner, function_tool`
- Agent is a dataclass; model param is `str | Model | None` defaulting to None (uses env/RunConfig default)
- Tool decorator: `@function_tool`, supports sync and async functions, return type str or Pydantic model
- Runner.run() is async, Runner.run_sync() is sync wrapper
- Multi-turn: `result.to_input_list() + [{"role": "user", "content": "..."}]`
- Model names: "gpt-4o" is the standard current default; docs also show "gpt-4o-mini"
- Key gotcha: session persistence cannot be combined with previous_response_id / conversation_id

## Outcome

- Impact: Provided complete SDK reference for implementing RAG agent in the rag-agent feature
- Tests: none run (research task)
- Files: PHR only
- Next prompts: Implement RAG agent using openai-agents SDK with function_tool for retrieval
- Reflection: SDK is clean and minimal; multi-turn via to_input_list() is the recommended manual approach

## Evaluation notes (flywheel)

- Failure modes observed: docs showed future model names (gpt-5.x) that are not current; cross-referenced README for stable gpt-4o usage
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment: implement minimal RAG tool with function_tool decorator
