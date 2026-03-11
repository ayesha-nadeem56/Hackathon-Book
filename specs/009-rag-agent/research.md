# Research: AI-Powered Book Q&A Agent

**Feature**: 009-rag-agent | **Date**: 2026-03-10
**Status**: Complete — all decisions resolved

---

## R-001: OpenAI Agents SDK — Package and Core API

**Question**: What is the correct package name, import path, and minimal Agent/Runner API?

**Decision**: `pip install openai-agents` (or `uv add openai-agents`). Core imports: `from agents import Agent, Runner, function_tool`.

**Rationale**: The OpenAI Agents SDK (v0.11+) is the official package. It provides `Agent` (dataclass), `Runner` (async executor), and `@function_tool` (tool decorator). The `swarm` library is a different, older experimental project — do not confuse them.

**Key API**:
```python
from agents import Agent, Runner, function_tool

agent = Agent(
    name="BookAgent",
    instructions="System prompt here",
    model="gpt-4o",
    tools=[my_tool],
)
result = await Runner.run(agent, "user question")
# OR sync:
result = Runner.run_sync(agent, "user question")
print(result.final_output)
```

---

## R-002: Multi-Turn Conversation History

**Question**: How do we maintain conversation context across multiple REPL turns?

**Decision**: Use `result.to_input_list()` + append new user message pattern. Pass the accumulated list as the `input` argument on each subsequent `Runner.run()` call.

**Rationale**: `to_input_list()` is the official SDK pattern that merges all prior messages, tool calls, and responses into a flat list. Works with any model (not just OpenAI). Does not require server-side storage.

**Code pattern**:
```python
# Turn 1
result = await Runner.run(agent, "What is ROS2?")
print(result.final_output)

# Turn 2
history = result.to_input_list()
history.append({"role": "user", "content": "Can you explain more?"})
result = await Runner.run(agent, history)
```

**Alternatives considered**:
- `previous_response_id` — only works with OpenAI Responses API; server stores history (~30 day expiry)
- `session=InMemorySession()` — simpler but cannot be combined with `previous_response_id`; good alternative if to_input_list() is too verbose

---

## R-003: Tool Definition

**Question**: How to define the retrieval function as an agent tool?

**Decision**: Use `@function_tool` decorator. Return `str`. Use Google-style docstring Args section or `Annotated[type, "description"]` for parameter descriptions.

**Code pattern**:
```python
@function_tool
def retrieve_book_content(query: str) -> str:
    """Retrieve relevant passages from the book for a given question.

    Args:
        query: The natural-language search query to find relevant passages.
    """
    # ... embed + qdrant search + format ...
    return formatted_passages_string
```

**Rationale**: `str` return type is simplest and sufficient — the LLM receives the formatted passages as text and can cite them. Pydantic return types add schema complexity without benefit here.

---

## R-004: Grounding System Prompt

**Question**: How do we enforce FR-003 (answer only from retrieved content)?

**Decision**: Include an explicit instruction in the agent's `instructions` field:

```
You are a helpful assistant that answers questions about the book content.
You MUST use the retrieve_book_content tool to find relevant passages for every question.
Only answer based on what the tool returns. If the tool returns no relevant passages,
say "I don't have relevant information in the book to answer that question."
Do not use your training knowledge to answer factual questions about the book.
Always cite the source URLs from the retrieved passages.
```

**Rationale**: LLM system prompts are the only mechanism to constrain answer grounding without fine-tuning. This pattern is industry-standard for RAG agents.

---

## R-005: File Location and Import Strategy

**Question**: User specified "project root" — how do we handle imports from backend/?

**Decision**: Place `agent.py` at the project root. Load `backend/.env` explicitly via `load_dotenv("backend/.env")`. Inline the retrieval primitives (embed_query, retrieve functions) copied from retrieve.py — ~30 lines — rather than importing via sys.path manipulation.

**Rationale**: Inlining keeps agent.py self-contained. The retrieval functions are simple and stable. sys.path manipulation is fragile and confusing. The alternative of placing agent.py in backend/ contradicts the user's explicit instruction.

**Run command**: `cd backend && python -m uv run python ../agent.py` — this way the uv virtual environment (which includes all deps) is activated before running.

---

## R-006: New Dependency — openai-agents

**Question**: What needs to change in backend/pyproject.toml?

**Decision**: Run `uv add openai-agents` from `backend/`. This adds `openai-agents` and its dependency `openai >=2.26.0` to pyproject.toml automatically.

**New env var required**: `OPENAI_API_KEY=sk-...` must be added to `backend/.env`.

**Existing deps unaffected**: `cohere`, `qdrant-client==1.17.0`, `python-dotenv`, `httpx`, `beautifulsoup4`, `tqdm` all remain compatible.

---

## R-007: REPL Loop Design

**Question**: How should the interactive REPL work?

**Decision**: Simple `while True` loop with `asyncio.run()`:
1. Print prompt `"\n> "` and read `input()`
2. Check for `quit`/`exit`/`q` → break
3. Skip empty/whitespace input with warning
4. Call `Runner.run(agent, history)` async
5. Print `result.final_output`
6. Update `history = result.to_input_list()` + append next user message at loop start

**Rationale**: Minimal complexity. `Runner.run_sync()` could work but nesting sync inside asyncio event loops is risky on Windows. Use `asyncio.run()` with an async REPL function.
