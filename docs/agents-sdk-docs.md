### Create Project and Virtual Environment (Bash)

Source: https://openai.github.io/openai-agents-python/quickstart

This snippet demonstrates how to create a new project directory, navigate into it, and set up a Python virtual environment using `venv`. This is a one-time setup for a new project.

```bash
mkdir my_project
cd my_project
python -m venv .venv
```

--------------------------------

### Install OpenAI Agents SDK (Bash)

Source: https://openai.github.io/openai-agents-python/quickstart

This command installs the OpenAI Agents Python SDK using pip. Alternatively, `uv add openai-agents` can be used if using the `uv` package installer. This makes the SDK available within the activated virtual environment.

```bash
pip install openai-agents
```

--------------------------------

### Quick Start: SQLAlchemy Session with Existing Engine

Source: https://openai.github.io/openai-agents-python/sessions/sqlalchemy_session

Shows how to create an `SQLAlchemySession` using an existing SQLAlchemy asynchronous engine (PostgreSQL example). This is useful for integrating with applications that already have a database engine configured. The example includes engine creation, session setup, task execution, and engine disposal.

```python
import asyncio
from agents import Agent, Runner
from agents.extensions.memory import SQLAlchemySession
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    # Create your database engine
    engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

    agent = Agent("Assistant")
    session = SQLAlchemySession(
        "user-456",
        engine=engine,
        create_tables=True
    )

    result = await Runner.run(agent, "Hello", session=session)
    print(result.final_output)

    # Clean up
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())

```

--------------------------------

### Install OpenAI Agents with Voice Dependencies

Source: https://openai.github.io/openai-agents-python/voice/quickstart

Installs the OpenAI Agents SDK along with optional voice-related dependencies. This is a prerequisite for using voice features.

```shell
pip install 'openai-agents[voice]'
```

--------------------------------

### Configure Realtime Runner (Python)

Source: https://openai.github.io/openai-agents-python/realtime/quickstart

Sets up the RealtimeRunner with the starting agent and configuration for model settings, including model name, voice, audio formats, transcription, and turn detection. Dependencies: RealtimeRunner class, agent instance.

```python
runner = RealtimeRunner(
    starting_agent=agent,
    config={
        "model_settings": {
            "model_name": "gpt-realtime",
            "voice": "ash",
            "modalities": ["audio"],
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {"model": "gpt-4o-mini-transcribe"},
            "turn_detection": {"type": "semantic_vad", "interrupt_response": True},
        }
    }
)
```

--------------------------------

### Complete Voice Pipeline Example

Source: https://openai.github.io/openai-agents-python/voice/quickstart

Combines all the previous steps into a single, runnable script. This includes setting up agents, initializing the voice pipeline, generating sample audio input, running the pipeline, and streaming the audio output. It requires `asyncio` to manage the asynchronous operations.

```python
import asyncio
import random

import numpy as np
import sounddevice as sd

from agents import (
    Agent,
    function_tool,
    set_tracing_disabled,
)
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    VoicePipeline,
)
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions


@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    print(f"[debug] get_weather called with city: {city}")
    choices = ["sunny", "cloudy", "rainy", "snowy"]
    return f"The weather in {city} is {random.choice(choices)}."


spanish_agent = Agent(
    name="Spanish",
    handoff_description="A spanish speaking agent.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. Speak in Spanish.",
    ),
    model="gpt-5.2",
)

agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. If the user speaks in Spanish, handoff to the spanish agent.",
    ),
    model="gpt-5.2",
    handoffs=[spanish_agent],
    tools=[get_weather],
)


async def main():
    pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(agent))
    buffer = np.zeros(24000 * 3, dtype=np.int16)
    audio_input = AudioInput(buffer=buffer)

    result = await pipeline.run(audio_input)

    # Create an audio player using `sounddevice`
    player = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
    player.start()

    # Play the audio stream as it comes in
    async for event in result.stream():
        if event.type == "voice_stream_event_audio":
            player.write(event.data)


if __name__ == "__main__":
    asyncio.run(main())

```

--------------------------------

### Realtime Agent and Runner Example in Python

Source: https://openai.github.io/openai-agents-python/realtime/quickstart

This Python code demonstrates how to set up and run a real-time conversational agent. It initializes a RealtimeAgent with specific instructions and a RealtimeRunner with detailed model and audio configurations. The code then processes various events emitted during the agent's session, such as agent start/end, tool usage, and audio events. It relies on the asyncio library for asynchronous operations and the agents.realtime module.

```python
import asyncio
from agents.realtime import RealtimeAgent, RealtimeRunner

def _truncate_str(s: str, max_length: int) -> str:
    if len(s) > max_length:
        return s[:max_length] + "..."
    return s

async def main():
    # Create the agent
    agent = RealtimeAgent(
        name="Assistant",
        instructions="You are a helpful voice assistant. Keep responses brief and conversational.",
    )
    # Set up the runner with configuration
    runner = RealtimeRunner(
        starting_agent=agent,
        config={
            "model_settings": {
                "model_name": "gpt-realtime",
                "voice": "ash",
                "modalities": ["audio"],
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "gpt-4o-mini-transcribe"},
                "turn_detection": {"type": "semantic_vad", "interrupt_response": True},
            }
        },
    )
    # Start the session
    session = await runner.run()

    async with session:
        print("Session started! The agent will stream audio responses in real-time.")
        # Process events
        async for event in session:
            try:
                if event.type == "agent_start":
                    print(f"Agent started: {event.agent.name}")
                elif event.type == "agent_end":
                    print(f"Agent ended: {event.agent.name}")
                elif event.type == "handoff":
                    print(f"Handoff from {event.from_agent.name} to {event.to_agent.name}")
                elif event.type == "tool_start":
                    print(f"Tool started: {event.tool.name}")
                elif event.type == "tool_end":
                    print(f"Tool ended: {event.tool.name}; output: {event.output}")
                elif event.type == "audio_end":
                    print("Audio ended")
                elif event.type == "audio":
                    # Enqueue audio for callback-based playback with metadata
                    # Non-blocking put; queue is unbounded, so drops won’t occur.
                    pass
                elif event.type == "audio_interrupted":
                    print("Audio interrupted")
                    # Begin graceful fade + flush in the audio callback and rebuild jitter buffer.
                elif event.type == "error":
                    print(f"Error: {event.error}")
                elif event.type == "history_updated":
                    pass  # Skip these frequent events
                elif event.type == "history_added":
                    pass  # Skip these frequent events
                elif event.type == "raw_model_event":
                    print(f"Raw model event: {_truncate_str(str(event.data), 200)}")
                else:
                    print(f"Unknown event type: {event.type}")
            except Exception as e:
                print(f"Error processing event: {_truncate_str(str(e), 200)}")

if __name__ == "__main__":
    # Run the session
    asyncio.run(main())

```

--------------------------------

### Activate Virtual Environment (Bash)

Source: https://openai.github.io/openai-agents-python/quickstart

This command activates the Python virtual environment created in the previous step. It needs to be run every time a new terminal session is started to use the project's isolated environment.

```bash
source .venv/bin/activate
```

--------------------------------

### RealtimeRunner run method example (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/runner

Starts and returns a realtime session, enabling bidirectional communication with the model. The example demonstrates initiating a session and sending a message, followed by iterating through events. Requires RealtimeSession.

```Python
    async def run(
        self, *, context: TContext | None = None, model_config: RealtimeModelConfig | None = None
    ) -> RealtimeSession:
        """Start and returns a realtime session.

        Returns:
            RealtimeSession: A session object that allows bidirectional communication with the
            realtime model.

        Example:
            ```python
            runner = RealtimeRunner(agent)
            async with await runner.run() as session:
                await session.send_message("Hello")
                async for event in session:
                    print(event)
            ```
        """
        # Create and return the connection
        session = RealtimeSession(
            model=self._model,
            agent=self._starting_agent,
            context=context,
            model_config=model_config,
            run_config=self._config,
        )

        return session

```

--------------------------------

### Run and Process Realtime Agent Session (Python)

Source: https://openai.github.io/openai-agents-python/realtime/quickstart

Starts a realtime agent session using the configured runner and asynchronously iterates through events. It handles various event types like agent start/end, handoffs, tool usage, audio events, and errors. Includes a helper function for truncating long strings. Dependencies: asyncio, RealtimeRunner, RealtimeAgent.

```python
# Start the session
session = await runner.run()

async with session:
    print("Session started! The agent will stream audio responses in real-time.")
    # Process events
    async for event in session:
        try:
            if event.type == "agent_start":
                print(f"Agent started: {event.agent.name}")
            elif event.type == "agent_end":
                print(f"Agent ended: {event.agent.name}")
            elif event.type == "handoff":
                print(f"Handoff from {event.from_agent.name} to {event.to_agent.name}")
            elif event.type == "tool_start":
                print(f"Tool started: {event.tool.name}")
            elif event.type == "tool_end":
                print(f"Tool ended: {event.tool.name}; output: {event.output}")
            elif event.type == "audio_end":
                print("Audio ended")
            elif event.type == "audio":
                # Enqueue audio for callback-based playback with metadata
                # Non-blocking put; queue is unbounded, so drops won’t occur.
                pass
            elif event.type == "audio_interrupted":
                print("Audio interrupted")
                # Begin graceful fade + flush in the audio callback and rebuild jitter buffer.
            elif event.type == "error":
                print(f"Error: {event.error}")
            elif event.type == "history_updated":
                pass  # Skip these frequent events
            elif event.type == "history_added":
                pass  # Skip these frequent events
            elif event.type == "raw_model_event":
                print(f"Raw model event: {_truncate_str(str(event.data), 200)}")
            else:
                print(f"Unknown event type: {event.type}")
        except Exception as e:
            print(f"Error processing event: {_truncate_str(str(e), 200)}")

def _truncate_str(s: str, max_length: int) -> str:
    if len(s) > max_length:
        return s[:max_length] + "..."
    return s

```

--------------------------------

### Quick Start: Advanced SQLite Session with Agent

Source: https://openai.github.io/openai-agents-python/sessions/advanced_sqlite_session

Demonstrates how to initialize an Agent and an AdvancedSQLiteSession, run a conversation turn, store usage data, and continue the conversation. This example highlights the basic workflow for using the advanced session features.

```python
from agents import Agent, Runner
from agents.extensions.memory import AdvancedSQLiteSession

# Create agent
agent = Agent(
    name="Assistant",
    instructions="Reply very concisely.",
)

# Create an advanced session
session = AdvancedSQLiteSession(
    session_id="conversation_123",
    db_path="conversations.db",
    create_tables=True
)

# First conversation turn
result = await Runner.run(
    agent,
    "What city is the Golden Gate Bridge in?",
    session=session
)
print(result.final_output)  # "San Francisco"

# IMPORTANT: Store usage data
await session.store_run_usage(result)

# Continue conversation
result = await Runner.run(
    agent,
    "What state is it in?",
    session=session
)
print(result.final_output)  # "California"
await session.store_run_usage(result)

```

--------------------------------

### Python Agent Workflow with Handoffs and Guardrails

Source: https://openai.github.io/openai-agents-python/quickstart

This Python code defines a complete agent workflow using the OpenAI Agents library. It includes a guardrail agent to check for homework, specialist agents for math and history, and a triage agent to route queries. The `Runner.run` function executes the workflow, demonstrating handoffs and input guardrails with example queries.

```python
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from agents.exceptions import InputGuardrailTripwireTriggered
from pydantic import BaseModel
import asyncio

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)


async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)

async def main():
    # Example 1: History question
    try:
        result = await Runner.run(triage_agent, "who was the first president of the united states?")
        print(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print("Guardrail blocked this input:", e)

    # Example 2: General/philosophical question
    try:
        result = await Runner.run(triage_agent, "What is the meaning of life?")
        print(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print("Guardrail blocked this input:", e)

if __name__ == "__main__":
    asyncio.run(main())

```

--------------------------------

### Example: Using LitellmModel in an Agent

Source: https://openai.github.io/openai-agents-python/models/litellm

A Python example demonstrating how to use LitellmModel to create an agent that can interact with various AI models. It includes setting up an agent with a model, API key, tools, and running a conversation. The example prompts the user for model and API key if not provided as arguments.

```python
from __future__ import annotations

import asyncio

from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

@function_tool
def get_weather(city: str):
    print(f"[debug] getting weather for {city}")
    return "The weather in {city} is sunny."


async def main(model: str, api_key: str):
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model=LitellmModel(model=model, api_key=api_key),
        tools=[get_weather],
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    # First try to get model/api key from args
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=False)
    parser.add_argument("--api-key", type=str, required=False)
    args = parser.parse_args()

    model = args.model
    if not model:
        model = input("Enter a model name for Litellm: ")

    api_key = args.api_key
    if not api_key:
        api_key = input("Enter an API key for Litellm: ")

    asyncio.run(main(model, api_key))
```

--------------------------------

### Implement Streamable HTTP MCP Server

Source: https://openai.github.io/openai-agents-python/mcp

This example demonstrates setting up a streamable HTTP MCP server using `MCPServerStreamableHttp`. It's suitable for managing network connections directly and running servers within custom infrastructure with low latency. The code includes agent setup, tool usage, and output printing.

```python
import asyncio
import os

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings

async def main() -> None:
    token = os.environ["MCP_SERVER_TOKEN"]
    async with MCPServerStreamableHttp(
        name="Streamable HTTP Python Server",
        params={
            "url": "http://localhost:8000/mcp",
            "headers": {"Authorization": f"Bearer {token}"},
            "timeout": 10,
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    ) as server:
        agent = Agent(
            name="Assistant",
            instructions="Use the MCP tools to answer the questions.",
            mcp_servers=[server],
            model_settings=ModelSettings(tool_choice="required"),
        )

        result = await Runner.run(agent, "Add 7 and 22.")
        print(result.final_output)

asyncio.run(main())

```

--------------------------------

### Quick Start: SQLAlchemy Session from Database URL

Source: https://openai.github.io/openai-agents-python/sessions/sqlalchemy_session

Demonstrates creating an `SQLAlchemySession` using a database URL (SQLite in-memory example). It initializes an agent and runner, then executes a task using the defined session. Includes necessary imports and asynchronous execution.

```python
import asyncio
from agents import Agent, Runner
from agents.extensions.memory import SQLAlchemySession

async def main():
    agent = Agent("Assistant")

    # Create session using database URL
    session = SQLAlchemySession.from_url(
        "user-123",
        url="sqlite+aiosqlite:///:memory:",
        create_tables=True
    )

    result = await Runner.run(agent, "Hello", session=session)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())

```

--------------------------------

### Setup Websocket Connection and Event Listener

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/models/openai_stt

Establishes a websocket connection, starts an event listener task, and waits for session creation events. Handles timeouts and other exceptions during the setup process. Requires a websockets client connection object and queues for state and output.

```python
async def _setup_connection(self, ws: websockets.ClientConnection) -> None:
        self._websocket = ws
        self._listener_task = asyncio.create_task(self._event_listener())

        try:
            event = await _wait_for_event(
                self._state_queue,
                ["session.created", "transcription_session.created"],
                SESSION_CREATION_TIMEOUT,
            )
        except TimeoutError as e:
            wrapped_err = STTWebsocketConnectionError(
                "Timeout waiting for transcription_session.created event"
            )
            await self._output_queue.put(ErrorSentinel(wrapped_err))
            raise wrapped_err from e
        except Exception as e:
            await self._output_queue.put(ErrorSentinel(e))
            raise e

        await self._configure_session()

        try:
            event = await _wait_for_event(
                self._state_queue,
                ["session.updated", "transcription_session.updated"],
                SESSION_UPDATE_TIMEOUT,
            )
            if _debug.DONT_LOG_MODEL_DATA:
                logger.debug("Session updated")
            else:
                logger.debug(f"Session updated: {event}")
        except TimeoutError as e:
            wrapped_err = STTWebsocketConnectionError(
                "Timeout waiting for transcription_session.updated event"
            )
            await self._output_queue.put(ErrorSentinel(wrapped_err))
            raise wrapped_err from e
        except Exception as e:
            await self._output_queue.put(ErrorSentinel(e))
            raise
```

--------------------------------

### RealtimeRunner Initialization and Run Method (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/runner

This Python code defines the RealtimeRunner class, responsible for managing real-time agent sessions. It includes the `__init__` method for setting up the runner with a starting agent, an optional model, and configuration, and the `run` method to initiate a session. The `run` method returns a `RealtimeSession` object for bidirectional communication. The example demonstrates how to instantiate the runner and start a session.

```python
class RealtimeRunner:
    """A `RealtimeRunner` is the equivalent of `Runner` for realtime agents. It automatically
    handles multiple turns by maintaining a persistent connection with the underlying model
    layer.

    The session manages the local history copy, executes tools, runs guardrails and facilitates
    handoffs between agents.

    Since this code runs on your server, it uses WebSockets by default. You can optionally create
    your own custom model layer by implementing the `RealtimeModel` interface.
    """

    def __init__(
        self,
        starting_agent: RealtimeAgent,
        *,
        model: RealtimeModel | None = None,
        config: RealtimeRunConfig | None = None,
    ) -> None:
        """Initialize the realtime runner.

        Args:
            starting_agent: The agent to start the session with.
            context: The context to use for the session.
            model: The model to use. If not provided, will use a default OpenAI realtime model.
            config: Override parameters to use for the entire run.
        """
        self._starting_agent = starting_agent
        self._config = config
        self._model = model or OpenAIRealtimeWebSocketModel()

    async def run(
        self, *, context: TContext | None = None, model_config: RealtimeModelConfig | None = None
    ) -> RealtimeSession:
        """Start and returns a realtime session.

        Returns:
            RealtimeSession: A session object that allows bidirectional communication with the
            realtime model.

        Example:
            ```python
            runner = RealtimeRunner(agent)
            async with await runner.run() as session:
                await session.send_message("Hello")
                async for event in session:
                    print(event)
            ```
        """
        # Create and return the connection
        session = RealtimeSession(
            model=self._model,
            agent=self._starting_agent,
            context=context,
            model_config=model_config,
            run_config=self._config,
        )

        return session

```

--------------------------------

### Initialization: AdvancedSQLiteSession

Source: https://openai.github.io/openai-agents-python/sessions/advanced_sqlite_session

Shows different ways to initialize an AdvancedSQLiteSession, including basic setup, with persistent storage via `db_path`, and with a custom logger instance. All examples ensure the necessary tables are created.

```python
from agents.extensions.memory import AdvancedSQLiteSession

# Basic initialization
session = AdvancedSQLiteSession(
    session_id="my_conversation",
    create_tables=True  # Auto-create advanced tables
)

# With persistent storage
session = AdvancedSQLiteSession(
    session_id="user_123",
    db_path="path/to/conversations.db",
    create_tables=True
)

# With custom logger
import logging
logger = logging.getLogger("my_app")
session = AdvancedSQLiteSession(
    session_id="session_456",
    create_tables=True,
    logger=logger
)

```

--------------------------------

### RealtimeRunner Initialization and Run Method

Source: https://openai.github.io/openai-agents-python/ko/ref/realtime/runner

Initializes the RealtimeRunner with a starting agent and an optional model or configuration. The `run` method starts a real-time session, enabling bidirectional communication with the model. It can be used asynchronously with a context manager.

```python
class RealtimeRunner:
    """A `RealtimeRunner` is the equivalent of `Runner` for realtime agents. It automatically
    handles multiple turns by maintaining a persistent connection with the underlying model
    layer.

    The session manages the local history copy, executes tools, runs guardrails and facilitates
    handoffs between agents.

    Since this code runs on your server, it uses WebSockets by default. You can optionally create
    your own custom model layer by implementing the `RealtimeModel` interface.
    """

    def __init__(
        self,
        starting_agent: RealtimeAgent,
        *,
        model: RealtimeModel | None = None,
        config: RealtimeRunConfig | None = None,
    ) -> None:
        """Initialize the realtime runner.

        Args:
            starting_agent: The agent to start the session with.
            context: The context to use for the session.
            model: The model to use. If not provided, will use a default OpenAI realtime model.
            config: Override parameters to use for the entire run.
        """
        self._starting_agent = starting_agent
        self._config = config
        self._model = model or OpenAIRealtimeWebSocketModel()

    async def run(
        self, *, context: TContext | None = None, model_config: RealtimeModelConfig | None = None
    ) -> RealtimeSession:
        """Start and returns a realtime session.

        Returns:
            RealtimeSession: A session object that allows bidirectional communication with the
            realtime model.

        Example:
            ```python
            runner = RealtimeRunner(agent)
            async with await runner.run() as session:
                await session.send_message("Hello")
                async for event in session:
                    print(event)
            ```
        """
        # Create and return the connection
        session = RealtimeSession(
            model=self._model,
            agent=self._starting_agent,
            context=context,
            model_config=model_config,
            run_config=self._config,
        )

        return session

```

--------------------------------

### Create a Realtime Agent Instance (Python)

Source: https://openai.github.io/openai-agents-python/realtime/quickstart

Initializes a RealtimeAgent with a name and instructions. This agent will act as the AI assistant in the voice conversation. Dependencies: RealtimeAgent class.

```python
agent = RealtimeAgent(
    name="Assistant",
    instructions="You are a helpful voice assistant. Keep your responses conversational and friendly.",
)
```

--------------------------------

### Install OpenAI Agents SDK using pip

Source: https://openai.github.io/openai-agents-python/index

This command installs the OpenAI Agents SDK package. Ensure you have pip installed and accessible in your environment.

```bash
pip install openai-agents

```

--------------------------------

### Create and Use a Custom Span in Python

Source: https://openai.github.io/openai-agents-python/ref/tracing

This Python code example illustrates how to create and utilize a custom span for tracking operations. It shows the use of the `custom_span` context manager to define the start and end of an operation, and how to set output data using `span.set_output()`. The example also includes notes on span nesting, context management, data inclusion, and error handling.

```python
# Creating a custom span
with custom_span("database_query", {
    "operation": "SELECT",
    "table": "users"
}) as span:
    results = await db.query("SELECT * FROM users")
    span.set_output({"count": len(results)})

# Handling errors in spans
with custom_span("risky_operation") as span:
    try:
        result = perform_risky_operation()
    except Exception as e:
        span.set_error({
            "message": str(e),
            "data": {"operation": "risky_operation"}
        })
        raise
```

--------------------------------

### RealtimeRunner Initialization

Source: https://openai.github.io/openai-agents-python/ref/realtime/runner

Initializes the RealtimeRunner, setting up the starting agent, model, and configuration for realtime agent sessions.

```APIDOC
## RealtimeRunner Constructor

### Description
Initializes the `RealtimeRunner` with a starting agent, an optional model, and configuration.

### Method
`__init__`

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

*   **starting_agent** (`RealtimeAgent`) - Required - The agent to start the session with.
*   **model** (`RealtimeModel | None`) - Optional - The model to use. Defaults to `OpenAIRealtimeWebSocketModel` if not provided.
*   **config** (`RealtimeRunConfig | None`) - Optional - Override parameters to use for the entire run.

### Request Example
```python
from agents.realtime.runner import RealtimeRunner
from agents.realtime.agent import RealtimeAgent # Assuming RealtimeAgent is defined elsewhere

# Assuming agent is an instance of RealtimeAgent
# runner = RealtimeRunner(starting_agent=agent)
```

### Response
None (Constructor does not return a value)

```

--------------------------------

### Quick Start: Using SQLiteSession for Agent Conversation History

Source: https://openai.github.io/openai-agents-python/sessions

Demonstrates how to initialize an Agent and Runner with a SQLiteSession to maintain conversation history across multiple turns. The session automatically stores and retrieves context, allowing the agent to remember previous interactions without manual intervention. This example shows both asynchronous and synchronous runner usage.

```python
from agents import Agent, Runner, SQLiteSession

# Create agent
agent = Agent(
    name="Assistant",
    instructions="Reply very concisely.",
)

# Create a session instance with a session ID
session = SQLiteSession("conversation_123")

# First turn
result = await Runner.run(
    agent,
    "What city is the Golden Gate Bridge in?",
    session=session
)
print(result.final_output)  # "San Francisco"

# Second turn - agent automatically remembers previous context
result = await Runner.run(
    agent,
    "What state is it in?",
    session=session
)
print(result.final_output)  # "California"

# Also works with synchronous runner
result = Runner.run_sync(
    agent,
    "What's the population?",
    session=session
)
print(result.final_output)  # "Approximately 39 million"

```

--------------------------------

### Create a Basic Agent (Python)

Source: https://openai.github.io/openai-agents-python/quickstart

This Python code defines a simple agent named 'Math Tutor' with specific instructions. It imports the `Agent` class from the `agents` library and initializes an agent instance.

```python
from agents import Agent

agent = Agent(
    name="Math Tutor",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)
```

--------------------------------

### Trace Usage Example

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing

Provides a basic example of how to use the `Trace` context manager for grouping operations.

```APIDOC
## Trace Usage Example

Provides a basic example of how to use the `Trace` context manager for grouping operations.

### Example

```python
# Basic trace usage
with trace("Order Processing") as t:
    validation_result = await Runner.run(validator, order_data)
    if validation_result.approved:
        await Runner.run(processor, order_data)
```
```

--------------------------------

### Import Realtime Agent Components (Python)

Source: https://openai.github.io/openai-agents-python/realtime/quickstart

Imports necessary classes (RealtimeAgent, RealtimeRunner) from the openai.agents.realtime module for creating and managing realtime agents. Requires Python 3.9+.

```python
import asyncio
from agents.realtime import RealtimeAgent, RealtimeRunner
```

--------------------------------

### Install SQLAlchemy Sessions for OpenAI Agents

Source: https://openai.github.io/openai-agents-python/sessions/sqlalchemy_session

Installs the 'openai-agents' library with the 'sqlalchemy' extra for session storage capabilities. This is a prerequisite for using SQLAlchemy-based sessions.

```bash
pip install openai-agents[sqlalchemy]

```

--------------------------------

### Run Realtime Session

Source: https://openai.github.io/openai-agents-python/ref/realtime/runner

Starts and returns a RealtimeSession object, enabling bidirectional communication with the realtime model. This method is crucial for initiating and managing the interaction loop with the agent. An example demonstrates how to use the session for sending messages and receiving events.

```python
async def run(
        self, *, context: TContext | None = None, model_config: RealtimeModelConfig | None = None
    ) -> RealtimeSession:
        """Start and returns a realtime session.

        Returns:
            RealtimeSession: A session object that allows bidirectional communication with the
            realtime model.

        Example:
            ```python
            runner = RealtimeRunner(agent)
            async with await runner.run() as session:
                await session.send_message("Hello")
                async for event in session:
                    print(event)
            ```
        """
        session = RealtimeSession(
            model=self._model,
            agent=self._starting_agent,
            context=context,
            model_config=model_config,
            run_config=self._config,
        )

        return session

```

--------------------------------

### Basic Agent Execution with OpenAI Agents SDK (Python)

Source: https://openai.github.io/openai-agents-python/index

This Python code demonstrates a 'Hello World' example using the OpenAI Agents SDK. It initializes an Agent with specific instructions and then uses the Runner to execute a task synchronously, printing the final output. This requires the OPENAI_API_KEY environment variable to be set.

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.

```

--------------------------------

### Run Agent Orchestration (Python)

Source: https://openai.github.io/openai-agents-python/quickstart

This Python code demonstrates how to run an agent orchestration using the `Runner` class. It shows an asynchronous `main` function that executes the 'Triage Agent' with a user query and prints the final output.

```python
from agents import Runner

async def main():
    result = await Runner.run(triage_agent, "who was the first president of the united states?")
    print(result.final_output)
```

--------------------------------

### RealtimeRunner Initialization (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/runner

Initializes the RealtimeRunner, setting up the starting agent and optionally a custom model or run configuration. If no model is provided, it defaults to an OpenAIRealtimeWebSocketModel. Dependencies include RealtimeAgent, RealtimeModel, and RealtimeRunConfig.

```Python
class RealtimeRunner:
    """A `RealtimeRunner` is the equivalent of `Runner` for realtime agents. It automatically
    handles multiple turns by maintaining a persistent connection with the underlying model
    layer.

    The session manages the local history copy, executes tools, runs guardrails and facilitates
    handoffs between agents.

    Since this code runs on your server, it uses WebSockets by default. You can optionally create
    your own custom model layer by implementing the `RealtimeModel` interface.
    """

    def __init__(
        self,
        starting_agent: RealtimeAgent,
        *,
        model: RealtimeModel | None = None,
        config: RealtimeRunConfig | None = None,
    ) -> None:
        """Initialize the realtime runner.

        Args:
            starting_agent: The agent to start the session with.
            context: The context to use for the session.
            model: The model to use. If not provided, will use a default OpenAI realtime model.
            config: Override parameters to use for the entire run.
        """
        self._starting_agent = starting_agent
        self._config = config
        self._model = model or OpenAIRealtimeWebSocketModel()

```

--------------------------------

### Implement Trace Start Method in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/traces

Implements the abstract method 'start' for a trace, which initiates the trace and optionally marks it as the current trace in the execution context. This method must be called before adding any spans and ensures thread-safety when marking as current.

```python
@abc.abstractmethod
def start(self, mark_as_current: bool = False):
    """Start the trace and optionally mark it as the current trace.

    Args:
        mark_as_current: If true, marks this trace as the current trace
            in the execution context.

    Notes:
        - Must be called before any spans can be added
        - Only one trace can be current at a time
        - Thread-safe when using mark_as_current
    """
    pass

```

--------------------------------

### Get Global Trace Provider - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/setup

Retrieves the currently set global trace provider. If no provider has been set, it raises a `RuntimeError`. This function is used to access the active tracing configuration.

```python
def get_trace_provider() -> TraceProvider:
    """Get the global trace provider used by tracing utilities."""
    if GLOBAL_TRACE_PROVIDER is None:
        raise RuntimeError("Trace provider not set")
    return GLOBAL_TRACE_PROVIDER
```

--------------------------------

### MCPServerStdio.name property

Source: https://openai.github.io/openai-agents-python/ko/ref/mcp/server

Gets a readable name for the MCP server instance. This property provides a string representation that can be used to identify the server, often derived from the command used to start it.

```APIDOC
## MCPServerStdio.name

### Description
A readable name for the server.

### Method
GET

### Endpoint
N/A (Property)

### Parameters
None

### Request Example
None

### Response
#### Success Response (200)
- **name** (str) - The readable name of the server.

#### Response Example
```json
{
  "name": "stdio: my_server_command"
}
```
```

--------------------------------

### Set OpenAI API Key (Bash)

Source: https://openai.github.io/openai-agents-python/quickstart

This command sets the OpenAI API key as an environment variable. Replace `sk-...` with your actual API key. This is crucial for authenticating with the OpenAI API.

```bash
export OPENAI_API_KEY=sk-...
```

--------------------------------

### Define Multiple Agents with Handoff Descriptions (Python)

Source: https://openai.github.io/openai-agents-python/quickstart

This Python snippet shows how to define multiple agents, including 'History Tutor' and 'Math Tutor', each with a `handoff_description`. This description provides context for routing decisions when agents need to hand off tasks.

```python
from agents import Agent

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)
```

--------------------------------

### Pass OpenAI API Key Directly to Session

Source: https://openai.github.io/openai-agents-python/realtime/quickstart

This Python code snippet shows an alternative method for authenticating with the OpenAI API by passing the API key directly when creating a session. This approach can be useful for temporary configurations or when environment variables are not accessible. It is part of the `RealtimeRunner.run()` method.

```python
session = await runner.run(model_config={"api_key": "your-api-key"})

```

--------------------------------

### Run Voice Pipeline and Stream Audio Output

Source: https://openai.github.io/openai-agents-python/voice/quickstart

Executes the voice pipeline with sample audio input (silence in this case) and streams the resulting audio output. It uses `sounddevice` to play the generated speech in real-time.

```python
import numpy as np
import sounddevice as sd
from agents.voice import AudioInput

# For simplicity, we'll just create 3 seconds of silence
# In reality, you'd get microphone data
buffer = np.zeros(24000 * 3, dtype=np.int16)
audio_input = AudioInput(buffer=buffer)

result = await pipeline.run(audio_input)

# Create an audio player using `sounddevice`
player = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
player.start()

# Play the audio stream as it comes in
async for event in result.stream():
    if event.type == "voice_stream_event_audio":
        player.write(event.data)

```

--------------------------------

### Initialize LitellmModel in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/litellm

Initializes the LitellmModel with a specified model name and optional base URL and API key. This setup is crucial for directing requests to the correct LiteLLM-compatible model and endpoint.

```python
class LitellmModel(Model):
    """This class enables using any model via LiteLLM. LiteLLM allows you to acess OpenAPI,
    Anthropic, Gemini, Mistral, and many other models.
    See supported models here: [litellm models](https://docs.litellm.ai/docs/providers).
    """

    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
```

--------------------------------

### Install LiteLLM dependency for OpenAI Agents SDK

Source: https://openai.github.io/openai-agents-python/models/litellm

Installs the optional 'litellm' dependency group for the OpenAI Agents SDK. This enables the use of LitellmModel for accessing various AI models.

```bash
pip install "openai-agents[litellm]"
```

--------------------------------

### Install openai-agents with Visualization Dependencies

Source: https://openai.github.io/openai-agents-python/visualization

Installs the `openai-agents` library with the optional `viz` dependency group, which is required for agent visualization. This command uses pip, the standard Python package installer.

```bash
pip install "openai-agents[viz]"
```

--------------------------------

### Start a Turn in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/result

Initiates a new turn in the voice pipeline processing. This method sets up tracing, marks the start of processing, and signals the beginning of a turn via a VoiceStreamEvent.

```python
async def _start_turn(self):
        if self._started_processing_turn:
            return

        self._tracing_span = speech_group_span()
        self._tracing_span.start()
        self._started_processing_turn = True
        self._first_byte_received = False
        self._generation_start_time = time_iso()
        await self._queue.put(VoiceStreamEventLifecycle(event="turn_started"))
```

--------------------------------

### Complete Session Memory Example

Source: https://openai.github.io/openai-agents-python/sessions

A comprehensive example showcasing session memory in action. It demonstrates how an agent, using a persistent SQLite session, remembers previous messages across multiple turns of a conversation, providing contextually relevant responses.

```python
import asyncio
from agents import Agent, Runner, SQLiteSession


async def main():
    # Create an agent
    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely.",
    )

    # Create a session instance that will persist across runs
    session = SQLiteSession("conversation_123", "conversation_history.db")

    print("=== Sessions Example ===")
    print("The agent will remember previous messages automatically.\n")

    # First turn
    print("First turn:")
    print("User: What city is the Golden Gate Bridge in?")
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session=session
    )
    print(f"Assistant: {result.final_output}")
    print()

    # Second turn - the agent will remember the previous conversation
    print("Second turn:")
    print("User: What state is it in?")
    result = await Runner.run(
        agent,
        "What state is it in?",
        session=session
    )
    print(f"Assistant: {result.final_output}")
    print()

    # Third turn - continuing the conversation
    print("Third turn:")
    print("User: What's the population of that state?")
    result = await Runner.run(
        agent,
        "What's the population of that state?",
        session=session
    )
    print(f"Assistant: {result.final_output}")
    print()

    print("=== Conversation Complete ===")
    print("Notice how the agent remembered the context from previous turns!")
    print("Sessions automatically handles conversation history.")


if __name__ == "__main__":
    asyncio.run(main())

```

--------------------------------

### Configure Realtime Audio Transcription in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/config

Defines the configuration for transcribing audio in realtime sessions. It specifies the language, the transcription model to use (e.g., 'gpt-4o-transcribe', 'whisper-1'), and an optional prompt to guide the transcription process. This configuration is part of the broader realtime agent setup.

```python
class RealtimeInputAudioTranscriptionConfig(TypedDict):
    """Configuration for audio transcription in realtime sessions."""

    language: NotRequired[str]
    """The language code for transcription."""

    model: NotRequired[Literal["gpt-4o-transcribe", "gpt-4o-mini-transcribe", "whisper-1"] | str]
    """The transcription model to use."""

    prompt: NotRequired[str]
    """An optional prompt to guide transcription."""

```

--------------------------------

### Start Trace

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing

Starts the trace. Optionally, it can be marked as the current trace in the execution context. This method must be called before any spans can be added to the trace.

```APIDOC
## POST /start

### Description
Start the trace and optionally mark it as the current trace.

### Method
POST

### Endpoint
/start

### Parameters
#### Query Parameters
- **mark_as_current** (bool) - Optional - If true, marks this trace as the current trace in the execution context. Defaults to `False`.

### Response
#### Success Response (200)
- **status** (str) - Indicates the success of the operation. Example: "Trace started successfully."

#### Response Example
{
  "status": "Trace started successfully."
}

### Notes
- Must be called before any spans can be added.
- Only one trace can be current at a time.
- Thread-safe when using `mark_as_current`.
```

--------------------------------

### Initialize Voice Pipeline

Source: https://openai.github.io/openai-agents-python/voice/quickstart

Initializes a `VoicePipeline` using a `SingleAgentVoiceWorkflow` and the previously defined agent. This sets up the core structure for processing voice input and generating responses.

```python
from agents.voice import SingleAgentVoiceWorkflow, VoicePipeline

pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(agent))
```

--------------------------------

### Implement Output Guardrail with Agent

Source: https://openai.github.io/openai-agents-python/guardrails

This example shows how to create an output guardrail that inspects the agent's response. It defines Pydantic models for message and math-related outputs. The guardrail agent checks if the output contains math, and the guardrail function uses this to determine if the tripwire should be triggered.

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)
class MessageOutput(BaseModel): 
    response: str

class MathOutput(BaseModel): 
    reasoning: str
    is_math: bool

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the output includes any math.",
    output_type=MathOutput,
)

@output_guardrail
async def math_guardrail(  
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math,
    )

agent = Agent( 
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    output_guardrails=[math_guardrail],
    output_type=MessageOutput,
)

async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except OutputGuardrailTripwireTriggered:
        print("Math output guardrail tripped")

```

--------------------------------

### Install openai-agents with encryption extra

Source: https://openai.github.io/openai-agents-python/sessions/encrypted_session

Installs the openai-agents library with the necessary 'encrypt' extra for using encrypted sessions. This is the first step before utilizing the encryption features.

```bash
pip install openai-agents[encrypt]
```

--------------------------------

### Initialize OpenAIResponsesModel

Source: https://openai.github.io/openai-agents-python/ja/ref/models/openai_responses

Initializes the OpenAIResponsesModel with a specified model, an asynchronous OpenAI client, and optional model explicitness. This setup is crucial for subsequent API interactions.

```python
class OpenAIResponsesModel(Model):
    """
    Implementation of `Model` that uses the OpenAI Responses API.
    """

    def __init(
        self,
        model: str | ChatModel,
        openai_client: AsyncOpenAI,
        *,
        model_is_explicit: bool = True,
    ) -> None:
        self.model = model
        self._model_is_explicit = model_is_explicit
        self._client = openai_client
```

--------------------------------

### SpanImpl Start and Finish Methods (Python)

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/spans

Provides methods to start and finish a span. The `start` method records the start time, notifies the processor, and optionally marks the span as current. The `finish` method records the end time, notifies the processor, and optionally resets the current span context.

```python
    def start(self, mark_as_current: bool = False):
        if self.started_at is not None:
            logger.warning("Span already started")
            return

        self._started_at = util.time_iso()
        self._processor.on_span_start(self)
        if mark_as_current:
            self._prev_span_token = Scope.set_current_span(self)

    def finish(self, reset_current: bool = False) -> None:
        if self.ended_at is not None:
            logger.warning("Span already finished")
            return

        self._ended_at = util.time_iso()
        self._processor.on_span_end(self)
        if reset_current and self._prev_span_token is not None:
            Scope.reset_current_span(self._prev_span_token)
            self._prev_span_token = None
```

--------------------------------

### Implement Trace Start Method

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/traces

Abstract method to start a trace. It can optionally mark the trace as the current one in the execution context. This must be called before adding spans and ensures thread-safety when `mark_as_current` is used.

```python
@abc.abstractmethod
def start(self, mark_as_current: bool = False):
    """Start the trace and optionally mark it as the current trace.

    Args:
        mark_as_current: If true, marks this trace as the current trace
            in the execution context.

    Notes:
        - Must be called before any spans can be added
        - Only one trace can be current at a time
        - Thread-safe when using mark_as_current
    """
    pass
```

--------------------------------

### Implement Tool Guardrails for Input and Output

Source: https://openai.github.io/openai-agents-python/guardrails

This example demonstrates how to implement both input and output guardrails for a tool. The `block_secrets` input guardrail checks tool arguments for secrets, while the `redact_output` output guardrail checks the tool's return value for sensitive data. These guardrails are applied to the `classify_text` function tool.

```python
import json
from agents import (
    Agent,
    Runner,
    ToolGuardrailFunctionOutput,
    function_tool,
    tool_input_guardrail,
    tool_output_guardrail,
)

@tool_input_guardrail
def block_secrets(data):
    args = json.loads(data.context.tool_arguments or "{}")
    if "sk-" in json.dumps(args):
        return ToolGuardrailFunctionOutput.reject_content(
            "Remove secrets before calling this tool."
        )
    return ToolGuardrailFunctionOutput.allow()


@tool_output_guardrail
def redact_output(data):
    text = str(data.output or "")
    if "sk-" in text:
        return ToolGuardrailFunctionOutput.reject_content("Output contained sensitive data.")
    return ToolGuardrailFunctionOutput.allow()


@function_tool(
    tool_input_guardrails=[block_secrets],
    tool_output_guardrails=[redact_output],
)
def classify_text(text: str) -> str:
    """Classify text for internal routing."""
    return f"length:{len(text)}"


agent = Agent(name="Classifier", tools=[classify_text])
result = Runner.run_sync(agent, "hello world")
print(result.final_output)

```

--------------------------------

### Basic Agent Handoff Setup - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/handoffs

Sets up a basic handoff where the primary focus is on the target agent and enabling the handoff. Optional parameters for tool naming and descriptions are available but not strictly required for initialization.

```python
def handoff(
    agent: Agent[TContext],
    *,
    tool_name_override: str | None = None,
    tool_description_override: str | None = None,
    input_filter: Callable[
        [HandoffInputData], HandoffInputData
    ]
    | None = None,
    nest_handoff_history: bool | None = None,
    is_enabled: bool
    | Callable[
        [RunContextWrapper[Any], Agent[Any]],
        MaybeAwaitable[bool],
    ] = True,
) -> Handoff[TContext, Agent[TContext]]


```

--------------------------------

### Agent Span Creation

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing

This endpoint (function) allows for the creation of a new agent span. Spans are used for tracing and monitoring agent activities. The span is not automatically started; users must explicitly start and finish it using a `with` statement or manual calls to `start()` and `finish()`.

```APIDOC
## agent_span

### Description
Create a new agent span. The span will not be started automatically, you should either do `with agent_span() ...` or call `span.start()` + `span.finish()` manually.

### Method
N/A (This is a Python function, not a direct HTTP endpoint)

### Endpoint
N/A

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
* **name** (str) - Required - The name of the agent.
* **handoffs** (list[str] | None) - Optional - Optional list of agent names to which this agent could hand off control. Defaults to None.
* **tools** (list[str] | None) - Optional - Optional list of tool names available to this agent. Defaults to None.
* **output_type** (str | None) - Optional - Optional name of the output type produced by the agent. Defaults to None.
* **span_id** (str | None) - Optional - The ID of the span. If not provided, we will generate an ID. We recommend using `util.gen_span_id()` to generate a span ID, to guarantee that IDs are correctly formatted. Defaults to None.
* **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, we will automatically use the current trace/span as the parent. Defaults to None.
* **disabled** (bool) - Optional - If True, we will return a Span but the Span will not be recorded. Defaults to False.

### Request Example
```python
from agents.tracing import agent_span

# Example using 'with' statement
with agent_span(name="MyAgent", tools=["search"]):
    # Agent logic here
    pass

# Example with manual start/finish
span = agent_span(name="AnotherAgent")
try:
    span.start()
    # Agent logic here
finally:
    span.finish()
```

### Response
#### Success Response
* **Span[AgentSpanData]** - The newly created agent span.
```

--------------------------------

### Initialize AsyncOpenAI Client in Python

Source: https://openai.github.io/openai-agents-python/ko/ref/models/openai_chatcompletions

This Python function provides a simple way to get an instance of the `AsyncOpenAI` client. It initializes the client only if it hasn't been already, ensuring a single instance is reused.

```python
def _get_client(self) -> AsyncOpenAI:
    if self._client is None:
        self._client = AsyncOpenAI()
    return self._client
```

--------------------------------

### Quick start: Encrypted session with SQLAlchemy

Source: https://openai.github.io/openai-agents-python/sessions/encrypted_session

Demonstrates how to set up and use an EncryptedSession with a SQLAlchemy session backend. It shows the creation of an underlying session, wrapping it with EncryptedSession, and then using it with the Runner.

```python
import asyncio
from agents import Agent, Runner
from agents.extensions.memory import EncryptedSession, SQLAlchemySession

async def main():
    agent = Agent("Assistant")

    # Create underlying session
    underlying_session = SQLAlchemySession.from_url(
        "user-123",
        url="sqlite+aiosqlite:///:memory:",
        create_tables=True
    )

    # Wrap with encryption
    session = EncryptedSession(
        session_id="user-123",
        underlying_session=underlying_session,
        encryption_key="your-secret-key-here",
        ttl=600  # 10 minutes
    )

    result = await Runner.run(agent, "Hello", session=session)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

--------------------------------

### Trace Start Event

Source: https://openai.github.io/openai-agents-python/ref/tracing

Callback executed when a new trace begins. It is called synchronously and should return quickly.

```APIDOC
## POST /trace/start

### Description
Called when a new trace begins execution. Contains workflow name and metadata.

### Method
POST

### Endpoint
/trace/start

### Parameters
#### Request Body
- **trace** (Trace) - Required - The trace that started. Contains workflow name and metadata.

### Request Example
```json
{
  "trace": {
    "workflow_name": "example_workflow",
    "metadata": {}
  }
}
```

### Response
#### Success Response (200)
- **status** (string) - Indicates success.

#### Response Example
```json
{
  "status": "ok"
}
```
```

--------------------------------

### OpenAI Provider Initialization (__init__)

Source: https://openai.github.io/openai-agents-python/ja/ref/models/multi_provider

Initializes a new OpenAI provider with various configuration options for API keys, base URLs, clients, organizations, projects, and response usage.

```APIDOC
## POST /openai/provider/initialize

### Description
Initializes a new OpenAI provider. You can configure API keys, base URLs, and other settings.

### Method
POST

### Endpoint
/openai/provider/initialize

### Parameters
#### Request Body
- **provider_map** (MultiProviderMap | None) - Optional - A MultiProviderMap that maps prefixes to ModelProviders. If not provided, a default mapping will be used.
- **openai_api_key** (str | None) - Optional - The API key to use for the OpenAI provider. If not provided, the default API key will be used.
- **openai_base_url** (str | None) - Optional - The base URL to use for the OpenAI provider. If not provided, the default base URL will be used.
- **openai_client** (AsyncOpenAI | None) - Optional - An optional OpenAI client to use. If not provided, a new OpenAI client will be created using the api_key and base_url.
- **openai_organization** (str | None) - Optional - The organization to use for the OpenAI provider.
- **openai_project** (str | None) - Optional - The project to use for the OpenAI provider.
- **openai_use_responses** (bool | None) - Optional - Whether to use the OpenAI responses API.

### Request Example
```json
{
  "openai_api_key": "your_api_key",
  "openai_base_url": "https://api.openai.com/v1",
  "openai_organization": "your_organization_id"
}
```

### Response
#### Success Response (200)
- **message** (str) - Confirmation message indicating successful initialization.

#### Response Example
```json
{
  "message": "OpenAI provider initialized successfully."
}
```
```

--------------------------------

### Set OpenAI API Key using Environment Variable

Source: https://openai.github.io/openai-agents-python/realtime/quickstart

This command demonstrates how to set the OpenAI API key using an environment variable. This is a common practice for securely managing API keys, especially in development and production environments. The `export` command is used in Unix-like shells (Linux, macOS) to set the variable for the current session.

```bash
export OPENAI_API_KEY="your-api-key-here"

```

--------------------------------

### RealtimeRunner Constructor

Source: https://openai.github.io/openai-agents-python/ko/ref/realtime/runner

The constructor for RealtimeRunner initializes the runner with a starting agent and optional model and configuration parameters. It defaults to using an OpenAI realtime WebSocket model if no model is provided.

```python
def __init__(
    self,
    starting_agent: RealtimeAgent,
    *,
    model: RealtimeModel | None = None,
    config: RealtimeRunConfig | None = None,
) -> None:
    """Initialize the realtime runner.

    Args:
        starting_agent: The agent to start the session with.
        context: The context to use for the session.
        model: The model to use. If not provided, will use a default OpenAI realtime model.
        config: Override parameters to use for the entire run.
    """
    self._starting_agent = starting_agent
    self._config = config
    self._model = model or OpenAIRealtimeWebSocketModel()

```

--------------------------------

### Branch Workflow Example: Create, Switch, Continue

Source: https://openai.github.io/openai-agents-python/sessions/advanced_sqlite_session

Illustrates a typical branch workflow: initiating a conversation, storing run usage, creating a new branch from a specific turn, continuing the conversation in the new branch, and switching back to the main branch. Requires `Runner` and `session` objects.

```python
# Original conversation
result = await Runner.run(agent, "What's the capital of France?", session=session)
await session.store_run_usage(result)

result = await Runner.run(agent, "What's the weather like there?", session=session)
await session.store_run_usage(result)

# Create branch from turn 2 (weather question)
branch_id = await session.create_branch_from_turn(2, "weather_focus")

# Continue in new branch with different question
result = await Runner.run(
    agent, 
    "What are the main tourist attractions in Paris?", 
    session=session
)
await session.store_run_usage(result)

# Switch back to main branch
await session.switch_to_branch("main")

# Continue original conversation
result = await Runner.run(
    agent, 
    "How expensive is it to visit?", 
    session=session
)
await session.store_run_usage(result)
```

--------------------------------

### Start and Finish Abstract Methods for Spans in Python

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing

Abstract methods for controlling the lifecycle of a span. The `start` method initiates the span, with an option to mark it as the current span. The `finish` method concludes the span's execution, with an option to reset the current span.

```python
import abc
from typing import Any, Dict, Optional, TypeVar

from typing_extensions import TypeVarTuple

TSpanData = TypeVar("TSpanData")
SpanError = Dict[str, Any]


class Span(abc.ABC):
    @abc.abstractmethod
    def start(self, mark_as_current: bool = False):
        """
        Start the span.

        Args:
            mark_as_current: If true, the span will be marked as the current span.
        """
        pass

    @abc.abstractmethod
    def finish(self, reset_current: bool = False) -> None:
        """
        Finish the span.

        Args:
            reset_current: If true, the span will be reset as the current span.
        """
        pass
```

--------------------------------

### Create stdio MCP Server for Local Subprocesses

Source: https://openai.github.io/openai-agents-python/mcp

This code example shows how to create an MCP server for local subprocesses using `MCPServerStdio`. The SDK manages process spawning and pipe handling. This is useful for quick proofs of concept or when the server exposes a command-line interface.

```python
from pathlib import Path
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

current_dir = Path(__file__).parent
samples_dir = current_dir / "sample_files"

async with MCPServerStdio(
    name="Filesystem Server via npx",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(samples_dir)],
    },
) as server:
    agent = Agent(
        name="Assistant",
        instructions="Use the files in the sample directory to answer questions.",
        mcp_servers=[server],
    )
    result = await Runner.run(agent, "List the files available to you.")
    print(result.final_output)


```

--------------------------------

### Abstract Span Methods

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing

Defines the abstract methods for starting and finishing a span. The `start` method initiates the span's execution, with an option to mark it as the current span. The `finish` method concludes the span's execution, also with an option to reset the current span.

```python
@abc.abstractmethod
def start(self, mark_as_current: bool = False):
    """
    Start the span.

    Args:
        mark_as_current: If true, the span will be marked as the current span.
    """
    pass

@abc.abstractmethod
def finish(self, reset_current: bool = False) -> None:
    """
    Finish the span.

    Args:
        reset_current: If true, the span will be reset as the current span.
    """
    pass
```

--------------------------------

### OpenAIResponsesModel Initialization and Response Fetching (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/models/openai_responses

Demonstrates the initialization of the OpenAIResponsesModel and the core logic for fetching responses from the OpenAI API. It includes handling of model settings, tools, output schemas, and optional tracing information. Dependencies include the `AsyncOpenAI` client and various agent-related models and utilities.

```python
class OpenAIResponsesModel(Model):
    """
    Implementation of `Model` that uses the OpenAI Responses API.
    """

    def __init(
        self,
        model: str | ChatModel,
        openai_client: AsyncOpenAI,
        *,
        model_is_explicit: bool = True,
    ) -> None:
        self.model = model
        self._model_is_explicit = model_is_explicit
        self._client = openai_client

    def _non_null_or_omit(self, value: Any) -> Any:
        return value if value is not None else omit

    async def get_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: list[Handoff],
        tracing: ModelTracing,
        previous_response_id: str | None = None,
        conversation_id: str | None = None,
        prompt: ResponsePromptParam | None = None,
    ) -> ModelResponse:
        with response_span(disabled=tracing.is_disabled()) as span_response:
            try:
                response = await self._fetch_response(
                    system_instructions,
                    input,
                    model_settings,
                    tools,
                    output_schema,
                    handoffs,
                    previous_response_id=previous_response_id,
                    conversation_id=conversation_id,
                    stream=False,
                    prompt=prompt,
                )

                if _debug.DONT_LOG_MODEL_DATA:
                    logger.debug("LLM responded")
                else:
                    logger.debug(
                        "LLM resp:\n"
                        f"""{                       json.dumps(
                            [x.model_dump() for x in response.output],
                            indent=2,
                            ensure_ascii=False,
                        )
                    }"""
                    )

                usage = (
                    Usage(
                        requests=1,
                        input_tokens=response.usage.input_tokens,
                        output_tokens=response.usage.output_tokens,
                        total_tokens=response.usage.total_tokens,
                        input_tokens_details=response.usage.input_tokens_details,
                        output_tokens_details=response.usage.output_tokens_details,
                    )
                    if response.usage
                    else Usage()
                )

                if tracing.include_data():
                    span_response.span_data.response = response
                    span_response.span_data.input = input
            except Exception as e:
                span_response.set_error(
                    SpanError(
                        message="Error getting response",
                        data={
                            "error": str(e) if tracing.include_data() else e.__class__.__name__,
                        },
                    )
                )
                request_id = e.request_id if isinstance(e, APIStatusError) else None
                logger.error(f"Error getting response: {e}. (request_id: {request_id})")
                raise

        return ModelResponse(
            output=response.output,
            usage=usage,

```

--------------------------------

### Define Agents and Tools for Voice Interaction

Source: https://openai.github.io/openai-agents-python/voice/quickstart

Sets up custom agents, including a Spanish-speaking agent and a primary assistant agent, with a weather-fetching tool. The assistant agent is configured to handoff to the Spanish agent if the user speaks Spanish. This defines the conversational logic for the voice pipeline.

```python
import asyncio
import random

from agents import (
    Agent,
    function_tool,
)
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions



@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    print(f"[debug] get_weather called with city: {city}")
    choices = ["sunny", "cloudy", "rainy", "snowy"]
    return f"The weather in {city} is {random.choice(choices)}."


spanish_agent = Agent(
    name="Spanish",
    handoff_description="A spanish speaking agent.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. Speak in Spanish.",
    ),
    model="gpt-5.2",
)

agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. If the user speaks in Spanish, handoff to the spanish agent.",
    ),
    model="gpt-5.2",
    handoffs=[spanish_agent],
    tools=[get_weather],
)

```

--------------------------------

### RealtimeSession Enter Context API

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/session

Asynchronously enters the session's context, connecting to the model and preparing it for event streaming and message exchange. This is the recommended way to start a session using an async context manager.

```APIDOC
## __aenter__ RealtimeSession

### Description
Asynchronously starts the session by connecting to the model. This enables streaming events and sending messages/audio. It's designed for use with Python's `async with` statement.

### Method
__aenter__ (async)

### Endpoint
N/A (Asynchronous context manager method)

### Parameters
None

### Request Example
```python
async with session:
    # Session is active here
    await session.send_message(...) 
```

### Response
#### Success Response (RealtimeSession)
- **self** (`RealtimeSession`) - The current session object, now connected and ready.

#### Response Example
```python
# The 'session' object is returned and ready for use within the 'async with' block.
```
```

--------------------------------

### Get Playback State in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/openai_realtime

Retrieves the current playback state. It checks if a playback tracker is available and returns its state. If not, it attempts to get the last audio item ID from the audio state tracker.

```python
def _get_playback_state(self) -> RealtimePlaybackState:
    if self._playback_tracker:
        return self._playback_tracker.get_state()

    if last_audio_item_id := self._audio_state_tracker.get_last_audio_item():
        item_id, item_content_index = last_audio_item_id
```

--------------------------------

### SQLiteSession Initialization and Connection Handling (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/memory

Demonstrates the initialization of the SQLiteSession class, including setting up database paths, table names, and managing SQLite connections. It differentiates between in-memory databases and persistent file-based databases, utilizing thread-local connections for the latter to enhance concurrency. Includes schema creation for session and message tables.

```python
class SQLiteSession(SessionABC):
    """SQLite-based implementation of session storage.

    This implementation stores conversation history in a SQLite database.
    By default, uses an in-memory database that is lost when the process ends.
    For persistent storage, provide a file path.
    """

    def __init__(
        self,
        session_id: str,
        db_path: str | Path = ":memory:",
        sessions_table: str = "agent_sessions",
        messages_table: str = "agent_messages",
    ):
        """Initialize the SQLite session.

        Args:
            session_id: Unique identifier for the conversation session
            db_path: Path to the SQLite database file. Defaults to ':memory:' (in-memory database)
            sessions_table: Name of the table to store session metadata. Defaults to
                'agent_sessions'
            messages_table: Name of the table to store message data. Defaults to 'agent_messages'
        """
        self.session_id = session_id
        self.db_path = db_path
        self.sessions_table = sessions_table
        self.messages_table = messages_table
        self._local = threading.local()
        self._lock = threading.Lock()

        # For in-memory databases, we need a shared connection to avoid thread isolation
        # For file databases, we use thread-local connections for better concurrency
        self._is_memory_db = str(db_path) == ":memory:"
        if self._is_memory_db:
            self._shared_connection = sqlite3.connect(":memory:", check_same_thread=False)
            self._shared_connection.execute("PRAGMA journal_mode=WAL")
            self._init_db_for_connection(self._shared_connection)
        else:
            # For file databases, initialize the schema once since it persists
            init_conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            init_conn.execute("PRAGMA journal_mode=WAL")
            self._init_db_for_connection(init_conn)
            init_conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        if self._is_memory_db:
            # Use shared connection for in-memory database to avoid thread isolation
            return self._shared_connection
        else:
            # Use thread-local connections for file databases
            if not hasattr(self._local, "connection"):
                self._local.connection = sqlite3.connect(
                    str(self.db_path),
                    check_same_thread=False,
                )
                self._local.connection.execute("PRAGMA journal_mode=WAL")
            assert isinstance(self._local.connection, sqlite3.Connection), (
            f"Expected sqlite3.Connection, got {type(self._local.connection)}"
        )
            return self._local.connection

    def _init_db_for_connection(self, conn: sqlite3.Connection) -> None:
        """Initialize the database schema for a specific connection."""
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.sessions_table} (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.messages_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

```

--------------------------------

### Ensure Background Worker Thread Started in Python

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/processors

Ensures the background worker thread for the BatchTraceProcessor is started if it's not already running. It uses double-checked locking to prevent race conditions and ensure only one thread is started. This method is called before adding items to the queue.

```python
def _ensure_thread_started(self) -> None:
    # Fast path without holding the lock
    if self._worker_thread and self._worker_thread.is_alive():
        return

    # Double-checked locking to avoid starting multiple threads
    with self._thread_start_lock:
        if self._worker_thread and self._worker_thread.is_alive():
            return

        self._worker_thread = threading.Thread(target=self._run, daemon=True)
        self._worker_thread.start()

```

--------------------------------

### Define Agent Instructions (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/agent

Specifies how an agent should behave by defining its system prompt. Instructions can be a static string or a dynamic function that generates the prompt based on context and agent instance. This is crucial for guiding the agent's responses and actions.

```python
instructions: (
    str
    | Callable[
        [
            RunContextWrapper[TContext],
            RealtimeAgent[TContext],
        ],
        MaybeAwaitable[str],
    ]
    | None
) = None
```

--------------------------------

### Configure OpenAI Realtime Session with Tools and Prompts (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/openai_realtime

This snippet demonstrates how to configure a session for the OpenAI Realtime API. It includes setting up audio configurations, converting custom tools and handoffs into the required `OpenAISessionFunction` format, and defining instructions, prompts with variables, max output tokens, and tool choices. This configuration is crucial for initializing a realtime session with specific parameters.

```python
audio = OpenAIRealtimeAudioConfig(
    input=OpenAIRealtimeAudioInput(**audio_input_args),
    output=OpenAIRealtimeAudioOutput(**audio_output_args),
),
tools = cast(
    Any,
    self._tools_to_session_tools(
        tools=model_settings.get("tools", []),
        handoffs=model_settings.get("handoffs", []),
    ),
)
)

if "instructions" in model_settings:
    session_create_request.instructions = model_settings.get("instructions")

if "prompt" in model_settings:
    _passed_prompt: Prompt = model_settings["prompt"]
    variables: dict[str, Any] | None = _passed_prompt.get("variables")
    session_create_request.prompt = ResponsePrompt(
        id=_passed_prompt["id"],
        variables=variables,
        version=_passed_prompt.get("version"),
    )

if "max_output_tokens" in model_settings:
    session_create_request.max_output_tokens = cast(
        Any, model_settings.get("max_output_tokens")
    )

if "tool_choice" in model_settings:
    session_create_request.tool_choice = cast(Any, model_settings.get("tool_choice"))

return session_create_request
```

--------------------------------

### GET /api/agents/memory/conversation

Source: https://openai.github.io/openai-agents-python/ref/memory

Retrieves the conversation history for a given session. Supports filtering by a limit to get the latest items.

```APIDOC
## GET /api/agents/memory/conversation

### Description
Retrieves the conversation history for this session. It can optionally fetch a limited number of the most recent items.

### Method
GET

### Endpoint
/api/agents/memory/conversation

### Parameters
#### Query Parameters
- **limit** (int) - Optional - Maximum number of items to retrieve. If not specified, retrieves all items. When specified, returns the latest N items in chronological order.

### Request Example
(No request body for GET request)

### Response
#### Success Response (200)
- **items** (list[object]) - List of input items representing the conversation history. Each item is an object containing conversation data.

#### Response Example
```json
{
  "items": [
    {
      "role": "user",
      "content": "Hello, tell me about AI."
    },
    {
      "role": "assistant",
      "content": "Artificial intelligence (AI) is intelligence demonstrated by machines..."
    }
  ]
}
```
```

--------------------------------

### Function Span Creation

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing/create

This endpoint allows you to create a new function span. The span is not started automatically; you must either use a `with` statement or manually call `start()` and `finish()`.

```APIDOC
## POST /function_span

### Description
Creates a new function span for tracing. The span needs to be manually started and finished.

### Method
POST

### Endpoint
/function_span

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **name** (str) - Required - The name of the function.
- **input** (str | None) - Optional - The input to the function.
- **output** (str | None) - Optional - The output of the function.
- **span_id** (str | None) - Optional - The ID of the span. If not provided, a unique ID will be generated.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, the current trace/span will be used.
- **disabled** (bool) - Optional - If True, the span will not be recorded. Defaults to False.

### Request Example
```json
{
  "name": "my_function",
  "input": "some_input_data",
  "output": "some_output_data",
  "span_id": null,
  "parent": null,
  "disabled": false
}
```

### Response
#### Success Response (200)
- **Span[FunctionSpanData]** - The newly created function span object.

#### Response Example
```json
{
  "span_id": "generated_span_id",
  "name": "my_function",
  "input": "some_input_data",
  "output": "some_output_data"
}
```
```

--------------------------------

### Abstract Span Methods for Start and Finish

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing/spans

Defines abstract methods for managing the lifecycle of a span: starting and finishing. These methods are intended to be implemented by concrete span classes.

```python
import abc

class AbstractSpan(abc.ABC):
    @abc.abstractmethod
    def start(self, mark_as_current: bool = False):
        """
        Start the span.

        Args:
            mark_as_current: If true, the span will be marked as the current span.
        """
        pass

    @abc.abstractmethod
    def finish(self, reset_current: bool = False) -> None:
        """
        Finish the span.

        Args:
            reset_current: If true, the span will be reset as the current span.
        """
        pass
```

--------------------------------

### Get Playback State in Python

Source: https://openai.github.io/openai-agents-python/ref/realtime/openai_realtime

Retrieves the current playback state. It first checks if a playback tracker is available and returns its state. If not, it attempts to get the last audio item ID from the audio state tracker to determine the playback state.

```python
def _get_playback_state(self) -> RealtimePlaybackState:
    if self._playback_tracker:
        return self._playback_tracker.get_state()

    if last_audio_item_id := self._audio_state_tracker.get_last_audio_item():
        item_id, item_content_index = last_audio_item_id

```

--------------------------------

### RealtimeRunner.run()

Source: https://openai.github.io/openai-agents-python/ko/ref/realtime/runner

Starts and returns a realtime session, enabling bidirectional communication with the realtime model. This method is asynchronous and should be used within an async context.

```APIDOC
## RealtimeRunner.run()

### Description
Starts and returns a realtime session. This session object allows for bidirectional communication with the realtime model.

### Method
`async def run(
    self,
    *,
    context: TContext | None = None,
    model_config: RealtimeModelConfig | None = None,
) -> RealtimeSession`

### Endpoint
N/A (This is a Python method, not a REST endpoint)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
```python
runner = RealtimeRunner(agent)
async with await runner.run() as session:
    await session.send_message("Hello")
    async for event in session:
        print(event)
```

### Response
#### Success Response (RealtimeSession)
- **RealtimeSession** (`RealtimeSession`) - A session object that allows bidirectional communication with the realtime model.

#### Response Example
```json
// The actual response is a RealtimeSession object, not a JSON payload.
// See the Request Example for usage.
```
```

--------------------------------

### Local Runtime Tools: Shell and Apply Patch with OpenAI Agents Python SDK

Source: https://openai.github.io/openai-agents-python/tools

Illustrates the setup for local runtime tools, specifically ShellTool and ApplyPatchTool. It includes custom implementations for a no-operation computer interface and an apply patch editor, along with a function to execute shell commands.

```python
from agents import Agent, ApplyPatchTool, ShellTool
from agents.computer import AsyncComputer
from agents.editor import ApplyPatchResult, ApplyPatchOperation, ApplyPatchEditor


class NoopComputer(AsyncComputer):
    environment = "browser"
    dimensions = (1024, 768)
    async def screenshot(self): return ""
    async def click(self, x, y, button): ...
    async def double_click(self, x, y): ...
    async def scroll(self, x, y, scroll_x, scroll_y): ...
    async def type(self, text): ...
    async def wait(self): ...
    async def move(self, x, y): ...
    async def keypress(self, keys): ...
    async def drag(self, path): ...


class NoopEditor(ApplyPatchEditor):
    async def create_file(self, op: ApplyPatchOperation): return ApplyPatchResult(status="completed")
    async def update_file(self, op: ApplyPatchOperation): return ApplyPatchResult(status="completed")
    async def delete_file(self, op: ApplyPatchOperation): return ApplyPatchResult(status="completed")


async def run_shell(request):
    return "shell output"


agent = Agent(
    name="Local tools agent",
    tools=[
        ShellTool(executor=run_shell),
        ApplyPatchTool(editor=NoopEditor()),
        # ComputerTool expects a Computer/AsyncComputer implementation; omitted here for brevity.
    ],
)

```

--------------------------------

### Configure Agents with Different Models and Settings

Source: https://openai.github.io/openai-agents-python/models

Demonstrates how to initialize agents with specific models, including using string names or ModelProvider instances. It also shows how to apply model settings like temperature and extra arguments for OpenAI's Responses API.

```python
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
    model="gpt-5-mini", 
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model=OpenAIChatCompletionsModel( 
        model="gpt-5-nano",
        openai_client=AsyncOpenAI()
    ),
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
    model="gpt-5",
)

async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)

```

```python
from agents import Agent, ModelSettings

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model="gpt-4.1",
    model_settings=ModelSettings(temperature=0.1),
)

```

```python
from agents import Agent, ModelSettings

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model="gpt-4.1",
    model_settings=ModelSettings(
        temperature=0.1,
        extra_args={"service_tier": "flex", "user": "user_12345"},
    ),
)

```

--------------------------------

### Span Abstract Method: Start Span

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/spans

The `start` method initiates a span's execution. It accepts an optional boolean argument `mark_as_current` to designate the span as the currently active one. This is fundamental for managing nested operations and context propagation.

```python
@abc.abstractmethod
def start(self, mark_as_current: bool = False):
    """
    Start the span.

    Args:
        mark_as_current: If true, the span will be marked as the current span.
    """
    pass
```

--------------------------------

### Span Methods: Start and Finish

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/spans

Abstract methods for controlling the lifecycle of a span. The `start` method initiates the span's execution, with an option to mark it as the current span. The `finish` method terminates the span's execution, with an option to reset it as the current span. These methods are crucial for timing and managing span states.

```python
    @abc.abstractmethod
    def start(self, mark_as_current: bool = False):
        """
        Start the span.

        Args:
            mark_as_current: If true, the span will be marked as the current span.
        """
        pass

    @abc.abstractmethod
    def finish(self, reset_current: bool = False) -> None:
        """
        Finish the span.

        Args:
            reset_current: If true, the span will be reset as the current span.
        """
        pass
```

--------------------------------

### Realtime Agent Methods

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/agent

Documentation for the `clone` and `get_system_prompt` methods of the RealtimeAgent class.

```APIDOC
## Realtime Agent Methods

### Clone Agent

#### Description
Creates a copy of the agent, allowing specific arguments to be modified in the new instance.

#### Method
`clone`

#### Parameters
- `**kwargs` (Any): Keyword arguments to override agent properties in the cloned instance.

#### Request Example
```python
new_agent = agent.clone(instructions="New instructions")
```

### Get System Prompt

#### Description
Retrieves the system prompt for the agent. It returns the static instruction string or the result of the dynamic instruction function.

#### Method
`get_system_prompt`

#### Parameters
- **run_context** (`RunContextWrapper[TContext]`): The wrapper for the run context.

#### Response
- **Success Response (str | None)**: The system prompt string or None if not defined.

#### Response Example
```python
system_prompt = await agent.get_system_prompt(run_context)
```
```

--------------------------------

### Create a Custom Trace with Context Manager

Source: https://openai.github.io/openai-agents-python/tracing

Demonstrates how to create a custom trace using the `trace()` function as a context manager. This approach automatically handles starting and finishing the trace, making it the recommended method for custom tracing. It wraps multiple agent runs within a single trace to group related operations.

```python
from agents import Agent, Runner, trace

async def main():
    agent = Agent(name="Joke generator", instructions="Tell funny jokes.")

    with trace("Joke workflow"):
        first_result = await Runner.run(agent, "Tell me a joke")
        second_result = await Runner.run(agent, f"Rate this joke: {first_result.final_output}")
        print(f"Joke: {first_result.final_output}")
        print(f"Rating: {second_result.final_output}")

```

--------------------------------

### Get Response API

Source: https://openai.github.io/openai-agents-python/ko/ref/models/interface

This endpoint allows you to get a response from the model by providing system instructions, input, model settings, tools, output schema, handoffs, tracing, and optional conversation context.

```APIDOC
## POST /agents/models/response

### Description
Get a response from the model.

### Method
POST

### Endpoint
/agents/models/response

### Parameters
#### Request Body
- **system_instructions** (str | None) - Required - The system instructions to use.
- **input** (str | list[TResponseInputItem]) - Required - The input items to the model, in OpenAI Responses format.
- **model_settings** (ModelSettings) - Required - The model settings to use.
- **tools** (list[Tool]) - Required - The tools available to the model.
- **output_schema** (AgentOutputSchemaBase | None) - Required - The output schema to use.
- **handoffs** (list[Handoff]) - Required - The handoffs available to the model.
- **tracing** (ModelTracing) - Required - Tracing configuration.
- **previous_response_id** (str | None) - Required - the ID of the previous response. Generally not used by the model, except for the OpenAI Responses API.
- **conversation_id** (str | None) - Required - The ID of the stored conversation, if any.
- **prompt** (ResponsePromptParam | None) - Required - The prompt config to use for the model.

### Request Example
```json
{
  "system_instructions": "You are a helpful assistant.",
  "input": "What is the capital of France?",
  "model_settings": { "model": "gpt-4" },
  "tools": [],
  "output_schema": null,
  "handoffs": [],
  "tracing": { "enabled": true },
  "previous_response_id": null,
  "conversation_id": null,
  "prompt": null
}
```

### Response
#### Success Response (200)
- **response** (ModelResponse) - The full model response.

#### Response Example
```json
{
  "response": {
    "content": "The capital of France is Paris.",
    "tool_calls": [],
    "metadata": {}
  }
}
```
```

--------------------------------

### RealtimeSession Initialization

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/session

Initializes a new RealtimeSession with the specified model, agent, and context. Optional configurations for model and runtime can also be provided.

```APIDOC
## __init__ RealtimeSession

### Description
Initializes the session with a model, agent, and context. Allows for optional model and runtime configurations.

### Method
__init__

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (`RealtimeModel`) - Required - The model to use.
- **agent** (`RealtimeAgent`) - Required - The current agent.
- **context** (`TContext | None`) - Required - The context object.
- **model_config** (`RealtimeModelConfig | None`) - Optional - Model configuration. Defaults to None.
- **run_config** (`RealtimeRunConfig | None`) - Optional - Runtime configuration including guardrails. Defaults to None.

### Request Example
```python
# Assuming model, agent, and context are already defined
session = RealtimeSession(
    model=my_model,
    agent=my_agent,
    context=my_context,
    model_config=my_model_config,
    run_config=my_run_config
)
```

### Response
#### Success Response (None)
This method does not return a value directly, but initializes the session object.

#### Response Example
None
```

--------------------------------

### Analyze Conversation: Get by Turns, Tool Usage, Find by Content

Source: https://openai.github.io/openai-agents-python/sessions/advanced_sqlite_session

Shows how to perform structured queries on conversation data using `AdvancedSQLiteSession`. Methods include retrieving conversation organized by turns, getting tool usage statistics, and finding turns by matching content. Depends on the `session` object.

```python
# Get conversation organized by turns
conversation_by_turns = await session.get_conversation_by_turns()
for turn_num, items in conversation_by_turns.items():
    print(f"Turn {turn_num}: {len(items)} items")
    for item in items:
        if item["tool_name"]:
            print(f"  - {item['type']} (tool: {item['tool_name']})")
        else:
            print(f"  - {item['type']}")

# Get tool usage statistics
tool_usage = await session.get_tool_usage()
for tool_name, count, turn in tool_usage:
    print(f"{tool_name}: used {count} times in turn {turn}")

# Find turns by content
matching_turns = await session.find_turns_by_content("weather")
for turn in matching_turns:
    print(f"Turn {turn['turn']}: {turn['content']}")
```

--------------------------------

### Get Current Time in ISO Format in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/provider

The `time_iso` abstract method provides a standardized way to get the current time formatted according to the ISO 8601 standard. This is often used for timestamping events within traces.

```python
@abstractmethod
def time_iso(self) -> str:
    """Return the current time in ISO 8601 format."""

```

--------------------------------

### as_tool Method Documentation

Source: https://openai.github.io/openai-agents-python/ja/ref/agent

This section details the `as_tool` method, its purpose, parameters, and how it differs from agent handoffs.

```APIDOC
## as_tool Method

### Description
Transforms an agent into a tool that can be called by other agents. This differs from agent handoffs as the new agent receives generated input instead of the conversation history, and the original agent continues the conversation after the tool call.

### Method
`as_tool`

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
```python
# Assuming 'my_agent' is an instance of an AgentBase subclass

tool_callable = my_agent.as_tool(
    tool_name="MyAgentAsTool",
    tool_description="This tool executes the functionality of MyAgent.",
    is_enabled=True,
    on_stream=my_stream_handler
)

# Now 'tool_callable' can be used as a tool by another agent.
```

### Response
#### Success Response (200)
Returns a `Tool` object that can be invoked by other agents.

#### Response Example
```json
{
  "tool_name": "MyAgentAsTool",
  "tool_description": "This tool executes the functionality of MyAgent.",
  "is_enabled": true
}
```

### Parameters Details:
- **tool_name** (`str | None`): The name of the tool. If not provided, the agent's name will be used. (Required)
- **tool_description** (`str | None`): The description of the tool, indicating its purpose and usage. (Required)
- **custom_output_extractor** (`Callable[[RunResult | RunResultStreaming], Awaitable[str]] | None`): A function to extract output from the agent's run result. Defaults to using the last message. (Optional)
- **is_enabled** (`bool | Callable[[RunContextWrapper[Any], AgentBase[Any]], MaybeAwaitable[bool]]`): Determines if the tool is available to be called. Can be a boolean or a function. Defaults to `True`.
- **on_stream** (`Callable[[AgentToolStreamEvent], MaybeAwaitable[None]] | None`): A callback function to handle streaming events during the nested agent run. (Optional)
- **run_config** (`RunConfig | None`): Configuration for the agent run. (Optional)
- **max_turns** (`int | None`): Maximum number of turns for the agent run. (Optional)
- **hooks** (`RunHooks[TContext] | None`): Hooks to be applied to the agent run. (Optional)
- **previous_response_id** (`str | None`): The ID of the previous response in the conversation. (Optional)
- **conversation_id** (`str | None`): The ID of the current conversation. (Optional)
- **session** (`Session | None`): The session object for the agent run. (Optional)
- **failure_error_function** (`ToolErrorFunction | None`): A function to generate an error message if the tool run fails. Defaults to `default_tool_error_function`.
```

--------------------------------

### Abstract Trace Start Callback - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing

Defines the `on_trace_start` method, which is called synchronously when a new trace begins. Implementations should return quickly to avoid blocking execution and handle errors internally.

```python
@abc.abstractmethod
def on_trace_start(self, trace: "Trace") -> None:
    """Called when a new trace begins execution.

    Args:
        trace: The trace that started. Contains workflow name and metadata.

    Notes:
        - Called synchronously on trace start
        - Should return quickly to avoid blocking execution
        - Any errors should be caught and handled internally
    """
    pass

```

--------------------------------

### Transcription Span API

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/create

This endpoint allows for the creation of a new transcription span. The span is not automatically started and requires manual initiation using a `with` statement or explicit `start()` and `finish()` calls.

```APIDOC
## transcription_span

### Description
Create a new transcription span. The span will not be started automatically, you should either do `with transcription_span() ...` or call `span.start()` + `span.finish()` manually.

### Method
Not Applicable (Python function)

### Endpoint
Not Applicable (Python function)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Parameters
- **model** (str | None) - Optional - The name of the model used for the speech-to-text.
- **input** (str | None) - Optional - The audio input of the speech-to-text transcription, as a base64 encoded string of audio bytes.
- **input_format** (str | None) - Optional - The format of the audio input (defaults to "pcm"). Defaults to 'pcm'.
- **output** (str | None) - Optional - The output of the speech-to-text transcription.
- **model_config** (Mapping[str, Any] | None) - Optional - The model configuration (hyperparameters) used.
- **span_id** (str | None) - Optional - The ID of the span. Optional. If not provided, we will generate an ID. We recommend using `util.gen_span_id()` to generate a span ID, to guarantee that IDs are correctly formatted.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, we will automatically use the current trace/span as the parent.
- **disabled** (bool) - Optional - If True, we will return a Span but the Span will not be recorded. Defaults to False.

### Request Example
```python
# Example usage within a 'with' statement:
with transcription_span(model="whisper-1", input="base64_encoded_audio_data") as span:
    # Perform transcription operations
    result = perform_transcription(span.input)
    span.output = result

# Example usage with manual start/finish:
tran_span = transcription_span(model="whisper-1", input="base64_encoded_audio_data")
tran_span.start()
try:
    # Perform transcription operations
    result = perform_transcription(tran_span.input)
    tran_span.output = result
finally:
    tran_span.finish()
```

### Response
#### Success Response (200)
- **Span[TranscriptionSpanData]** - The newly created speech-to-text span.

#### Response Example
```json
{
  "span_id": "generated_or_provided_id",
  "parent_id": "optional_parent_id",
  "start_time": "timestamp",
  "end_time": "timestamp",
  "name": "transcription",
  "data": {
    "input": "base64_encoded_audio_data",
    "input_format": "pcm",
    "output": "transcribed_text",
    "model": "whisper-1",
    "model_config": {}
  }
}
```
```

--------------------------------

### RealtimeSession Initialization

Source: https://openai.github.io/openai-agents-python/ref/realtime/session

Initializes a RealtimeSession object with a model, agent, context, and optional configurations. It sets up internal state for history, model settings, event queues, and guardrail tracking.

```python
def __init__(self,
        model: RealtimeModel,
        agent: RealtimeAgent,
        context: object,
        model_config: dict | None = None,
        run_config: dict | None = None,
    ):
        """Initialize the RealtimeSession.

        Args:
            model: The RealtimeModel instance to use for communication.
            agent: The initial RealtimeAgent for the session.
            context: The context object for the session.
            model_config: Optional configuration for the model.
            run_config: Runtime configuration including guardrails.
        """
        self._model = model
        self._current_agent = agent
        self._context_wrapper = RunContextWrapper(context)
        self._event_info = RealtimeEventInfo(context=self._context_wrapper)
        self._history: list[RealtimeItem] = []
        self._model_config = model_config or {}
        self._run_config = run_config or {}
        initial_model_settings = self._model_config.get("initial_model_settings")
        run_config_settings = self._run_config.get("model_settings")
        self._base_model_settings: RealtimeSessionModelSettings = {
            **(run_config_settings or {}),
            **(initial_model_settings or {}),
        }
        self._event_queue: asyncio.Queue[RealtimeSessionEvent] = asyncio.Queue()
        self._closed = False
        self._stored_exception: BaseException | None = None

        # Guardrails state tracking
        self._interrupted_response_ids: set[str] = set()
        self._item_transcripts: dict[str, str] = {}  # item_id -> accumulated transcript
        self._item_guardrail_run_counts: dict[str, int] = {}  # item_id -> run count
        self._debounce_text_length = self._run_config.get("guardrails_settings", {}).get(
            "debounce_text_length", 100
        )

        self._guardrail_tasks: set[asyncio.Task[Any]] = set()
        self._tool_call_tasks: set[asyncio.Task[Any]] = set()
        self._async_tool_calls: bool = bool(self._run_config.get("async_tool_calls", True))
```

--------------------------------

### GET /tools/all

Source: https://openai.github.io/openai-agents-python/ja/ref/agent

Retrieves all agent tools, including both MCP tools and function tools. This endpoint provides a comprehensive list of all tools accessible by the agent.

```APIDOC
## GET /tools/all

### Description
All agent tools, including MCP tools and function tools.

### Method
GET

### Endpoint
/tools/all

### Parameters
#### Query Parameters
- **run_context** (RunContextWrapper) - Required - The context for the current run.

### Request Example
```json
{
  "run_context": "<RunContextWrapper object>"
}
```

### Response
#### Success Response (200)
- **tools** (list[Tool]) - A list of all available tools, including MCP and function tools.

#### Response Example
```json
[
  {
    "name": "mcp_tool_example",
    "description": "An example MCP tool",
    "parameters": {},
    "return_direct": false
  },
  {
    "name": "function_tool_example",
    "description": "An example function tool",
    "parameters": {},
    "return_direct": false
  }
]
```
```

--------------------------------

### Trace Lifecycle Events

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/provider

Callbacks for the start and end of a trace.

```APIDOC
## on_trace_start

### Description
Called when a trace is started.

### Method
This is a method within a class, likely a tracing provider.

### Endpoint
N/A (Internal method)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **trace** (Trace) - Required - The trace object representing the current trace.

### Request Example
```python
# Assuming 'trace' is an instance of the Trace class
provider.on_trace_start(trace)
```

### Response
#### Success Response (None)
This method does not return a value.

## on_trace_end

### Description
Called when a trace is finished.

### Method
This is a method within a class, likely a tracing provider.

### Endpoint
N/A (Internal method)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **trace** (Trace) - Required - The trace object representing the finished trace.

### Request Example
```python
# Assuming 'trace' is an instance of the Trace class
provider.on_trace_end(trace)
```

### Response
#### Success Response (None)
This method does not return a value.
```

--------------------------------

### Get Text-to-Speech Model

Source: https://openai.github.io/openai-agents-python/ko/ref/voice/models/openai_model_provider

Retrieves a text-to-speech model by its name. If no model name is provided, a default model will be returned.

```APIDOC
## GET /voice/models/openai/tts

### Description
Retrieves a text-to-speech (TTS) model by its name. If `model_name` is not specified, a default TTS model is used.

### Method
GET

### Endpoint
/voice/models/openai/tts

### Parameters
#### Query Parameters
- **model_name** (str) - Optional - The name of the text-to-speech model to retrieve. Defaults to a predefined model if not provided.

### Request Example
```
GET /voice/models/openai/tts?model_name=tts-1
```

### Response
#### Success Response (200)
- **model_type** (str) - The type of the TTS model (e.g., "OpenAITTSModel").
- **model_name** (str) - The name of the retrieved TTS model.

#### Response Example
```json
{
  "model_type": "OpenAITTSModel",
  "model_name": "tts-1"
}
```
```

--------------------------------

### Handle Dynamic Instructions in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/agent

This code demonstrates how to handle dynamic instructions for an agent. It checks if the instructions are a callable function, inspects its signature to ensure it accepts exactly two arguments (context and agent), and then calls the function, supporting both synchronous and asynchronous functions. If instructions are not a string or callable, an error is logged.

```python
import inspect
from typing import Callable, Awaitable, cast

# Assuming RunContextWrapper and Agent are defined elsewhere
# class RunContextWrapper[TContext]: pass
# class Agent[TContext]: pass

# Placeholder for logger and cast if not available in the snippet's context
class Logger:
    def error(self, message):
        print(f"ERROR: {message}")
logger = Logger()

def cast(type, value):
    return value

async def await_cast(type, value):
    return await value

class PromptUtil:
    @staticmethod
    async def to_model_input(prompt, run_context, agent):
        # Dummy implementation for demonstration
        return f"Processed prompt: {prompt}"

class ResponsePromptParam:
    pass

class ModelSettings:
    pass

class AgentOutputSchemaBase:
    pass

class AgentHooks:
    pass

class Handoff:
    pass

def get_default_model_settings():
    return ModelSettings()

class RunContextWrapper[TContext]:
    pass

class Agent[TContext]:
    def __init__(self, instructions=None, prompt=None):
        self.instructions = instructions
        self.prompt = prompt

    async def get_prompt(self, run_context: RunContextWrapper[TContext]) -> ResponsePromptParam | None:
        """Get the prompt for the agent."""
        return await PromptUtil.to_model_input(self.prompt, run_context, self)

    async def process_instructions(self, run_context: RunContextWrapper[TContext]) -> str | None:
        """Processes the agent's instructions, handling string or callable inputs."""
        if isinstance(self.instructions, str):
            return self.instructions
        elif callable(self.instructions):
            # Inspect the signature of the instructions function
            sig = inspect.signature(self.instructions)
            params = list(sig.parameters.values())

            # Enforce exactly 2 parameters
            if len(params) != 2:
                raise TypeError(
                    f"'instructions' callable must accept exactly 2 arguments (context, agent), "
                    f"but got {len(params)}: {[p.name for p in params]}"
                )

            # Call the instructions function properly
            if inspect.iscoroutinefunction(self.instructions):
                return await await_cast(Awaitable[str], self.instructions(run_context, self))
            else:
                return cast(str, self.instructions(run_context, self))

        elif self.instructions is not None:
            logger.error(
                f"Instructions must be a string or a callable function, "
                f"got {type(self.instructions).__name__}"
            )

        return None

# Example Usage:

async def dynamic_instructions(context, agent):
    return f"Dynamic instructions for agent based on context: {context}"

# Example with a string instruction
agent_str = Agent(instructions="This is a static instruction.")
# Example with a callable instruction
agent_callable = Agent(instructions=dynamic_instructions)

async def main():
    # Dummy run_context
    class DummyRunContext:
        pass
    run_context = DummyRunContext()

    instructions_str = await agent_str.process_instructions(run_context)
    print(f"String instructions: {instructions_str}")

    instructions_callable = await agent_callable.process_instructions(run_context)
    print(f"Callable instructions: {instructions_callable}")

# To run the example:
# import asyncio
# asyncio.run(main())

```

--------------------------------

### Span Methods

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing

This section covers the core methods for managing the lifecycle of a span: starting and finishing.

```APIDOC
## Span Methods

This section covers the core methods for managing the lifecycle of a span: starting and finishing.

### `start(mark_as_current: bool = False)`

- **Description**: Start the span.
- **Parameters**:
  - `mark_as_current` (bool): If true, the span will be marked as the current span. (Default: `False`)

### `finish(reset_current: bool = False) -> None`

- **Description**: Finish the span.
- **Parameters**:
  - `reset_current` (bool): If true, the span will be reset as the current span. (Default: `False`)
```

--------------------------------

### Initialize OpenAIChatCompletionsModel in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/models/openai_chatcompletions

Initializes the OpenAIChatCompletionsModel with a specific OpenAI chat model and an asynchronous OpenAI client. This setup is crucial for making subsequent API calls.

```python
class OpenAIChatCompletionsModel(Model):
    def __init__(
        self,
        model: str | ChatModel,
        openai_client: AsyncOpenAI,
    ) -> None:
        self.model = model
        self._client = openai_client
```

--------------------------------

### ComputerCreate Protocol

Source: https://openai.github.io/openai-agents-python/ref/tool

Protocol for initializing a computer for the current run context.

```APIDOC
## ComputerCreate Protocol

### Description
Initializes a computer for the current run context.

### Method
`__call__`

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **run_context** (RunContextWrapper[Any]) - Required - The run context wrapper.

### Request Example
```python
# This is a protocol, actual implementation will vary.
async def create_computer(run_context: RunContextWrapper[Any]) -> Computer:
    # ... implementation ...
    pass
```

### Response
#### Success Response (200)
- **ComputerT_co** (Any) - The created computer instance.

#### Response Example
```python
# Example of a computer instance
class MyComputer:
    pass

# Assuming MyComputer is the type for ComputerT_co
# The actual return value would be an instance of MyComputer
```
```

--------------------------------

### Creating Handoffs Between Realtime Agents (Python)

Source: https://openai.github.io/openai-agents-python/realtime/guide

Illustrates how to implement conversation handoffs between specialized `RealtimeAgent` instances. This allows a main agent to transfer the conversation to a more suitable agent (e.g., billing or technical support) based on user intent. The example defines specialized agents and then configures the main agent with handoff configurations.

```python
from agents.realtime import RealtimeAgent, realtime_handoff

# Specialized agents
billing_agent = RealtimeAgent(
    name="Billing Support",
    instructions="You specialize in billing and payment issues.",
)

technical_agent = RealtimeAgent(
    name="Technical Support",
    instructions="You handle technical troubleshooting.",
)

# Main agent with handoffs
main_agent = RealtimeAgent(
    name="Customer Service",
    instructions="You are the main customer service agent. Hand off to specialists when needed.",
    handoffs=[
        realtime_handoff(billing_agent, tool_description="Transfer to billing support"),
        realtime_handoff(technical_agent, tool_description="Transfer to technical support"),
    ]
)
```

--------------------------------

### RealtimeRunner Initialization Method (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/runner

This Python code snippet details the `__init__` method for the `RealtimeRunner` class. It outlines the parameters required for initializing a real-time agent session, including the starting agent, an optional custom model, and configuration overrides. The method initializes internal state and sets up a default OpenAI realtime WebSocket model if none is provided. The arguments specify the type and purpose of each parameter.

```python
def __init__(
    self,
    starting_agent: RealtimeAgent,
    *,
    model: RealtimeModel | None = None,
    config: RealtimeRunConfig | None = None,
) -> None:
    """Initialize the realtime runner.

    Args:
        starting_agent: The agent to start the session with.
        context: The context to use for the session.
        model: The model to use. If not provided, will use a default OpenAI realtime model.
        config: Override parameters to use for the entire run.
    """
    self._starting_agent = starting_agent
    self._config = config
    self._model = model or OpenAIRealtimeWebSocketModel()

```

--------------------------------

### SQLAlchemySession Initialization

Source: https://openai.github.io/openai-agents-python/zh/ref/extensions/memory/sqlalchemy_session

Creates an instance of SQLAlchemySession, establishing a connection to the database using SQLAlchemy's async engine. It handles optional keyword arguments for engine creation and constructor parameters. Dependencies include `sqlalchemy.ext.asyncio.create_async_engine`.

```python
def __init__(
        cls,
        session_id: str,
        url: str,
        engine_kwargs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> "SQLAlchemySession":
        """Create a new SQLAlchemySession.

        Args:
            session_id: The unique identifier for the session.
            url: The database connection URL.
            engine_kwargs (dict[str, Any] | None): Additional keyword arguments forwarded to
                sqlalchemy.ext.asyncio.create_async_engine.
            **kwargs: Additional keyword arguments forwarded to the main constructor
                (e.g., create_tables, custom table names, etc.).

        Returns:
            SQLAlchemySession: An instance of SQLAlchemySession connected to the specified database.
        """
        engine_kwargs = engine_kwargs or {}
        engine = create_async_engine(url, **engine_kwargs)
        return cls(session_id, engine=engine, **kwargs)
```

--------------------------------

### Adding Tools to Realtime Agents (Python)

Source: https://openai.github.io/openai-agents-python/realtime/guide

Demonstrates how to define and add function tools to a RealtimeAgent. These tools allow the agent to perform specific actions during a conversation. The example shows defining `get_weather` and `book_appointment` functions decorated as tools and then passing them to the `RealtimeAgent` constructor.

```python
from agents import function_tool
from agents.realtime import RealtimeAgent

@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Your weather API logic here
    return f"The weather in {city} is sunny, 72°F"

@function_tool
def book_appointment(date: str, time: str, service: str) -> str:
    """Book an appointment."""
    # Your booking logic here
    return f"Appointment booked for {service} on {date} at {time}"

agent = RealtimeAgent(
    name="Assistant",
    instructions="You can help with weather and appointments.",
    tools=[get_weather, book_appointment],
)
```

--------------------------------

### Get Prompt API

Source: https://openai.github.io/openai-agents-python/ko/ref/mcp/server

Retrieves a specific prompt from the server by name.

```APIDOC
## GET /get_prompt/{name}

### Description
Get a specific prompt from the server.

### Method
GET

### Endpoint
/get_prompt/{name}

### Parameters
#### Path Parameters
- **name** (str) - Required - The name of the prompt to retrieve.

#### Query Parameters
- **arguments** (dict[str, Any] | None) - Optional - A dictionary of arguments to pass to the prompt.

### Response
#### Success Response (200)
- **prompt** (GetPromptResult) - A result object containing the prompt details.

#### Response Example
```json
{
  "prompt": {
    "name": "example_prompt",
    "template": "This is an example prompt template."
  }
}
```
```

--------------------------------

### Web and File Search with OpenAI Agents Python SDK

Source: https://openai.github.io/openai-agents-python/tools

Demonstrates how to configure an agent with WebSearchTool and FileSearchTool for retrieving information. The FileSearchTool requires vector store IDs and a maximum number of results to be specified.

```python
from agents import Agent, FileSearchTool, Runner, WebSearchTool

agent = Agent(
    name="Assistant",
    tools=[
        WebSearchTool(),
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=["VECTOR_STORE_ID"],
        ),
    ],
)

async def main():
    result = await Runner.run(agent, "Which coffee shop should I go to, taking into account my preferences and the weather today in SF?")
    print(result.final_output)

```

--------------------------------

### Get Text-to-Speech Model

Source: https://openai.github.io/openai-agents-python/ko/ref/voice/models/openai_provider

Retrieves a text-to-speech model by its name. If no name is provided, a default model will be returned.

```APIDOC
## get_tts_model

### Description
Get a text-to-speech model by name. If no name is provided, a default model will be returned.

### Method
GET

### Endpoint
/websites/openai_github_io_openai-agents-python/tts_models

### Parameters
#### Path Parameters
None

#### Query Parameters
- **model_name** (str | None) - Required - The name of the model to get.

#### Request Body
None

### Request Example
```
GET /websites/openai_github_io_openai-agents-python/tts_models?model_name=tts-1
```

### Response
#### Success Response (200)
- **TTSModel** (TTSModel) - The text-to-speech model.

#### Response Example
```json
{
  "model_type": "OpenAITTSModel",
  "model_name": "tts-1"
}
```
```

--------------------------------

### Initialize RealtimeSession in Python

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/session

Initializes a RealtimeSession object with the model, agent, context, and configuration. It sets up internal state for event handling, guardrails, and model settings, preparing for a real-time interaction session.

```python
def __init__(
        self,
        model: RealtimeModel,
        agent: RealtimeAgent,
        context: RunContext,
        model_config: RealtimeModelConfig | None = None,
        run_config: RuntimeConfiguration | None = None,
    ):
        """Initialize the session.

        Args:
            model: The real-time model to interact with.
            agent: The agent to use for the session.
            context: The run context for the session.
            model_config: Model-specific configuration.
            run_config: Runtime configuration including guardrails.
        """
        self._model = model
        self._current_agent = agent
        self._context_wrapper = RunContextWrapper(context)
        self._event_info = RealtimeEventInfo(context=self._context_wrapper)
        self._history: list[RealtimeItem] = []
        self._model_config = model_config or {}
        self._run_config = run_config or {}
        initial_model_settings = self._model_config.get("initial_model_settings")
        run_config_settings = self._run_config.get("model_settings")
        self._base_model_settings: RealtimeSessionModelSettings = {
            **(run_config_settings or {}),
            **(initial_model_settings or {}),
        }
        self._event_queue: asyncio.Queue[RealtimeSessionEvent] = asyncio.Queue()
        self._closed = False
        self._stored_exception: BaseException | None = None

        # Guardrails state tracking
        self._interrupted_response_ids: set[str] = set()
        self._item_transcripts: dict[str, str] = {}
        self._item_guardrail_run_counts: dict[str, int] = {}
        self._debounce_text_length = self._run_config.get("guardrails_settings", {}).get(
            "debounce_text_length", 100
        )

        self._guardrail_tasks: set[asyncio.Task[Any]] = set()
        self._tool_call_tasks: set[asyncio.Task[Any]] = set()
        self._async_tool_calls: bool = bool(self._run_config.get("async_tool_calls", True))
```

--------------------------------

### Get AsyncOpenAI Client (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/models/openai_chatcompletions

This function provides a singleton instance of the AsyncOpenAI client. If the client has not been initialized, it creates a new instance. This ensures that only one client object is used throughout the application, which can be beneficial for resource management.

```python
    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI()
        return self._client
```

--------------------------------

### Get Real-time Session Configuration (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/openai_realtime

Retrieves and constructs the session configuration for a real-time session based on model settings. It meticulously processes audio input and output configurations, including format, noise reduction, transcription, and turn detection. Default settings are applied when specific configurations are not found.

```python
def _get_session_config(
        self,
        model_settings: RealtimeSessionModelSettings
    ) -> OpenAISessionCreateRequest:
        """Get the session config."""
        audio_input_args: dict[str, Any] = {}
        audio_output_args: dict[str, Any] = {}

        audio_config = model_settings.get("audio")
        audio_config_mapping = audio_config if isinstance(audio_config, Mapping) else None
        input_audio_config: Mapping[str, Any] = (
            cast(Mapping[str, Any], audio_config_mapping.get("input", {}))
            if audio_config_mapping
            else {}
        )
        output_audio_config: Mapping[str, Any] = (
            cast(Mapping[str, Any], audio_config_mapping.get("output", {}))
            if audio_config_mapping
            else {}
        )

        input_format_source: FormatInput = (
            input_audio_config.get("format") if input_audio_config else None
        )
        if input_format_source is None:
            if self._call_id:
                input_format_source = model_settings.get("input_audio_format")
            else:
                input_format_source = model_settings.get(
                    "input_audio_format", DEFAULT_MODEL_SETTINGS.get("input_audio_format")
                )
        audio_input_args["format"] = to_realtime_audio_format(input_format_source)

        if "noise_reduction" in input_audio_config:
            audio_input_args["noise_reduction"] = input_audio_config.get("noise_reduction")
        elif "input_audio_noise_reduction" in model_settings:
            audio_input_args["noise_reduction"] = model_settings.get("input_audio_noise_reduction")

        if "transcription" in input_audio_config:
            audio_input_args["transcription"] = input_audio_config.get("transcription")
        elif "input_audio_transcription" in model_settings:
            audio_input_args["transcription"] = model_settings.get("input_audio_transcription")
        else:
            audio_input_args["transcription"] = DEFAULT_MODEL_SETTINGS.get(
                "input_audio_transcription"
            )

        if "turn_detection" in input_audio_config:
            audio_input_args["turn_detection"] = self._normalize_turn_detection_config(
                input_audio_config.get("turn_detection")
            )
        elif "turn_detection" in model_settings:
            audio_input_args["turn_detection"] = self._normalize_turn_detection_config(
                model_settings.get("turn_detection")
            )
        else:
            audio_input_args["turn_detection"] = DEFAULT_MODEL_SETTINGS.get("turn_detection")

        requested_voice = output_audio_config.get("voice") if output_audio_config else None
        audio_output_args["voice"] = requested_voice or model_settings.get(
            "voice", DEFAULT_MODEL_SETTINGS.get("voice")
        )

        output_format_source: FormatInput = (
            output_audio_config.get("format") if output_audio_config else None
        )
        if output_format_source is None:
            if self._call_id:
                output_format_source = model_settings.get("output_audio_format")
            else:
                output_format_source = model_settings.get(
                    "output_audio_format", DEFAULT_MODEL_SETTINGS.get("output_audio_format")
                )
        audio_output_args["format"] = to_realtime_audio_format(output_format_source)

        if "speed" in output_audio_config:
            audio_output_args["speed"] = output_audio_config.get("speed")
        elif "speed" in model_settings:
            audio_output_args["speed"] = model_settings.get("speed")

        output_modalities = (
            model_settings.get("output_modalities")
            or model_settings.get("modalities")
            or DEFAULT_MODEL_SETTINGS.get("modalities")
        )

        # Construct full session object. `type` will be excluded at serialization time for updates.
        session_create_request = OpenAISessionCreateRequest(
            type="realtime",
            model=(model_settings.get("model_name") or self.model) or "gpt-realtime",
            output_modalities=output_modalities,
            input_audio=audio_input_args,
            output_audio=audio_output_args,
        )
        return session_create_request
```

--------------------------------

### Voice Model Provider - get_tts_model

Source: https://openai.github.io/openai-agents-python/zh/ref/voice/model

Get a text-to-speech model by name.

```APIDOC
## GET /voice/tts-model

### Description
Get a text-to-speech model by name.

### Method
GET

### Endpoint
/voice/tts-model

### Parameters
#### Query Parameters
- **model_name** (str | None) - Required - The name of the model to get.

### Response
#### Success Response (200)
- **model** (TTSModel) - The text-to-speech model.

#### Response Example
{
  "model": "<TTSModel object>"
}
```

--------------------------------

### Create Guardrail Span in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/create

Creates a new guardrail span. The span must be explicitly started and finished using a `with` statement or manual `start()` and `finish()` calls. It accepts parameters for naming, trigger status, span ID, parent span, and a disabled flag.

```python
def guardrail_span(
    name: str,
    triggered: bool = False,
    span_id: str | None = None,
    parent: Trace | Span[Any] | None = None,
    disabled: bool = False,
) -> Span[GuardrailSpanData]:
    """Create a new guardrail span. The span will not be started automatically, you should either
    do `with guardrail_span() ...` or call `span.start()` + `span.finish()` manually.

    Args:
        name: The name of the guardrail.
        triggered: Whether the guardrail was triggered.
        span_id: The ID of the span. Optional. If not provided, we will generate an ID. We
            recommend using `util.gen_span_id()` to generate a span ID, to guarantee that IDs are
            correctly formatted.
        parent: The parent span or trace. If not provided, we will automatically use the current
            trace/span as the parent.
        disabled: If True, we will return a Span but the Span will not be recorded.
    """
    return get_trace_provider().create_span(
        span_data=GuardrailSpanData(name=name, triggered=triggered),
        span_id=span_id,
        parent=parent,
        disabled=disabled,
    )

```

--------------------------------

### Get Prompt API

Source: https://openai.github.io/openai-agents-python/ja/ref/mcp/server

Retrieves a specific prompt from the server by its name, optionally with arguments.

```APIDOC
## GET /prompts/{name}

### Description
Retrieves a specific prompt from the server by its name, optionally with arguments.

### Method
GET

### Endpoint
/prompts/{name}

### Parameters
#### Path Parameters
- **name** (str) - Required - The name of the prompt to retrieve.

#### Query Parameters
- **arguments** (dict[str, Any] | None) - Optional - Arguments to be used with the prompt.

### Request Example
```json
{
  "arguments": {
    "variable1": "value1"
  }
}
```

### Response
#### Success Response (200)
- **prompt_details** (GetPromptResult) - A result object containing the prompt details.

#### Response Example
```json
{
  "prompt_details": {
    "content": "This is the content of the prompt."
  }
}
```
```

--------------------------------

### Span Lifecycle Events

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/provider

Callbacks for the start and end of a span within a trace.

```APIDOC
## on_span_start

### Description
Called when a span is started.

### Method
This is a method within a class, likely a tracing provider.

### Endpoint
N/A (Internal method)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **span** (Span[Any]) - Required - The span object representing the current span.

### Request Example
```python
# Assuming 'span' is an instance of the Span class
provider.on_span_start(span)
```

### Response
#### Success Response (None)
This method does not return a value.

## on_span_end

### Description
Called when a span is finished.

### Method
This is a method within a class, likely a tracing provider.

### Endpoint
N/A (Internal method)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **span** (Span[Any]) - Required - The span object representing the finished span.

### Request Example
```python
# Assuming 'span' is an instance of the Span class
provider.on_span_end(span)
```

### Response
#### Success Response (None)
This method does not return a value.
```

--------------------------------

### Generate Agent Instructions from MCP Server Prompts

Source: https://openai.github.io/openai-agents-python/mcp

MCP servers can provide dynamic prompts to generate agent instructions. Use `get_prompt` to fetch a prompt template with optional arguments, which can then be used to initialize an agent.

```python
from agents import Agent

prompt_result = await server.get_prompt(
    "generate_code_review_instructions",
    {"focus": "security vulnerabilities", "language": "python"},
)
instructions = prompt_result.messages[0].content.text

agent = Agent(
    name="Code Reviewer",
    instructions=instructions,
    mcp_servers=[server],
)


```

--------------------------------

### Get Speech-to-Text Model

Source: https://openai.github.io/openai-agents-python/ko/ref/voice/models/openai_model_provider

Retrieves a speech-to-text model by its name. If no model name is provided, a default model will be returned.

```APIDOC
## GET /voice/models/openai/stt

### Description
Retrieves a speech-to-text (STT) model by its name. If `model_name` is not specified, a default STT model is used.

### Method
GET

### Endpoint
/voice/models/openai/stt

### Parameters
#### Query Parameters
- **model_name** (str) - Optional - The name of the speech-to-text model to retrieve. Defaults to a predefined model if not provided.

### Request Example
```
GET /voice/models/openai/stt?model_name=whisper-1
```

### Response
#### Success Response (200)
- **model_type** (str) - The type of the STT model (e.g., "OpenAISTTModel").
- **model_name** (str) - The name of the retrieved STT model.

#### Response Example
```json
{
  "model_type": "OpenAISTTModel",
  "model_name": "whisper-1"
}
```
```

--------------------------------

### Implement Span with Tracing Functionality in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/spans

This Python code defines the SpanImpl class, which extends the Span base class. It manages trace and span IDs, start and end times, and associated span data. The class integrates with a TracingProcessor to handle span start and end events and supports context management for current spans.

```python
class SpanImpl(Span[TSpanData]):
    __slots__ = (
        "_trace_id",
        "_span_id",
        "_parent_id",
        "_started_at",
        "_ended_at",
        "_error",
        "_prev_span_token",
        "_processor",
        "_span_data",
        "_tracing_api_key",
    )

    def __init__(
        self,
        trace_id: str,
        span_id: str | None,
        parent_id: str | None,
        processor: TracingProcessor,
        span_data: TSpanData,
        tracing_api_key: str | None,
    ):
        self._trace_id = trace_id
        self._span_id = span_id or util.gen_span_id()
        self._parent_id = parent_id
        self._started_at: str | None = None
        self._ended_at: str | None = None
        self._processor = processor
        self._error: SpanError | None = None
        self._prev_span_token: contextvars.Token[Span[TSpanData] | None] | None = None
        self._span_data = span_data
        self._tracing_api_key = tracing_api_key

    @property
    def trace_id(self) -> str:
        return self._trace_id

    @property
    def span_id(self) -> str:
        return self._span_id

    @property
    def span_data(self) -> TSpanData:
        return self._span_data

    @property
    def parent_id(self) -> str | None:
        return self._parent_id

    def start(self, mark_as_current: bool = False):
        if self.started_at is not None:
            logger.warning("Span already started")
            return

        self._started_at = util.time_iso()
        self._processor.on_span_start(self)
        if mark_as_current:
            self._prev_span_token = Scope.set_current_span(self)

    def finish(self, reset_current: bool = False) -> None:
        if self.ended_at is not None:
            logger.warning("Span already finished")
            return

        self._ended_at = util.time_iso()
        self._processor.on_span_end(self)
        if reset_current and self._prev_span_token is not None:
            Scope.reset_current_span(self._prev_span_token)
            self._prev_span_token = None

    def __enter__(self) -> Span[TSpanData]:
        self.start(mark_as_current=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        reset_current = True
        if exc_type is GeneratorExit:
            logger.debug("GeneratorExit, skipping span reset")
            reset_current = False

        self.finish(reset_current=reset_current)

    def set_error(self, error: SpanError) -> None:
        self._error = error

    @property
    def error(self) -> SpanError | None:
        return self._error

    @property
    def started_at(self) -> str | None:
        return self._started_at

    @property
    def ended_at(self) -> str | None:
        return self._ended_at

    @property
    def tracing_api_key(self) -> str | None:
        return self._tracing_api_key

    def export(self) -> dict[str, Any] | None:
        return {
            "object": "trace.span",
            "id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self._parent_id,
            "started_at": self._started_at,
            "ended_at": self._ended_at,
            "span_data": self.span_data.export(),
            "error": self._error,
        }

```

--------------------------------

### on_start Method for Voice Workflow Initialization

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/workflow

The async on_start method in VoiceWorkflowBase is an optional hook that runs before any user input is processed. It can be used to deliver introductory messages or instructions via text-to-speech. The default implementation yields nothing, indicating no action is taken.

```python
async def on_start(self) -> AsyncIterator[str]:
    """
    Optional method that runs before any user input is received. Can be used
    to deliver a greeting or instruction via TTS. Defaults to doing nothing.
    """
    return
    yield
```

--------------------------------

### Get Function Tools

Source: https://openai.github.io/openai-agents-python/ko/ref/mcp/util

Retrieves all function tools from a single MCP server. It fetches the tools and then converts them into the Agents SDK's FunctionTool format.

```APIDOC
## GET /servers/{server_name}/tools

### Description
Get all function tools from a single MCP server. This method fetches tools from the specified server and converts them into a format compatible with the Agents SDK.

### Method
GET

### Endpoint
/servers/{server_name}/tools

### Parameters
#### Path Parameters
- **server_name** (string) - Required - The name of the MCP server to retrieve tools from.

#### Query Parameters
- **convert_schemas_to_strict** (bool) - Required - Flag to determine if input schemas should be converted to a strict JSON schema format.
- **run_context** (RunContextWrapper[Any]) - Required - The context for the current run operation.
- **agent** (AgentBase) - Required - The agent instance performing the operation.

### Response
#### Success Response (200)
- **tools** (list[Tool]) - A list of function tools available on the specified server.

#### Response Example
```json
[
  {
    "name": "another_tool",
    "description": "Another example tool",
    "params_json_schema": {},
    "on_invoke_tool": "<function>",
    "strict_json_schema": true
  }
]
```
```

--------------------------------

### Span Lifecycle Methods

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing

Methods for managing the lifecycle of a span, including starting and finishing.

```APIDOC
## Span Lifecycle Methods

Methods to control the start and end of a span.

### `start`

*   **Description**: Starts the span. Optionally marks it as the current span.
*   **Parameters**:
    *   `mark_as_current` (bool): If true, the span will be marked as the current span. Defaults to `False`.

### `finish`

*   **Description**: Finishes the span. Optionally resets the current span.
*   **Parameters**:
    *   `reset_current` (bool): If true, the span will be reset as the current span. Defaults to `False`.
*   **Returns**: `None`
```

--------------------------------

### Run Agent Workflow (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/run

Executes an agent workflow starting from a specified agent. The workflow continues until a final output is produced, handling agent handoffs and tool calls. It includes error handling for exceeding maximum turns or triggering guardrails. Key parameters include the starting agent, initial input, context, maximum turns, and optional configurations for conversation management and callbacks.

```python
async def run(
    starting_agent: Agent[TContext],
    input: str | list[TResponseInputItem],
    *,
    context: TContext | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
    hooks: RunHooks[TContext] | None = None,
    run_config: RunConfig | None = None,
    previous_response_id: str | None = None,
    auto_previous_response_id: bool = False,
    conversation_id: str | None = None,
    session: Session | None = None,
) -> RunResult:
    """
    Run a workflow starting at the given agent.

    The agent will run in a loop until a final output is generated. The loop runs like so:

      1. The agent is invoked with the given input.
      2. If there is a final output (i.e. the agent produces something of type
         `agent.output_type`), the loop terminates.
      3. If there's a handoff, we run the loop again, with the new agent.
      4. Else, we run tool calls (if any), and re-run the loop.

    In two cases, the agent may raise an exception:

      1. If the max_turns is exceeded, a MaxTurnsExceeded exception is raised.
      2. If a guardrail tripwire is triggered, a GuardrailTripwireTriggered
         exception is raised.

    Note:
        Only the first agent's input guardrails are run.

    Args:
        starting_agent: The starting agent to run.
        input: The initial input to the agent. You can pass a single string for a
            user message, or a list of input items.
        context: The context to run the agent with.
        max_turns: The maximum number of turns to run the agent for. A turn is
    """
    pass
```

--------------------------------

### Initialize OpenAI Voice Model Provider (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/models/openai_model_provider

Initializes a new OpenAI voice model provider. It can accept an API key, base URL, an existing OpenAI client, organization, and project. If an OpenAI client is provided, API key and base URL should not be. Otherwise, a new client is created using the provided credentials.

```python
def __init__(
    self,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    openai_client: AsyncOpenAI | None = None,
    organization: str | None = None,
    project: str | None = None,
) -> None:
    """Create a new OpenAI voice model provider.

    Args:
        api_key: The API key to use for the OpenAI client. If not provided, we will use the
            default API key.
        base_url: The base URL to use for the OpenAI client. If not provided, we will use the
            default base URL.
        openai_client: An optional OpenAI client to use. If not provided, we will create a new
            OpenAI client using the api_key and base_url.
        organization: The organization to use for the OpenAI client.
        project: The project to use for the OpenAI client.
    """
    if openai_client is not None:
        assert api_key is None and base_url is None,
            "Don't provide api_key or base_url if you provide openai_client"
        self._client: AsyncOpenAI | None = openai_client
    else:
        self._client = None
        self._stored_api_key = api_key
        self._stored_base_url = base_url
        self._stored_organization = organization
        self._stored_project = project

```

--------------------------------

### GET /tools/mcp

Source: https://openai.github.io/openai-agents-python/ja/ref/agent

Fetches the available tools from the MCP servers. This endpoint retrieves a list of tools that are managed by the MCP (Multi-Cloud Platform) service.

```APIDOC
## GET /tools/mcp

### Description
Fetches the available tools from the MCP servers.

### Method
GET

### Endpoint
/tools/mcp

### Parameters
#### Query Parameters
- **run_context** (RunContextWrapper) - Required - The context for the current run.

### Request Example
```json
{
  "run_context": "<RunContextWrapper object>"
}
```

### Response
#### Success Response (200)
- **tools** (list[Tool]) - A list of available tools from MCP servers.

#### Response Example
```json
[
  {
    "name": "example_tool",
    "description": "An example tool",
    "parameters": {},
    "return_direct": false
  }
]
```
```

--------------------------------

### Span Lifecycle Management - Python

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing/spans

Provides methods for managing the lifecycle of a SpanImpl instance. The `start` method records the start time and notifies the processor, optionally setting the span as the current one. The `finish` method records the end time, notifies the processor, and optionally resets the current span context.

```python
def start(self, mark_as_current: bool = False):
    if self.started_at is not None:
        logger.warning("Span already started")
        return

    self._started_at = util.time_iso()
    self._processor.on_span_start(self)
    if mark_as_current:
        self._prev_span_token = Scope.set_current_span(self)

def finish(self, reset_current: bool = False) -> None:
    if self.ended_at is not None:
        logger.warning("Span already finished")
        return

    self._ended_at = util.time_iso()
    self._processor.on_span_end(self)
    if reset_current and self._prev_span_token is not None:
        Scope.reset_current_span(self._prev_span_token)
        self._prev_span_token = None
```

--------------------------------

### Abstract Span Start Callback - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing

Defines the `on_span_start` method, invoked synchronously when a new span begins. Implementations should execute quickly and avoid blocking, as spans are automatically nested within the current trace or span.

```python
@abc.abstractmethod
def on_span_start(self, span: "Span[Any]") -> None:
    """Called when a new span begins execution.

    Args:
        span: The span that started. Contains operation details and context.

    Notes:
        - Called synchronously on span start
        - Should return quickly to avoid blocking execution
        - Spans are automatically nested under current trace/span
    """
    pass

```

--------------------------------

### Initialize OpenAI Voice Model Provider (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/models/openai_provider

Initializes the OpenAI voice model provider. It can be configured with an API key, base URL, organization, and project, or by providing an existing AsyncOpenAI client. If an OpenAI client is provided, API key and base URL should not be specified.

```python
def __init__(
    self,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    openai_client: AsyncOpenAI | None = None,
    organization: str | None = None,
    project: str | None = None,
) -> None:
    """Create a new OpenAI voice model provider.

    Args:
        api_key: The API key to use for the OpenAI client. If not provided, we will use the
            default API key.
        base_url: The base URL to use for the OpenAI client. If not provided, we will use the
            default base URL.
        openai_client: An optional OpenAI client to use. If not provided, we will create a new
            OpenAI client using the api_key and base_url.
        organization: The organization to use for the OpenAI client.
        project: The project to use for the OpenAI client.
    """
    if openai_client is not None:
        assert api_key is None and base_url is None,
            ("Don't provide api_key or base_url if you provide openai_client")
        self._client: AsyncOpenAI | None = openai_client
    else:
        self._client = None
        self._stored_api_key = api_key
        self._stored_base_url = base_url
        self._stored_organization = organization
        self._stored_project = project

```

--------------------------------

### Get Speech-to-Text Model

Source: https://openai.github.io/openai-agents-python/ko/ref/voice/models/openai_provider

Retrieves a speech-to-text model by its name. If no name is provided, a default model will be returned.

```APIDOC
## get_stt_model

### Description
Get a speech-to-text model by name. If no name is provided, a default model will be returned.

### Method
GET

### Endpoint
/websites/openai_github_io_openai-agents-python/stt_models

### Parameters
#### Path Parameters
None

#### Query Parameters
- **model_name** (str | None) - Required - The name of the model to get.

#### Request Body
None

### Request Example
```
GET /websites/openai_github_io_openai-agents-python/stt_models?model_name=whisper-1
```

### Response
#### Success Response (200)
- **STTModel** (STTModel) - The speech-to-text model.

#### Response Example
```json
{
  "model_type": "OpenAISTTModel",
  "model_name": "whisper-1"
}
```
```

--------------------------------

### Create Speech Group Span - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/create

Creates a new speech group span. This span is not started automatically; users must either use a `with` statement or manually call `start()` and `finish()` on the returned span object. It accepts input text, an optional span ID, a parent trace or span, and a disabled flag.

```Python
def speech_group_span(
    input: str | None = None,
    span_id: str | None = None,
    parent: Trace | Span[Any] | None = None,
    disabled: bool = False,
) -> Span[SpeechGroupSpanData]:
    """Create a new speech group span. The span will not be started automatically, you should
    either do `with speech_group_span() ...` or call `span.start()` + `span.finish()` manually.

    Args:
        input: The input text used for the speech request.
        span_id: The ID of the span. Optional. If not provided, we will generate an ID. We
            recommend using `util.gen_span_id()` to generate a span ID, to guarantee that IDs are
            correctly formatted.
        parent: The parent span or trace. If not provided, we will automatically use the current
            trace/span as the parent.
        disabled: If True, we will return a Span but the Span will not be recorded.
    """
    return get_trace_provider().create_span(
        span_data=SpeechGroupSpanData(input=input),
        span_id=span_id,
        parent=parent,
        disabled=disabled,
    )
```

--------------------------------

### Orchestrating Agents with Tools in Python

Source: https://openai.github.io/openai-agents-python/tools

This example demonstrates how to use multiple specialized agents orchestrated by a central agent. The orchestrator agent uses the specialized agents as tools to perform translations. It requires the 'agents' and 'asyncio' libraries.

```python
from agents import Agent, Runner
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You translate the user's message to Spanish",
)

french_agent = Agent(
    name="French agent",
    instructions="You translate the user's message to French",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate."
        "If asked for multiple translations, you call the relevant tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the user's message to French",
        ),
    ],
)

async def main():
    result = await Runner.run(orchestrator_agent, input="Say 'Hello, how are you?' in Spanish.")
    print(result.final_output)


```

--------------------------------

### Python Session Management: Add and Pop Items

Source: https://openai.github.io/openai-agents-python/ref/memory/openai_responses_compaction_session

Demonstrates how to extend session items and asynchronously pop an item from the session. Popping an item may reset internal caches for compaction candidates and session items.

```python
self._session_items.extend(items)

    async def pop_item(self) -> TResponseInputItem | None:
        popped = await self.underlying_session.pop_item()
        if popped:
            self._compaction_candidate_items = None
            self._session_items = None
        return popped
```

--------------------------------

### VoiceStreamEventLifecycle

Source: https://openai.github.io/openai-agents-python/ref/voice/events

Represents a lifecycle event streamed from the VoicePipeline, indicating the start or end of a turn or session.

```APIDOC
## VoiceStreamEventLifecycle

### Description
Streaming event from the VoicePipeline indicating a lifecycle change.

### Method
N/A (Event Type)

### Endpoint
N/A (Event Type)

### Parameters
#### Request Body
N/A

### Request Example
```json
{
  "type": "voice_stream_event_lifecycle",
  "event": "turn_started"
}
```

### Response
#### Success Response (200)
- **event** (Literal["turn_started", "turn_ended", "session_ended"]) - The lifecycle event that occurred.
- **type** (Literal["voice_stream_event_lifecycle"]) - The type of event, always 'voice_stream_event_lifecycle'.

#### Response Example
```json
{
  "type": "voice_stream_event_lifecycle",
  "event": "turn_ended"
}
```
```

--------------------------------

### Manual Conversation Management with Runner.run

Source: https://openai.github.io/openai-agents-python/running_agents

Demonstrates how to manage a multi-turn conversation manually using the `Runner.run` method. It shows how to capture the result of one turn and use it as input for the next, including adding new user input. This example requires the `openai` and `langchain_core` libraries.

```python
from openai import OpenAI
from langchain_core.agents import AgentExecutor
from langchain_core.runnables import RunnableSequence
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages, BaseMessage
from typing import List, Dict, Any

# Mock Agent and Runner for demonstration purposes
class MockAgent:
    def __init__(self, name, instructions):
        self.name = name
        self.instructions = instructions

    async def __call__(self, messages: List[Dict[str, str]]):
        # Simulate agent thinking and tool use
        last_message = messages[-1]
        if "Golden Gate Bridge" in last_message['content']:
            return {"messages": [{"role": "assistant", "content": "San Francisco"}]},
        elif "state" in last_message['content']:
            return {"messages": [{"role": "assistant", "content": "California"}]}
        else:
            return {"messages": [{"role": "assistant", "content": "I don't understand."}]}

class MockRunner:
    @staticmethod
    async def run(agent, input_data):
        # Simulate a run, returning a mock result object
        if isinstance(input_data, str):
            input_data = [{"role": "user", "content": input_data}]
        
        # Simulate agent processing
        agent_output = await agent(input_data)
        
        # Mock RunResultBase
        class MockRunResult:
            def __init__(self, final_output, messages):
                self.final_output = final_output
                self.messages = messages

            def to_input_list(self):
                # Simulate converting to input list for next turn
                return self.messages

        return MockRunResult(agent_output['messages'][-1]['content'], agent_output['messages'])

# --- Actual example code ---    
async def main():
    agent = MockAgent(name="Assistant", instructions="Reply very concisely.")

    thread_id = "thread_123"  # Example thread ID
    # In a real scenario, you would use a tracing library like 'trace'
    # For this example, we'll skip the actual trace context manager
    # with trace(workflow_name="Conversation", group_id=thread_id):
    
    # First turn
    result = await MockRunner.run(agent, "What city is the Golden Gate Bridge in?")
    print(result.final_output)
    # Expected output: San Francisco

    # Second turn
    # Manually construct the input for the next turn
    new_input = result.to_input_list() + [{"role": "user", "content": "What state is it in?"}]
    result = await MockRunner.run(agent, new_input)
    print(result.final_output)
    # Expected output: California

# To run this example:
# import asyncio
# asyncio.run(main())

```

--------------------------------

### GET /agents/tools

Source: https://openai.github.io/openai-agents-python/ja/ref/agent

Retrieves a list of all available agent tools, including both MCP tools and function tools. This endpoint allows you to discover the capabilities of the agent.

```APIDOC
## GET /agents/tools

### Description
Retrieves all agent tools, including MCP tools and function tools.

### Method
GET

### Endpoint
/agents/tools

### Parameters
#### Query Parameters
- **run_context** (RunContextWrapper) - Required - The context for the current run.

### Request Example
```json
{
  "run_context": { ... } 
}
```

### Response
#### Success Response (200)
- **tools** (list[Tool]) - A list of available Tool objects.

#### Response Example
```json
{
  "tools": [
    {
      "name": "tool_name_1",
      "description": "description_of_tool_1"
    },
    {
      "name": "tool_name_2",
      "description": "description_of_tool_2"
    }
  ]
}
```
```

--------------------------------

### Get System Prompt Dynamically (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/agent

Asynchronously retrieves the system prompt for the agent. It handles both static string instructions and dynamically generated instructions from a callable function, returning the appropriate prompt or None if not defined.

```python
async def get_system_prompt(self, run_context: RunContextWrapper[TContext]) -> str | None:
    """Get the system prompt for the agent."""
    if isinstance(self.instructions, str):
        return self.instructions
    elif callable(self.instructions):
        if inspect.iscoroutinefunction(self.instructions):
            return await cast(Awaitable[str], self.instructions(run_context, self))
        else:
            return cast(str, self.instructions(run_context, self))
    elif self.instructions is not None:
        logger.error(f"Instructions must be a string or a function, got {self.instructions}")

    return None
```

--------------------------------

### GET /get_tts_model

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/model

Retrieves a text-to-speech model by its specified name.

```APIDOC
## GET /get_tts_model

### Description
Get a text-to-speech model by name.

### Method
GET

### Endpoint
/get_tts_model

### Parameters
#### Path Parameters
None

#### Query Parameters
- **model_name** (str | None) - Required - The name of the model to get.

### Request Example
```json
{
  "model_name": "your_model_name"
}
```

### Response
#### Success Response (200)
- **model** (TTSModel) - The text-to-speech model.

#### Response Example
```json
{
  "model": "TTSModel object"
}
```
```

--------------------------------

### Basic Trace Usage with Context Manager (Python)

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/traces

Illustrates the fundamental usage of the `trace` context manager for instrumenting a workflow. This basic example focuses on naming the trace and ensuring proper execution and cleanup of the traced operation.

```python
from openai_agents.tracing import trace

# Assuming Runner, validator, order_data, and processor are defined elsewhere

with trace("Order Processing") as t:
    validation_result = await Runner.run(validator, order_data)
    if validation_result.approved:
        await Runner.run(processor, order_data)
```

--------------------------------

### Get Session Usage

Source: https://openai.github.io/openai-agents-python/ko/ref/extensions/memory/advanced_sqlite_session

Retrieves cumulative usage statistics for a session, either for all branches or a specific branch if provided.

```APIDOC
## GET /session/usage

### Description
Get cumulative usage for session or specific branch.

### Method
GET

### Endpoint
/session/usage

### Parameters
#### Query Parameters
- **branch_id** (str) - Optional - If provided, only get usage for that branch. If None, get all branches.

### Response
#### Success Response (200)
- **requests** (int) - Total number of requests.
- **input_tokens** (int) - Total input tokens.
- **output_tokens** (int) - Total output tokens.
- **total_tokens** (int) - Total tokens (input + output).
- **total_turns** (int) - Total number of turns in the session.

#### Response Example
```json
{
  "requests": 100,
  "input_tokens": 5000,
  "output_tokens": 7500,
  "total_tokens": 12500,
  "total_turns": 50
}
```

#### Error Response (e.g., 404)
```json
{
  "message": "No usage data found."
}
```
```

--------------------------------

### GET /get_stt_model

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/model

Retrieves a speech-to-text model by its specified name.

```APIDOC
## GET /get_stt_model

### Description
Get a speech-to-text model by name.

### Method
GET

### Endpoint
/get_stt_model

### Parameters
#### Path Parameters
None

#### Query Parameters
- **model_name** (str | None) - Required - The name of the model to get.

### Request Example
```json
{
  "model_name": "your_model_name"
}
```

### Response
#### Success Response (200)
- **model** (STTModel) - The speech-to-text model.

#### Response Example
```json
{
  "model": "STTModel object"
}
```
```

--------------------------------

### Trace Start Event

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/provider

Callback function invoked when a new trace begins. It iterates through registered processors and calls their respective `on_trace_start` method.

```APIDOC
## on_trace_start

### Description
Called when a trace is started. This method iterates through all registered trace processors and invokes their `on_trace_start` method, handling potential exceptions during the process.

### Method
This appears to be a method within a class, likely related to tracing.

### Endpoint
N/A (Internal method)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
*   **trace** (Trace) - Required - The trace object representing the current trace session.

### Request Example
```json
{
  "trace": { ... Trace object details ... }
}
```

### Response
#### Success Response (None)
This method returns `None`.

#### Response Example
None
```

--------------------------------

### Handoff Span API

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing

Creates a new handoff span. This span is not started automatically; manual start/finish or a `with` statement is required.

```APIDOC
## POST /agents/tracing/handoff_span

### Description
Creates a new handoff span to track the transition of control between agents. The span requires manual management for starting and finishing, either through a `with` statement or explicit `start()` and `finish()` calls.

### Method
POST

### Endpoint
`/agents/tracing/handoff_span`

### Parameters
#### Query Parameters
- **from_agent** (str | None) - Optional - The name of the agent initiating the handoff.
- **to_agent** (str | None) - Optional - The name of the agent receiving the handoff.
- **span_id** (str | None) - Optional - The ID for the span. If not provided, a unique ID will be generated. It is recommended to use `util.gen_span_id()` for consistent formatting.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If omitted, the current trace/span will be used as the parent.
- **disabled** (bool) - Optional - If set to `True`, the created span will not be recorded. Defaults to `False`.

### Request Example
```json
{
  "from_agent": "AgentA",
  "to_agent": "AgentB",
  "span_id": "generated-span-id",
  "parent": null,
  "disabled": false
}
```

### Response
#### Success Response (200)
- **span** (Span[HandoffSpanData]) - The newly created handoff span object, which can be used to manage its lifecycle.

#### Response Example
```json
{
  "span": {
    "span_id": "generated-span-id",
    "span_data": {
      "from_agent": "AgentA",
      "to_agent": "AgentB"
    }
  }
}
```
```

--------------------------------

### GET /agents/agent_output/name

Source: https://openai.github.io/openai-agents-python/ja/ref/agent_output

Retrieves the name of the output type. This is a simple getter method.

```APIDOC
## GET /agents/agent_output/name

### Description
Retrieves the name of the output type.

### Method
GET

### Endpoint
/agents/agent_output/name

### Parameters
(No parameters are required for this endpoint)

### Request Body
(No request body is expected for this endpoint)

### Response
#### Success Response (200)
- **name** (string) - The name of the output type.

#### Response Example
```json
{
  "name": "string_output_type"
}
```
```

--------------------------------

### Span Start Event

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/provider

Callback function triggered when a new span begins within a trace. It calls the `on_span_start` method on each registered processor.

```APIDOC
## on_span_start

### Description
Called when a span is started. This method iterates through all registered trace processors and invokes their `on_span_start` method, handling potential exceptions.

### Method
This appears to be a method within a class, likely related to tracing.

### Endpoint
N/A (Internal method)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
*   **span** (Span[Any]) - Required - The span object representing the current span.

### Request Example
```json
{
  "span": { ... Span object details ... }
}
```

### Response
#### Success Response (None)
This method returns `None`.

#### Response Example
None
```

--------------------------------

### Initialize OpenAIVoiceModelProvider in Python

Source: https://openai.github.io/openai-agents-python/ref/voice/models/openai_provider

Initializes the OpenAIVoiceModelProvider, which uses OpenAI models. It can accept an existing OpenAI client or configuration parameters like API key and base URL to create a new client. Lazy loading of the client is implemented to avoid errors when no API key is set.

```python
class OpenAIVoiceModelProvider(VoiceModelProvider):
    """A voice model provider that uses OpenAI models."""

    def __init__(
        self,
        *, 
        api_key: str | None = None,
        base_url: str | None = None,
        openai_client: AsyncOpenAI | None = None,
        organization: str | None = None,
        project: str | None = None,
    ) -> None:
        """Create a new OpenAI voice model provider.

        Args:
            api_key: The API key to use for the OpenAI client. If not provided, we will use the
                default API key.
            base_url: The base URL to use for the OpenAI client. If not provided, we will use the
                default base URL.
            openai_client: An optional OpenAI client to use. If not provided, we will create a new
                OpenAI client using the api_key and base_url.
            organization: The organization to use for the OpenAI client.
            project: The project to use for the OpenAI client.
        """
        if openai_client is not None:
            assert api_key is None and base_url is None,
            ("Don't provide api_key or base_url if you provide openai_client")
            self._client: AsyncOpenAI | None = openai_client
        else:
            self._client = None
            self._stored_api_key = api_key
            self._stored_base_url = base_url
            self._stored_organization = organization
            self._stored_project = project
```

--------------------------------

### Tool Start Callback in Python

Source: https://openai.github.io/openai-agents-python/ko/ref/lifecycle

The `on_tool_start` asynchronous method in `RunHooksBase` is called immediately before a local tool is invoked. It provides the context, the agent using the tool, and the tool itself, allowing for pre-execution logic.

```python
async def on_tool_start(
    context: RunContextWrapper[TContext],
    agent: TAgent,
    tool: Tool,
) -> None:
    pass
```

--------------------------------

### Initialize OpenAI Provider (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/models/multi_provider

Initializes a new OpenAI provider with optional configurations for API key, base URL, client, organization, project, and response usage. It allows for a default provider map or a custom one to be provided.

```python
def __init__(
    self,
    *,
    provider_map: MultiProviderMap | None = None,
    openai_api_key: str | None = None,
    openai_base_url: str | None = None,
    openai_client: AsyncOpenAI | None = None,
    openai_organization: str | None = None,
    openai_project: str | None = None,
    openai_use_responses: bool | None = None,
) -> None:
    """Create a new OpenAI provider.

    Args:
        provider_map: A MultiProviderMap that maps prefixes to ModelProviders. If not provided,
            we will use a default mapping. See the documentation for this class to see the
            default mapping.
        openai_api_key: The API key to use for the OpenAI provider. If not provided, we will use
            the default API key.
        openai_base_url: The base URL to use for the OpenAI provider. If not provided, we will
            use the default base URL.
        openai_client: An optional OpenAI client to use. If not provided, we will create a new
            OpenAI client using the api_key and base_url.
        openai_organization: The organization to use for the OpenAI provider.
        openai_project: The project to use for the OpenAI provider.
        openai_use_responses: Whether to use the OpenAI responses API.
    """
    self.provider_map = provider_map
    self.openai_provider = OpenAIProvider(
        api_key=openai_api_key,
        base_url=openai_base_url,
        openai_client=openai_client,
        organization=openai_organization,
        project=openai_project,
        use_responses=openai_use_responses,
    )

    self._fallback_providers: dict[str, ModelProvider] = {}

```

--------------------------------

### Configure Agent Prompt (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/agent

Allows dynamic configuration of an agent's instructions, tools, and other settings using a Prompt object. This feature is specifically for agents utilizing OpenAI models, enabling external configuration of agent behavior.

```python
prompt: Prompt | None = None
```

--------------------------------

### Basic Trace Usage in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing

Illustrates the fundamental usage of the `trace` context manager for tracking a workflow named 'Order Processing'. It shows how to initiate a trace and execute operations within its scope, ensuring that all actions are recorded for analysis. This basic example sets the foundation for more advanced tracing scenarios.

```python
from agents.tracing.traces import trace

# ... Runner, validator, and processor definitions ...

with trace("Order Processing") as t:
    validation_result = await Runner.run(validator, order_data)
    if validation_result.approved:
        await Runner.run(processor, order_data)
```

--------------------------------

### Create Streams API

Source: https://openai.github.io/openai-agents-python/zh/ref/mcp/server

Creates the necessary streams for the server connection. This method is part of the server setup process.

```APIDOC
## POST /websites/openai_github_io_openai-agents-python/create_streams

### Description
Creates the streams for the server. This method is used internally to set up communication channels.

### Method
POST

### Endpoint
/websites/openai_github_io_openai-agents-python/create_streams

### Parameters
#### Query Parameters
- **url** (string) - Required - The URL for the server connection.
- **headers** (object) - Optional - Headers to include in the server request.
- **timeout** (integer) - Optional - Timeout in seconds for the initial connection.
- **sse_read_timeout** (integer) - Optional - Timeout in seconds for reading Server-Sent Events.

### Request Body
This endpoint does not expect a request body.

### Response
#### Success Response (200)
- **stream_tuple** (tuple) - A tuple containing the receive stream, send stream, and an optional session ID callback.

#### Response Example
```json
{
  "stream_tuple": [
    "<ReceiveStreamObject>",
    "<SendStreamObject>",
    "<GetSessionIdCallbackObject> | null"
  ]
}
```
```

--------------------------------

### Define and Use a Guardrail (Python)

Source: https://openai.github.io/openai-agents-python/quickstart

This Python snippet defines a 'Guardrail check' agent and a custom guardrail function `homework_guardrail`. It uses Pydantic for output type definition and the `Runner` to execute the guardrail logic, checking if a user query is homework-related.

```python
from agents import GuardrailFunctionOutput, Agent, Runner
from pydantic import BaseModel


class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )
```

--------------------------------

### Get Realtime Session Configuration Details (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/openai_realtime

Retrieves and constructs the session configuration for a realtime OpenAI agent session. This method processes various audio input and output parameters, including format, noise reduction, transcription, turn detection, and voice settings, applying defaults where necessary. It ensures all required parameters are correctly formatted for the OpenAI API.

```python
def _get_session_config(
        self,
        model_settings: RealtimeSessionModelSettings
    ) -> OpenAISessionCreateRequest:
        """Get the session config."""
        audio_input_args: dict[str, Any] = {}
        audio_output_args: dict[str, Any] = {}

        audio_config = model_settings.get("audio")
        audio_config_mapping = audio_config if isinstance(audio_config, Mapping) else None
        input_audio_config: Mapping[str, Any] = (
            cast(Mapping[str, Any], audio_config_mapping.get("input", {}))
            if audio_config_mapping
            else {}
        )
        output_audio_config: Mapping[str, Any] = (
            cast(Mapping[str, Any], audio_config_mapping.get("output", {}))
            if audio_config_mapping
            else {}
        )

        input_format_source: FormatInput = (
            input_audio_config.get("format") if input_audio_config else None
        )
        if input_format_source is None:
            if self._call_id:
                input_format_source = model_settings.get("input_audio_format")
            else:
                input_format_source = model_settings.get(
                    "input_audio_format", DEFAULT_MODEL_SETTINGS.get("input_audio_format")
                )
        audio_input_args["format"] = to_realtime_audio_format(input_format_source)

        if "noise_reduction" in input_audio_config:
            audio_input_args["noise_reduction"] = input_audio_config.get("noise_reduction")
        elif "input_audio_noise_reduction" in model_settings:
            audio_input_args["noise_reduction"] = model_settings.get("input_audio_noise_reduction")

        if "transcription" in input_audio_config:
            audio_input_args["transcription"] = input_audio_config.get("transcription")
        elif "input_audio_transcription" in model_settings:
            audio_input_args["transcription"] = model_settings.get("input_audio_transcription")
        else:
            audio_input_args["transcription"] = DEFAULT_MODEL_SETTINGS.get(
                "input_audio_transcription"
            )

        if "turn_detection" in input_audio_config:
            audio_input_args["turn_detection"] = self._normalize_turn_detection_config(
                input_audio_config.get("turn_detection")
            )
        elif "turn_detection" in model_settings:
            audio_input_args["turn_detection"] = self._normalize_turn_detection_config(
                model_settings.get("turn_detection")
            )
        else:
            audio_input_args["turn_detection"] = DEFAULT_MODEL_SETTINGS.get("turn_detection")

        requested_voice = output_audio_config.get("voice") if output_audio_config else None
        audio_output_args["voice"] = requested_voice or model_settings.get(
            "voice", DEFAULT_MODEL_SETTINGS.get("voice")
        )

        output_format_source: FormatInput = (
            output_audio_config.get("format") if output_audio_config else None
        )
        if output_format_source is None:
            if self._call_id:
                output_format_source = model_settings.get("output_audio_format")
            else:
                output_format_source = model_settings.get(
                    "output_audio_format", DEFAULT_MODEL_SETTINGS.get("output_audio_format")
                )
        audio_output_args["format"] = to_realtime_audio_format(output_format_source)

        if "speed" in output_audio_config:
            audio_output_args["speed"] = output_audio_config.get("speed")
        elif "speed" in model_settings:
            audio_output_args["speed"] = model_settings.get("speed")

        output_modalities = (
            model_settings.get("output_modalities")
            or model_settings.get("modalities")
            or DEFAULT_MODEL_SETTINGS.get("modalities")
        )

        # Construct full session object. `type` will be excluded at serialization time for updates.
        session_create_request = OpenAISessionCreateRequest(
            type="realtime",
            model=(model_settings.get("model_name") or self.model) or "gpt-realtime",
            output_modalities=output_modalities,
        )
        return session_create_request
```

--------------------------------

### Get Prompt - Python

Source: https://openai.github.io/openai-agents-python/zh/ref/mcp/server

Abstract method to retrieve a specific prompt by name from the server, optionally with arguments. It returns a GetPromptResult.

```python
@abc.abstractmethod
async def get_prompt(
    self, name: str, arguments: dict[str, Any] | None = None
) -> GetPromptResult:
    """Get a specific prompt from the server."""
    pass

```

--------------------------------

### GET /sessions/{session_id}/items

Source: https://openai.github.io/openai-agents-python/ja/ref/memory/session

Retrieve the conversation history for a given session.

```APIDOC
## GET /sessions/{session_id}/items

### Description
Retrieve the conversation history for this session.

### Method
GET

### Endpoint
/sessions/{session_id}/items

### Parameters
#### Path Parameters
- **session_id** (str) - Required - The ID of the session to retrieve history from.

#### Query Parameters
- **limit** (int) - Optional - Maximum number of items to retrieve. If None, retrieves all items. When specified, returns the latest N items in chronological order.

### Request Example
GET /sessions/sess_abc/items?limit=10

### Response
#### Success Response (200)
- **items** (list[TResponseInputItem]) - List of input items representing the conversation history

#### Response Example
{
  "items": [
    {
      "content": "Hello!",
      "role": "user"
    },
    {
      "content": "Hi there!",
      "role": "assistant"
    }
  ]
}
```

--------------------------------

### Create Basic Hosted MCP Tool in Python

Source: https://openai.github.io/openai-agents-python/mcp

Demonstrates how to create a basic hosted MCP tool by adding a `HostedMCPTool` to an agent's tools list. This forwards server labels and metadata to the Responses API, allowing the model to invoke remote tools without direct Python callbacks. Requires the `agents` library and `asyncio`.

```python
import asyncio

from agents import Agent, HostedMCPTool, Runner

async def main() -> None:
    agent = Agent(
        name="Assistant",
        tools=[
            HostedMCPTool(
                tool_config={
                    "type": "mcp",
                    "server_label": "gitmcp",
                    "server_url": "https://gitmcp.io/openai/codex",
                    "require_approval": "never",
                }
            )
        ],
    )

    result = await Runner.run(agent, "Which language is this repository written in?")
    print(result.final_output)

asyncio.run(main())
```

--------------------------------

### Span Processing Methods

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/processor_interface

Methods called during the lifecycle of a span, including when a span starts and ends.

```APIDOC
## POST /websites/openai_github_io_openai-agents-python/on_span_start

### Description
Called when a new span begins execution. This method is synchronous and should return quickly to avoid blocking execution. Spans are automatically nested under the current trace or span.

### Method
POST

### Endpoint
/websites/openai_github_io_openai-agents-python/on_span_start

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **span** (Span[Any]) - Required - The span that started. Contains operation details and context.

### Request Example
```json
{
  "span": {
    "operation_name": "example_operation",
    "context": {},
    "start_time": 1678886400.0
  }
}
```

### Response
#### Success Response (200)
- **status** (string) - Indicates successful processing.

#### Response Example
```json
{
  "status": "processed"
}
```

## POST /websites/openai_github_io_openai-agents-python/on_span_end

### Description
Called when a span completes execution. This method is synchronous, should not block or raise exceptions, and is a good time to export or process the individual span.

### Method
POST

### Endpoint
/websites/openai_github_io_openai-agents-python/on_span_end

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **span** (Span[Any]) - Required - The completed span containing execution results.

### Request Example
```json
{
  "span": {
    "operation_name": "example_operation",
    "context": {},
    "start_time": 1678886400.0,
    "end_time": 1678886460.0,
    "results": {}
  }
}
```

### Response
#### Success Response (200)
- **status** (string) - Indicates successful processing.

#### Response Example
```json
{
  "status": "processed"
}
```
```

--------------------------------

### get_system_prompt Method

Source: https://openai.github.io/openai-agents-python/ref/realtime/agent

Retrieves the system prompt for the agent, dynamically generating it if instructions are provided as a function.

```APIDOC
## GET /get_system_prompt

### Description
Retrieves the system prompt that will be used for the agent. If the `instructions` attribute is a string, it is returned directly. If `instructions` is a callable function, it is invoked with the current run context and agent instance to generate the prompt dynamically.

### Method
GET

### Endpoint
`/get_system_prompt`

### Parameters
#### Query Parameters
- **run_context** (RunContextWrapper) - The wrapper for the current run context, passed to the instructions function if it's dynamic.

### Response
#### Success Response (200)
- **system_prompt** (str | None) - The generated system prompt string, or None if no instructions are configured.
```

--------------------------------

### GET /api/tools/mcp

Source: https://openai.github.io/openai-agents-python/ref/agent

Fetches the available tools from the MCP servers. This endpoint retrieves a list of tools that are managed by the MCP (Multi-Cloud Platform).

```APIDOC
## GET /api/tools/mcp

### Description
Fetches the available tools from the MCP servers.

### Method
GET

### Endpoint
/api/tools/mcp

### Parameters
#### Query Parameters
- **run_context** (RunContextWrapper) - Required - The context for the current run.

### Request Example
```json
{
  "run_context": { ... }
}
```

### Response
#### Success Response (200)
- **tools** (list[Tool]) - A list of available MCP tools.

#### Response Example
```json
{
  "tools": [
    {
      "name": "example_tool",
      "description": "An example tool",
      "parameters": { ... }
    }
  ]
}
```
```

--------------------------------

### Trace Processing Methods

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/processor_interface

Methods called during the lifecycle of a trace, including when a trace starts and ends.

```APIDOC
## POST /websites/openai_github_io_openai-agents-python/on_trace_start

### Description
Called when a new trace begins execution. This method is synchronous and should return quickly to avoid blocking execution.

### Method
POST

### Endpoint
/websites/openai_github_io_openai-agents-python/on_trace_start

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **trace** (Trace) - Required - The trace that started. Contains workflow name and metadata.

### Request Example
```json
{
  "trace": {
    "workflow_name": "example_workflow",
    "metadata": {}
  }
}
```

### Response
#### Success Response (200)
- **status** (string) - Indicates successful processing.

#### Response Example
```json
{
  "status": "processed"
}
```

## POST /websites/openai_github_io_openai-agents-python/on_trace_end

### Description
Called when a trace completes execution. This method is synchronous and is a good time to export or process the complete trace and handle cleanup of any trace-specific resources.

### Method
POST

### Endpoint
/websites/openai_github_io_openai-agents-python/on_trace_end

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **trace** (Trace) - Required - The completed trace containing all spans and results.

### Request Example
```json
{
  "trace": {
    "workflow_name": "example_workflow",
    "metadata": {},
    "spans": [],
    "results": {}
  }
}
```

### Response
#### Success Response (200)
- **status** (string) - Indicates successful processing.

#### Response Example
```json
{
  "status": "processed"
}
```
```

--------------------------------

### MCPServerStdio Constructor

Source: https://openai.github.io/openai-agents-python/ko/ref/mcp/server

Initializes a new instance of the MCPServerStdio class. This constructor sets up the MCP server to communicate via standard input and output, configuring parameters such as the command to execute, arguments, environment variables, and working directory.

```APIDOC
## MCPServerStdio.__init__

### Description
Create a new MCP server based on the stdio transport.

### Method
Constructor

### Endpoint
N/A (Class method)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **params** (MCPServerStdioParams) - Required - The params that configure the server. This includes the command to run to start the server, the args to pass to the command, the environment variables to set for the server, the working directory to use when spawning the process, and the text encoding used when sending/receiving messages to the server.
- **cache_tools_list** (bool) - Optional - Whether to cache the tools list. If `True`, the tools list will be cached and only fetched from the server once. If `False`, the tools list will be fetched from the server on each call to `list_tools()`. The cache can be invalidated by calling `invalidate_tools_cache()`. You should set this to `True` if you know the server will not change its tools list, because it can drastically improve latency (by avoiding a round-trip to the server every time).
- **name** (str | None) - Optional - A readable name for the server. If not provided, we'll create one from the command.
- **client_session_timeout_seconds** (float | None) - Optional - the read timeout passed to the MCP ClientSession. Defaults to 5.
- **tool_filter** (ToolFilter) - Optional - The tool filter to use for filtering tools.
- **use_structured_content** (bool) - Optional - Whether to use `tool_result.structured_content` when calling an MCP tool. Defaults to False for backwards compatibility - most MCP servers still include the structured content in the `tool_result.content`, and using it by default will cause duplicate content. You can set this to True if you know the server will not duplicate the structured content in the `tool_result.content`.
- **max_retry_attempts** (int) - Optional - Number of times to retry failed list_tools/call_tool calls. Defaults to no retries.
- **retry_backoff_seconds_base** (float) - Optional - The base delay, in seconds, for exponential backoff between retries. Defaults to 1.0.
- **message_handler** (MessageHandlerFnT | None) - Optional - Optional handler invoked for session messages as delivered by the ClientSession.

### Request Example
None

### Response
#### Success Response (200)
None

#### Response Example
None
```

--------------------------------

### mcp_tools_span

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing

Creates a new MCP list tools span. This span is not started automatically and requires manual start/finish calls or usage within a 'with' statement.

```APIDOC
## mcp_tools_span

### Description
Creates a new MCP list tools span. The span will not be started automatically, you should either do `with mcp_tools_span() ...` or call `span.start()` + `span.finish()` manually.

### Method
(Not applicable - this is a Python function)

### Endpoint
(Not applicable - this is a Python function)

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
(None)

### Request Example
```python
# Using a 'with' statement
with mcp_tools_span(server="my_server", result=["tool1", "tool2"]):
    # Your code here
    pass

# Manual start and finish
span = mcp_tools_span(server="my_server", result=["tool1", "tool2"])
span.start()
# Your code here
span.finish()
```

### Response
#### Success Response
- **Span** (Span[MCPListToolsSpanData]) - The created MCP list tools span.

#### Response Example
(The response is a Span object, not a JSON payload. Example usage is shown in Request Example.)
```

--------------------------------

### Implement on_start Hook in AgentHooksBase (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/lifecycle

The `on_start` method is an asynchronous hook in `AgentHooksBase`, called before an agent is invoked. This hook is triggered each time the running agent is changed to this specific agent, receiving the agent hook context and the agent instance.

```python
async def on_start(
    context: AgentHookContext[TContext], agent: TAgent
) -> None:
    pass
```

--------------------------------

### generation_span

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing

Creates a new generation span to capture model generation details. This span needs to be explicitly started and finished.

```APIDOC
## POST /generation_span

### Description
Create a new generation span. The span will not be started automatically, you should either do `with generation_span() ...` or call `span.start()` + `span.finish()` manually. This span captures the details of a model generation, including the input message sequence, any generated outputs, the model name and configuration, and usage data. If you only need to capture a model response identifier, use `response_span()` instead.

### Method
POST

### Endpoint
/generation_span

### Parameters
#### Query Parameters
- **input** (Sequence[Mapping[str, Any]] | None) - Optional - The sequence of input messages sent to the model.
- **output** (Sequence[Mapping[str, Any]] | None) - Optional - The sequence of output messages received from the model.
- **model** (str | None) - Optional - The model identifier used for the generation.
- **model_config** (Mapping[str, Any] | None) - Optional - The model configuration (hyperparameters) used.
- **usage** (dict[str, Any] | None) - Optional - A dictionary of usage information (input tokens, output tokens, etc.).
- **span_id** (str | None) - Optional - The ID of the span. Optional. If not provided, we will generate an ID. We recommend using `util.gen_span_id()` to generate a span ID, to guarantee that IDs are correctly formatted.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, we will automatically use the current trace/span as the parent.
- **disabled** (bool) - Optional - If True, we will return a Span but the Span will not be recorded. Default: False

### Response
#### Success Response (200)
- **Span[GenerationSpanData]** - The newly created generation span.

#### Response Example
```json
{
  "example": "Span[GenerationSpanData]"
}
```
```

--------------------------------

### Create Speech Span in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/create

This Python function, speech_span, is designed to create a tracing span for speech-related operations. It accepts various parameters to define the speech model, input text, output format, and associated tracing metadata. The span is not automatically started and requires manual initiation via a `with` statement or explicit `start()` and `finish()` calls. It returns a Span object containing SpeechSpanData.

```python
def speech_span(
    model: str | None = None,
    input: str | None = None,
    output: str | None = None,
    output_format: str | None = "pcm",
    model_config: Mapping[str, Any] | None = None,
    first_content_at: str | None = None,
    span_id: str | None = None,
    parent: Trace | Span[Any] | None = None,
    disabled: bool = False,
) -> Span[SpeechSpanData]:
    """Create a new speech span. The span will not be started automatically, you should either do
    `with speech_span() ...` or call `span.start()` + `span.finish()` manually.

    Args:
        model: The name of the model used for the text-to-speech.
        input: The text input of the text-to-speech.
        output: The audio output of the text-to-speech as base64 encoded string of PCM audio bytes.
        output_format: The format of the audio output (defaults to "pcm").
        model_config: The model configuration (hyperparameters) used.
        first_content_at: The time of the first byte of the audio output.
        span_id: The ID of the span. Optional. If not provided, we will generate an ID. We
            recommend using `util.gen_span_id()` to generate a span ID, to guarantee that IDs are
            correctly formatted.
        parent: The parent span or trace. If not provided, we will automatically use the current
            trace/span as the parent.
        disabled: If True, we will return a Span but the Span will not be recorded.
    """
    return get_trace_provider().create_span(
        span_data=SpeechSpanData(
            model=model,
            input=input,
            output=output,
            output_format=output_format,
            model_config=model_config,
            first_content_at=first_content_at,
        ),
        span_id=span_id,
        parent=parent,
        disabled=disabled,
    )

```

--------------------------------

### Run Agent Workflow in Streaming Mode (Python)

Source: https://openai.github.io/openai-agents-python/ref/run

Executes an agent workflow starting from a specified agent in streaming mode. The method returns a result object with a streaming method for semantic events. It handles agent loops, tool calls, and exceptions such as max turns exceeded or guardrail triggers. Key parameters include the starting agent, initial input, context, maximum turns, and optional hooks for lifecycle events.

```python
from typing import TypeVar, Optional, List

# Assuming Agent, AgentOutput, RunHooks, RunConfig, Session, RunResultStreaming, DEFAULT_MAX_TURNS, TResponseInputItem are defined elsewhere

class Agent:
    # ... (Agent class definition)
    pass

TContext = TypeVar('TContext')

class RunResultStreaming:
    # ... (RunResultStreaming class definition)
    pass

class RunHooks:
    # ... (RunHooks class definition)
    pass

class RunConfig:
    # ... (RunConfig class definition)
    pass

class Session:
    # ... (Session class definition)
    pass

class TResponseInputItem:
    # ... (TResponseInputItem class definition)
    pass

DEFAULT_MAX_TURNS = 10 # Example default value

class YourAgentClass: # Replace with the actual class name
    @classmethod
    def run_streamed(
        cls,
        starting_agent: Agent[TContext],
        input: str | List[TResponseInputItem],
        context: TContext | None = None,
        max_turns: int = DEFAULT_MAX_TURNS,
        hooks: RunHooks[TContext] | None = None,
        run_config: RunConfig | None = None,
        previous_response_id: str | None = None,
        auto_previous_response_id: bool = False,
        conversation_id: str | None = None,
        session: Session | None = None,
    ) -> RunResultStreaming:
        """
        Run a workflow starting at the given agent in streaming mode.

        The returned result object contains a method you can use to stream semantic
        events as they are generated.

        The agent will run in a loop until a final output is generated. The loop runs like so:

          1. The agent is invoked with the given input.
          2. If there is a final output (i.e. the agent produces something of type
             `agent.output_type`), the loop terminates.
          3. If there's a handoff, we run the loop again, with the new agent.
          4. Else, we run tool calls (if any), and re-run the loop.

        In two cases, the agent may raise an exception:

          1. If the max_turns is exceeded, a MaxTurnsExceeded exception is raised.
          2. If a guardrail tripwire is triggered, a GuardrailTripwireTriggered
             exception is raised.

        Note:
            Only the first agent's input guardrails are run.

        Args:
            starting_agent: The starting agent to run.
            input: The initial input to the agent. You can pass a single string for a
                user message, or a list of input items.
            context: The context to run the agent with.
            max_turns: The maximum number of turns to run the agent for. A turn is
                defined as one AI invocation (including any tool calls that might occur).
            hooks: An object that receives callbacks on various lifecycle events.
            run_config: Global settings for the entire agent run.
            previous_response_id: The ID of the previous response, if using OpenAI models via the Responses API, this allows you to skip passing in input from the previous turn.
            auto_previous_response_id: Whether to automatically use the previous response ID.
            conversation_id: The ID of the stored conversation, if any.
            session: A session for automatic conversation history management.

        Returns:
            A result object that contains data about the run, as well as a method to
            stream events.
        """
        # Implementation details would go here
        pass

```

--------------------------------

### GET /api/tools/all

Source: https://openai.github.io/openai-agents-python/ref/agent

Retrieves all agent tools, including both MCP tools and function tools. This endpoint provides a comprehensive list of all tools available to the agent.

```APIDOC
## GET /api/tools/all

### Description
All agent tools, including MCP tools and function tools.

### Method
GET

### Endpoint
/api/tools/all

### Parameters
#### Query Parameters
- **run_context** (RunContextWrapper) - Required - The context for the current run.

### Request Example
```json
{
  "run_context": { ... }
}
```

### Response
#### Success Response (200)
- **tools** (list[Tool]) - A list of all available agent tools.

#### Response Example
```json
{
  "tools": [
    {
      "name": "mcp_tool_example",
      "description": "An example MCP tool",
      "parameters": { ... }
    },
    {
      "name": "function_tool_example",
      "description": "An example function tool",
      "parameters": { ... }
    }
  ]
}
```
```

--------------------------------

### AdvancedSQLiteSession Initialization

Source: https://openai.github.io/openai-agents-python/ko/ref/extensions/memory/advanced_sqlite_session

Initializes the AdvancedSQLiteSession with session details, database path, table creation option, and logger.

```APIDOC
## AdvancedSQLiteSession `__init__`

### Description
Initializes the AdvancedSQLiteSession with session details, database path, table creation option, and logger.

### Method
`__init__`

### Parameters
#### Keyword Parameters
- **session_id** (str) - Required - The ID of the session
- **db_path** (str | Path) - Optional - The path to the SQLite database file. Defaults to `:memory:` for in-memory storage
- **create_tables** (bool) - Optional - Whether to create the structure tables
- **logger** (Logger | None) - Optional - The logger to use. Defaults to the module logger
- **kwargs** () - Optional - Additional keyword arguments to pass to the superclass

### Request Example
```python
# Example Usage:
# from agents.extensions.memory.advanced_sqlite_session import AdvancedSQLiteSession
# session = AdvancedSQLiteSession(session_id="my_session", db_path="my_database.db", create_tables=True)
```

### Response
This is a constructor and does not return a value directly.
```

--------------------------------

### Run Compaction using OpenAIResponsesCompactionArgs in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/memory/openai_responses_compaction_session

The `run_compaction` function executes the compaction process using the `responses.compact` API. It takes an optional `OpenAIResponsesCompactionArgs` object to configure the compaction mode, response ID, and storage behavior. It returns `None` and handles the logic for deciding whether to compact, compacting the responses, and updating the session items.

```python
async def run_compaction(self, args: OpenAIResponsesCompactionArgs | None = None) -> None:
    """Run compaction using responses.compact API."""
    if args and args.get("response_id"):
        self._response_id = args["response_id"]
    requested_mode = args.get("compaction_mode") if args else None
    if args and "store" in args:
        store = args["store"]
        if store is False and self._response_id:
            self._last_unstored_response_id = self._response_id
        elif store is True and self._response_id == self._last_unstored_response_id:
            self._last_unstored_response_id = None
    else:
        store = None
    resolved_mode = self._resolve_compaction_mode_for_response(
        response_id=self._response_id,
        store=store,
        requested_mode=requested_mode,
    )

    if resolved_mode == "previous_response_id" and not self._response_id:
        raise ValueError(
            "OpenAIResponsesCompactionSession.run_compaction requires a response_id "
            "when using previous_response_id compaction."
        )

    compaction_candidate_items, session_items = await self._ensure_compaction_candidates()

    force = args.get("force", False) if args else False
    should_compact = force or self.should_trigger_compaction(
        {
            "response_id": self._response_id,
            "compaction_mode": resolved_mode,
            "compaction_candidate_items": compaction_candidate_items,
            "session_items": session_items,
        }
    )

    if not should_compact:
        logger.debug(
            f"skip: decision hook declined compaction for {self._response_id} "
            f"(mode={resolved_mode})"
        )
        return

    self._deferred_response_id = None
    logger.debug(
        f"compact: start for {self._response_id} using {self.model} (mode={resolved_mode})"
    )

    compact_kwargs: dict[str, Any] = {"model": self.model}
    if resolved_mode == "previous_response_id":
        compact_kwargs["previous_response_id"] = self._response_id
    else:
        compact_kwargs["input"] = session_items

    compacted = await self.client.responses.compact(**compact_kwargs)

    await self.underlying_session.clear_session()
    output_items: list[TResponseInputItem] = []
    if compacted.output:
        for item in compacted.output:
            if isinstance(item, dict):
                output_items.append(item)
            else:
                # Suppress Pydantic literal warnings: responses.compact can return
                # user-style input_text content inside ResponseOutputMessage.
                output_items.append(
                    item.model_dump(exclude_unset=True, warnings=False)  # type: ignore
                )

    if output_items:
        await self.underlying_session.add_items(output_items)

    self._compaction_candidate_items = select_compaction_candidate_items(output_items)
    self._session_items = output_items

    logger.debug(
        f"compact: done for {self._response_id} "
        f"(mode={resolved_mode}, output={len(output_items)}, "
        f"candidates={len(self._compaction_candidate_items)})"
    )

```

--------------------------------

### Span Management Methods API

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/spans

This section details the methods for managing the lifecycle of a span, including starting and finishing its execution.

```APIDOC
## Span Management Methods API

### Description
This API group covers the essential methods for controlling the execution lifecycle of a span within the tracing system.

### Methods

#### `start`

##### Description
Starts the span's execution.

##### Method
`start(mark_as_current: bool = False)`

##### Parameters
- **mark_as_current** (`bool`) - Optional - If true, the span will be marked as the current span. Defaults to `False`.

#### `finish`

##### Description
Finishes the span's execution.

##### Method
`finish(reset_current: bool = False) -> None`

##### Parameters
- **reset_current** (`bool`) - Optional - If true, the span will be reset as the current span. Defaults to `False`.
```

--------------------------------

### Trace Lifecycle Management API

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/traces

Manages the lifecycle of a trace, including starting, finishing, and exporting trace data.

```APIDOC
## Trace Lifecycle Management API

### Description
This API allows for the management of a trace's lifecycle, including initiating a trace, completing it, and exporting its collected data. It also handles the context management of traces.

### Endpoints

#### `start`

##### Description
Start the trace and optionally mark it as the current trace in the execution context.

##### Method
POST

##### Endpoint
`/start`

##### Parameters
* **mark_as_current** (bool) - Optional - If true, marks this trace as the current trace in the execution context. Defaults to `False`.

##### Notes
* Must be called before any spans can be added.
* Only one trace can be current at a time.
* Thread-safe when using `mark_as_current`.

#### `finish`

##### Description
Finish the trace and optionally reset the current trace.

##### Method
POST

##### Endpoint
`/finish`

##### Parameters
* **reset_current** (bool) - Optional - If true, resets the current trace to the previous trace in the execution context. Defaults to `False`.

##### Notes
* Must be called to complete the trace.
* Finalizes all open spans.
* Thread-safe when using `reset_current`.

#### `export`

##### Description
Export the trace data as a serializable dictionary.

##### Method
GET

##### Endpoint
`/export`

##### Response
* **export_data** (dict[str, Any] | None) - A dictionary containing trace data, or None if tracing is disabled. Includes all spans and their data, used for sending traces to backends, and may include metadata and group ID.
```

--------------------------------

### Get ModelProvider by Prefix

Source: https://openai.github.io/openai-agents-python/ko/ref/models/multi_provider

The `get_provider` method retrieves the `ModelProvider` associated with a specific prefix. If the prefix is not found in the map, it returns `None`.

```python
def get_provider(self, prefix: str) -> ModelProvider | None:
    """Returns the ModelProvider for the given prefix.

    Args:
        prefix: The prefix of the model name e.g. "openai" or "my_prefix".
    """
    return self._mapping.get(prefix)
```

--------------------------------

### Customize Python Logging (Python)

Source: https://openai.github.io/openai-agents-python/config

Provides an example of how to customize the SDK's logging behavior by directly interacting with Python's built-in logging module. This allows for fine-grained control over log levels and handlers.

```python
import logging

logger = logging.getLogger("openai.agents") # or openai.agents.tracing for the Tracing logger

# To make all logs show up
logger.setLevel(logging.DEBUG)
# To make info and above show up
logger.setLevel(logging.INFO)
# To make warning and above show up
logger.setLevel(logging.WARNING)
# etc

# You can customize this as needed, but this will output to `stderr` by default
logger.addHandler(logging.StreamHandler())

```

--------------------------------

### MCP Tools Span Creation

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing

Creates a new span for MCP list tools calls. This span is not started automatically and requires manual start/finish or usage within a `with` statement.

```APIDOC
## POST /api/tracing/mcp_tools_span

### Description
Creates a new MCP list tools span. The span will not be started automatically; you should either use `with mcp_tools_span() ...` or call `span.start()` and `span.finish()` manually.

### Method
POST

### Endpoint
/api/tracing/mcp_tools_span

### Parameters
#### Query Parameters
- **server** (str | None) - Optional - The name of the MCP server.
- **result** (list[str] | None) - Optional - The result of the MCP list tools call.
- **span_id** (str | None) - Optional - The ID of the span. If not provided, an ID will be generated. It is recommended to use `util.gen_span_id()` for correct formatting.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, the current trace/span will be used.
- **disabled** (bool) - Optional - If True, the Span will be created but not recorded. Defaults to `False`.

### Request Example
```json
{
  "server": "mcp_server_1",
  "result": ["tool1", "tool2"],
  "span_id": "generated_span_id",
  "parent": null,
  "disabled": false
}
```

### Response
#### Success Response (200)
- **Span[MCPListToolsSpanData]** - The created span object, containing MCP list tools span data.

#### Response Example
```json
{
  "span_id": "created_span_id",
  "data": {
    "server": "mcp_server_1",
    "result": ["tool1", "tool2"]
  }
}
```
```

--------------------------------

### Optional on_start method for VoiceWorkflowBase - Python

Source: https://openai.github.io/openai-agents-python/ref/voice/workflow

The `on_start` method in `VoiceWorkflowBase` provides an optional hook for executing code before any user interaction. It's an asynchronous generator that can yield initial speech content, such as greetings or instructions.

```python
async def on_start(self) -> AsyncIterator[str]:
    """
    Optional method that runs before any user input is received. Can be used
    to deliver a greeting or instruction via TTS. Defaults to doing nothing.
    """
    return
    yield

```

--------------------------------

### response_span

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing

Creates a new span for an API response. This span is not started automatically and requires manual start/finish or use within a `with` statement.

```APIDOC
## response_span

### Description
Create a new response span. The span will not be started automatically, you should either do `with response_span() ...` or call `span.start()` + `span.finish()` manually.

### Method
There is no direct HTTP method for this function as it is a Python utility for tracing.

### Endpoint
N/A (Python function)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
```python
from agents.tracing import response_span
from openai import OpenAI

# Assuming 'client' is an initialized OpenAI client
# response = client.chat.completions.create(...)

# Example using a 'with' statement
# with response_span(response=response) as span:
#     # Span is active here
#     pass # Span is automatically finished

# Example with manual start and finish
# span = response_span(response=response)
# span.start()
# # Do work
# span.finish()
```

### Response
#### Success Response (200)
This function returns a `Span` object which can be used for tracing.
- **Span** (Span[ResponseSpanData]) - The created span object.

#### Response Example
```json
{
  "span_id": "generated_or_provided_id",
  "parent_id": "optional_parent_id",
  "name": "response",
  "start_time": "timestamp",
  "end_time": "timestamp",
  "status": "COMPLETED/FAILED",
  "data": {
    "response": {
      "id": "response_id",
      "object": "chat.completion",
      "created": 1677652288,
      "model": "gpt-3.5-turbo-0613",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "Hello there! How can I assist you today?"
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 9,
        "completion_tokens": 10,
        "total_tokens": 19
      }
    }
  }
}
```
```

--------------------------------

### Get Turn Usage

Source: https://openai.github.io/openai-agents-python/zh/ref/extensions/memory/advanced_sqlite_session

Retrieves usage statistics for specific turns or all turns within a session and branch, including detailed JSON token information.

```APIDOC
## GET /get_turn_usage

### Description
Retrieves usage statistics by turn with full JSON token details. This method can fetch data for a specific turn or all turns within a given branch of a session.

### Method
GET

### Endpoint
/get_turn_usage

### Parameters
#### Query Parameters
- **user_turn_number** (int) - Optional - Specific turn to get usage for. If None, returns all turns.
- **branch_id** (string) - Optional - Branch to get usage from (defaults to the current branch if None).

### Request Example
```json
{
  "user_turn_number": 5,
  "branch_id": "branch-123"
}
```

### Response
#### Success Response (200)
- **requests** (integer) - The number of requests made in the turn.
- **input_tokens** (integer) - The total number of input tokens used.
- **output_tokens** (integer) - The total number of output tokens used.
- **total_tokens** (integer) - The total number of tokens used (input + output).
- **input_tokens_details** (object) - Detailed breakdown of input tokens (can be null if not available or parsing fails).
- **output_tokens_details** (object) - Detailed breakdown of output tokens (can be null if not available or parsing fails).

If `user_turn_number` is not provided, the response will be a list of these objects, each representing a turn.

#### Response Example (Single Turn)
```json
{
  "requests": 1,
  "input_tokens": 150,
  "output_tokens": 200,
  "total_tokens": 350,
  "input_tokens_details": {
    "model_a": 100,
    "model_b": 50
  },
  "output_tokens_details": {
    "model_c": 150,
    "model_d": 50
  }
}
```

#### Response Example (All Turns)
```json
[
  {
    "user_turn_number": 1,
    "requests": 1,
    "input_tokens": 100,
    "output_tokens": 120,
    "total_tokens": 220,
    "input_tokens_details": null,
    "output_tokens_details": null
  },
  {
    "user_turn_number": 2,
    "requests": 2,
    "input_tokens": 200,
    "output_tokens": 250,
    "total_tokens": 450,
    "input_tokens_details": {
      "model_a": 200
    },
    "output_tokens_details": {
      "model_c": 250
    }
  }
]
```
```

--------------------------------

### Get Session Items - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/memory/openai_responses_compaction_session

Retrieves items from the underlying session, optionally applying a limit. This method allows fetching the current state of the session's items.

```python
async def get_items(self, limit: int | None = None) -> list[TResponseInputItem]:
        return await self.underlying_session.get_items(limit)
```

--------------------------------

### GET /session/usage

Source: https://openai.github.io/openai-agents-python/zh/ref/extensions/memory/advanced_sqlite_session

Retrieves cumulative usage statistics for the current session. This endpoint can optionally filter usage by a specific branch ID.

```APIDOC
## GET /session/usage

### Description
Get cumulative usage for the current session or a specific branch within the session. Usage statistics include total requests, input tokens, output tokens, total tokens, and total turns.

### Method
GET

### Endpoint
/session/usage

### Parameters
#### Query Parameters
- **branch_id** (str) - Optional - If provided, only return usage statistics for this specific branch. If not provided, return usage statistics for all branches in the session.

### Request Example
(No request body for GET requests)

### Response
#### Success Response (200)
- **requests** (int) - The total number of requests made.
- **input_tokens** (int) - The total number of input tokens used.
- **output_tokens** (int) - The total number of output tokens generated.
- **total_tokens** (int) - The total number of tokens used (input + output).
- **total_turns** (int) - The total number of turns in the session or branch.

#### Response Example
```json
{
  "requests": 150,
  "input_tokens": 15000,
  "output_tokens": 20000,
  "total_tokens": 35000,
  "total_turns": 75
}
```

#### Error Response (e.g., if no usage data is found)
(No specific error response documented, likely returns an empty object or null based on implementation)

#### Response Example (No Usage Data)
```json
null
```
```

--------------------------------

### MCPServerStdio Constructor

Source: https://openai.github.io/openai-agents-python/ref/mcp/server

Initializes a new MCPServerStdio instance. This server uses the stdio transport for communication and requires parameters specifying the command to run, arguments, environment variables, working directory, and text encoding.

```APIDOC
## MCPServerStdio Constructor

### Description
Initializes a new MCPServerStdio instance. This server uses the stdio transport for communication and requires parameters specifying the command to run, arguments, environment variables, working directory, and text encoding.

### Method
__init__

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **params** (MCPServerStdioParams) - Required - The parameters that configure the server. This includes the command to run to start the server, the args to pass to the command, the environment variables to set for the server, the working directory to use when spawning the process, and the text encoding used when sending/receiving messages to the server.
- **cache_tools_list** (bool) - Optional - Whether to cache the tools list. If `True`, the tools list will be cached and only fetched from the server once. If `False`, the tools list will be fetched from the server on each call to `list_tools()`.
- **name** (str | None) - Optional - A readable name for the server. If not provided, we'll create one from the command.
- **client_session_timeout_seconds** (float | None) - Optional - The read timeout passed to the MCP ClientSession. Defaults to 5 seconds.
- **tool_filter** (ToolFilter) - Optional - The tool filter to use for filtering tools.
- **use_structured_content** (bool) - Optional - Whether to use `tool_result.structured_content` when calling an MCP tool. Defaults to False for backwards compatibility.
- **max_retry_attempts** (int) - Optional - Number of times to retry failed list_tools/call_tool calls. Defaults to no retries.
- **retry_backoff_seconds_base** (float) - Optional - The base delay, in seconds, for exponential backoff between retries. Defaults to 1.0.
- **message_handler** (MessageHandlerFnT | None) - Optional - Optional handler invoked for session messages as delivered by the ClientSession.

### Request Example
```json
{
  "params": {
    "command": "python",
    "args": ["-m", "my_agent.server"],
    "env": {"MY_VAR": "my_value"},
    "cwd": "/path/to/working/dir",
    "encoding": "utf-8",
    "encoding_error_handler": "strict"
  },
  "cache_tools_list": true,
  "name": "MyMCPStdioServer",
  "client_session_timeout_seconds": 10,
  "use_structured_content": true,
  "max_retry_attempts": 3,
  "retry_backoff_seconds_base": 0.5
}
```

### Response
#### Success Response (200)
This method does not return a value directly, but initializes the server object.

#### Response Example
None
```

--------------------------------

### AgentHooksBase: Agent Start/End Callbacks (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/lifecycle

Defines callbacks for the start and end of a specific agent's execution. `on_start` is called when the agent becomes active, and `on_end` is triggered when it produces its final output.

```python
class AgentHooksBase[TContext, TAgent]:
    async def on_start(
        self, context: AgentHookContext[TContext], agent: TAgent
    ) -> None:
        """Called before the agent is invoked. Called each time the running agent is changed to this agent."""
        pass

    async def on_end(
        self,
        context: AgentHookContext[TContext],
        agent: TAgent,
        output: Any,
    ) -> None:
        """Called when the agent produces a final output."""
        pass

```

--------------------------------

### GET /api/tool_usage

Source: https://openai.github.io/openai-agents-python/ref/extensions/memory/advanced_sqlite_session

Retrieves a summary of tool usage, including counts and turn numbers, for a specified branch. Defaults to the current branch if no branch ID is provided.

```APIDOC
## GET /api/tool_usage

### Description
Retrieves a summary of tool usage, including counts and turn numbers, for a specified branch. Defaults to the current branch if no branch ID is provided.

### Method
GET

### Endpoint
`/api/tool_usage`

#### Query Parameters
- **branch_id** (string) - Optional - The ID of the branch to retrieve tool usage from. Defaults to the current branch if not specified.

### Response
#### Success Response (200)
- **tool_usage_list** (array) - A list of tool usage records.
  - **tool_name** (string) - The name of the tool.
  - **usage_count** (integer) - The number of times the tool was used in that turn.
  - **turn_number** (integer) - The turn number in which the tool was used.

#### Response Example
```json
[
  {"tool_name": "code_interpreter", "usage_count": 1, "turn_number": 2},
  {"tool_name": "web_search", "usage_count": 1, "turn_number": 3}
]
```
```

--------------------------------

### Get Specific Prompt from Server (Python)

Source: https://openai.github.io/openai-agents-python/ref/mcp/server

Abstract method to fetch a specific prompt by its name, optionally with arguments. It returns a GetPromptResult containing the prompt details.

```python
import abc
from typing import Any, Dict, Optional

# Assuming this type is defined elsewhere
class GetPromptResult:
    pass

class MCPBaseServer(abc.ABC):
    @abc.abstractmethod
    async def get_prompt(self, name: str, arguments: dict[str, Any] | None = None) -> GetPromptResult:
        """Get a specific prompt from the server."""
        pass

```

--------------------------------

### Handle Realtime Model Turn Events in Python

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/openai_realtime

Manages the start and end of a turn in the Realtime Model conversation. It emits `RealtimeModelTurnStartedEvent` when a response is created and `RealtimeModelTurnEndedEvent` when a response is completed.

```python
elif parsed.type == "response.created":
            self._ongoing_response = True
            await self._emit_event(RealtimeModelTurnStartedEvent())
        elif parsed.type == "response.done":
            self._ongoing_response = False
            await self._emit_event(RealtimeModelTurnEndedEvent())

```

--------------------------------

### Format Agent Prompt with Handoff Instructions

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/handoff_prompt

A Python function that takes a user prompt and prepends the recommended system context for agents that support handoffs. This ensures agents are aware of the multi-agent system and handoff mechanisms.

```python
def prompt_with_handoff_instructions(prompt: str) -> str:
    """
    Add recommended instructions to the prompt for agents that use handoffs.
    """
    return f"{RECOMMENDED_PROMPT_PREFIX}\n\n{prompt}"
```

--------------------------------

### GET /api/history

Source: https://openai.github.io/openai-agents-python/ja/ref/memory

Retrieves the conversation history for the current session. You can specify a limit to fetch only the most recent messages.

```APIDOC
## GET /api/history

### Description
Retrieves the conversation history for this session. You can optionally limit the number of items returned.

### Method
GET

### Endpoint
/api/history

### Parameters
#### Query Parameters
- **limit** (integer) - Optional - Maximum number of items to retrieve. If not specified, retrieves all items. When specified, returns the latest N items in chronological order.

### Request Example
(No request body for GET)

### Response
#### Success Response (200)
- **items** (list[object]) - A list of objects, where each object represents an item in the conversation history. Each item may contain various fields depending on its type.

#### Response Example
```json
{
  "items": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    },
    {
      "role": "assistant",
      "content": "I'm doing well, thank you! How can I help you today?"
    }
  ]
}
```
```

--------------------------------

### OpenAIRealtimeSIPModel: Build Initial Session Payload (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/openai_realtime

Builds a session payload for Realtime Calls API, mirroring RealtimeSession connect behavior. This is useful for accepting SIP-originated calls without duplicating session setup logic. It takes an agent, context, model configuration, run configuration, and optional overrides to construct the payload.

```python
class OpenAIRealtimeSIPModel(OpenAIRealtimeWebSocketModel):
    """Realtime model that attaches to SIP-originated calls using a call ID."""

    @staticmethod
    async def build_initial_session_payload(
        agent: RealtimeAgent[Any],
        *,
        context: TContext | None = None,
        model_config: RealtimeModelConfig | None = None,
        run_config: RealtimeRunConfig | None = None,
        overrides: RealtimeSessionModelSettings | None = None,
    ) -> OpenAISessionCreateRequest:
        """Build a session payload that mirrors what a RealtimeSession would send on connect.

        This helper can be used to accept SIP-originated calls by forwarding the returned payload to
        the Realtime Calls API without duplicating session setup logic.
        """
        run_config_settings = (run_config or {}).get("model_settings") or {}
        initial_model_settings = (model_config or {}).get("initial_model_settings") or {}
        base_settings: RealtimeSessionModelSettings = {
            **run_config_settings,
            **initial_model_settings,
        }

        context_wrapper = RunContextWrapper(context)
        merged_settings = await _build_model_settings_from_agent(
            agent=agent,
            context_wrapper=context_wrapper,
            base_settings=base_settings,
            starting_settings=initial_model_settings,
            run_config=run_config,
        )

        if overrides:
            merged_settings.update(overrides)

        model = OpenAIRealtimeWebSocketModel()
        return model._get_session_config(merged_settings)
```

--------------------------------

### Get Output Type Name

Source: https://openai.github.io/openai-agents-python/zh/ref/agent_output

Retrieves the string representation of the output type. This function is used to identify the expected data format for agent outputs.

```python
def name(self) -> str:
    """The name of the output type."""
    return _type_to_str(self.output_type)
```

--------------------------------

### Handle Agent Handoff and Tool Execution

Source: https://openai.github.io/openai-agents-python/ref/realtime/session

This snippet handles agent handoffs and tool execution. It checks for specific event names in a handoff map, executes the handoff logic, updates the current agent, and sends necessary events to the model, including session updates and tool outputs. It also includes error handling for unknown tools.

```python
output=result,
                    agent=agent,
                    arguments=event.arguments,
                )
            )
        elif event.name in handoff_map:
            handoff = handoff_map[event.name]
            tool_context = ToolContext(
                context=self._context_wrapper.context,
                usage=self._context_wrapper.usage,
                tool_name=event.name,
                tool_call_id=event.call_id,
                tool_arguments=event.arguments,
            )

            # Execute the handoff to get the new agent
            result = await handoff.on_invoke_handoff(self._context_wrapper, event.arguments)
            if not isinstance(result, RealtimeAgent):
                raise UserError(
                    f"Handoff {handoff.tool_name} returned invalid result: {type(result)}"
                )

            # Store previous agent for event
            previous_agent = agent

            # Update current agent
            self._current_agent = result

            # Get updated model settings from new agent
            updated_settings = await self._get_updated_model_settings_from_agent(
                starting_settings=None,
                agent=self._current_agent,
            )

            # Send handoff event
            await self._put_event(
                RealtimeHandoffEvent(
                    from_agent=previous_agent,
                    to_agent=self._current_agent,
                    info=self._event_info,
                )
            )

            # First, send the session update so the model receives the new instructions
            await self._model.send_event(
                RealtimeModelSendSessionUpdate(session_settings=updated_settings)
            )

            # Then send tool output to complete the handoff (this triggers a new response)
            transfer_message = handoff.get_transfer_message(result)
            await self._model.send_event(
                RealtimeModelSendToolOutput(
                    tool_call=event,
                    output=transfer_message,
                    start_response=True,
                )
            )
        else:
            await self._put_event(
                RealtimeError(
                    info=self._event_info,
                    error={"message": f"Tool {event.name} not found"},
                )
            )
```

--------------------------------

### Get State Options with Consistency and Concurrency

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/memory/dapr_session

Configures and returns StateOptions based on consistency settings (strong or eventual) and optional concurrency parameters. Handles cases where no options are needed.

```python
def _get_state_options(self, *, concurrency: Concurrency | None = None) -> StateOptions | None:
        """Get StateOptions configured with consistency and optional concurrency."""
        options_kwargs: dict[str, Any] = {}
        if self._consistency == DAPR_CONSISTENCY_STRONG:
            options_kwargs["consistency"] = Consistency.strong
        elif self._consistency == DAPR_CONSISTENCY_EVENTUAL:
            options_kwargs["consistency"] = Consistency.eventual
        if concurrency is not None:
            options_kwargs["concurrency"] = concurrency
        if options_kwargs:
            return StateOptions(**options_kwargs)
        return None
```

--------------------------------

### Define Recommended Prompt Prefix for Handoffs

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/handoff_prompt

Defines a system context prefix that includes instructions for agents operating within the Agents SDK, emphasizing seamless handoffs between agents using a specific function naming convention.

```python
RECOMMENDED_PROMPT_PREFIX = "# System context\nYou are part of a multi-agent system called the Agents SDK, designed to make agent coordination and execution easy. Agents uses two primary abstraction: **Agents** and **Handoffs**. An agent encompasses instructions and tools and can hand off a conversation to another agent when appropriate. Handoffs are achieved by calling a handoff function, generally named `transfer_to_<agent_name>`. Transfers between agents are handled seamlessly in the background; do not mention or draw attention to these transfers in your conversation with the user.\n"
```

--------------------------------

### SessionABC - Get Items

Source: https://openai.github.io/openai-agents-python/zh/ref/memory/session

Retrieves the conversation history for a given session, with an optional limit on the number of items returned.

```APIDOC
## GET /sessions/{sessionId}/items

### Description
Retrieve the conversation history for this session.

### Method
GET

### Endpoint
/sessions/{sessionId}/items

### Parameters
#### Query Parameters
- **limit** (integer | null) - Optional - Maximum number of items to retrieve. If None, retrieves all items. When specified, returns the latest N items in chronological order.

### Response
#### Success Response (200)
- **items** (list[TResponseInputItem]) - List of input items representing the conversation history

#### Response Example
```json
{
  "items": [
    {
      "role": "user",
      "content": "Hello!"
    },
    {
      "role": "assistant",
      "content": "Hi there! How can I help you today?"
    }
  ]
}
```
```

--------------------------------

### Get Realtime Session Configuration (Python)

Source: https://openai.github.io/openai-agents-python/ref/realtime/openai_realtime

Retrieves and constructs the session configuration for a realtime session based on provided model settings. This method handles the mapping of various audio input and output parameters, including format, noise reduction, transcription, turn detection, and voice. It uses default settings when specific configurations are not found and ensures audio formats are correctly converted using `to_realtime_audio_format`. Dependencies include `RealtimeSessionModelSettings`, `OpenAISessionCreateRequest`, `to_realtime_audio_format`, and `DEFAULT_MODEL_SETTINGS`.

```python
def _get_session_config(
        self,
        model_settings: RealtimeSessionModelSettings
    ) -> OpenAISessionCreateRequest:
        """Get the session config."""
        audio_input_args: dict[str, Any] = {}
        audio_output_args: dict[str, Any] = {}

        audio_config = model_settings.get("audio")
        audio_config_mapping = audio_config if isinstance(audio_config, Mapping) else None
        input_audio_config: Mapping[str, Any] = (
            cast(Mapping[str, Any], audio_config_mapping.get("input", {}))
            if audio_config_mapping
            else {}
        )
        output_audio_config: Mapping[str, Any] = (
            cast(Mapping[str, Any], audio_config_mapping.get("output", {}))
            if audio_config_mapping
            else {}
        )

        input_format_source: FormatInput = (
            input_audio_config.get("format") if input_audio_config else None
        )
        if input_format_source is None:
            if self._call_id:
                input_format_source = model_settings.get("input_audio_format")
            else:
                input_format_source = model_settings.get(
                    "input_audio_format", DEFAULT_MODEL_SETTINGS.get("input_audio_format")
                )
        audio_input_args["format"] = to_realtime_audio_format(input_format_source)

        if "noise_reduction" in input_audio_config:
            audio_input_args["noise_reduction"] = input_audio_config.get("noise_reduction")
        elif "input_audio_noise_reduction" in model_settings:
            audio_input_args["noise_reduction"] = model_settings.get("input_audio_noise_reduction")

        if "transcription" in input_audio_config:
            audio_input_args["transcription"] = input_audio_config.get("transcription")
        elif "input_audio_transcription" in model_settings:
            audio_input_args["transcription"] = model_settings.get("input_audio_transcription")
        else:
            audio_input_args["transcription"] = DEFAULT_MODEL_SETTINGS.get(
                "input_audio_transcription"
            )

        if "turn_detection" in input_audio_config:
            audio_input_args["turn_detection"] = self._normalize_turn_detection_config(
                input_audio_config.get("turn_detection")
            )
        elif "turn_detection" in model_settings:
            audio_input_args["turn_detection"] = self._normalize_turn_detection_config(
                model_settings.get("turn_detection")
            )
        else:
            audio_input_args["turn_detection"] = DEFAULT_MODEL_SETTINGS.get("turn_detection")

        requested_voice = output_audio_config.get("voice") if output_audio_config else None
        audio_output_args["voice"] = requested_voice or model_settings.get(
            "voice", DEFAULT_MODEL_SETTINGS.get("voice")
        )

        output_format_source: FormatInput = (
            output_audio_config.get("format") if output_audio_config else None
        )
        if output_format_source is None:
            if self._call_id:
                output_format_source = model_settings.get("output_audio_format")
            else:
                output_format_source = model_settings.get(
                    "output_audio_format", DEFAULT_MODEL_SETTINGS.get("output_audio_format")
                )
        audio_output_args["format"] = to_realtime_audio_format(output_format_source)

        if "speed" in output_audio_config:
            audio_output_args["speed"] = output_audio_config.get("speed")
        elif "speed" in model_settings:
            audio_output_args["speed"] = model_settings.get("speed")

        output_modalities = (
            model_settings.get("output_modalities")
            or model_settings.get("modalities")
            or DEFAULT_MODEL_SETTINGS.get("modalities")
        )

        # Construct full session object. `type` will be excluded at serialization time for updates.
        session_create_request = OpenAISessionCreateRequest(
            type="realtime",
            model=(model_settings.get("model_name") or self.model) or "gpt-realtime",
            output_modalities=output_modalities,

```

--------------------------------

### Trace Lifecycle Management

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing

Manages the lifecycle of a trace, allowing it to be started and finished. Optionally, traces can be marked as the current trace during execution.

```APIDOC
## Trace Lifecycle Management

### Description
Manages the start and end of a trace, including options to set it as the current trace.

### Endpoints

- **POST /trace/start**
- **POST /trace/finish**

### Parameters

#### Start Trace
- **mark_as_current** (bool) - Optional - If true, marks this trace as the current trace in the execution context. Defaults to `False`.

#### Finish Trace
- **reset_current** (bool) - Optional - If true, resets the current trace to the previous trace in the execution context. Defaults to `False`.

### Notes

- `start()` must be called before any spans can be added.
- Only one trace can be current at a time.
- `finish()` must be called to complete the trace and finalize all open spans.
- Both methods are thread-safe when using their respective optional parameters.

### Request Example

#### Start Trace Example
```json
{
  "mark_as_current": true
}
```

#### Finish Trace Example
```json
{
  "reset_current": true
}
```

### Response

#### Success Response (200)

Responses for start and finish operations typically indicate success without returning specific data, signifying the operation was completed.

#### Response Example

*Success is indicated by a 200 OK status code.*
```

--------------------------------

### Python: Basic Trace Usage

Source: https://openai.github.io/openai-agents-python/ref/tracing

Illustrates the basic usage of the `trace` context manager in Python for defining a workflow. It shows how to wrap a series of operations within a `with trace(...)` block, ensuring proper setup and cleanup for the trace. This is useful for simple workflow logging without specific grouping or metadata.

```python
# Assuming Runner, validator, order_data, and processor are defined elsewhere

# Basic trace usage
with trace("Order Processing") as t:
    validation_result = await Runner.run(validator, order_data)
    if validation_result.approved:
        await Runner.run(processor, order_data)
```

--------------------------------

### Trace Provider Management

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing

Utilities for managing the global trace provider, including getting the current provider and setting a new one.

```APIDOC
## Trace Provider Utilities

### Description
Utilities for managing the global trace provider, including getting the current provider and setting a new one.

### Functions

#### get_trace_provider()
- **Description**: Get the global trace provider used by tracing utilities.
- **Returns**: `TraceProvider` - The current global trace provider.

#### set_trace_provider(provider: TraceProvider)
- **Description**: Set the global trace provider used by tracing utilities.
- **Parameters**:
  - **provider** (`TraceProvider`) - Required - The trace provider to set as global.
- **Returns**: `None`
```

--------------------------------

### GET /conversations/history

Source: https://openai.github.io/openai-agents-python/zh/ref/memory/sqlite_session

Retrieves the conversation history for a given session. It supports an optional limit to fetch the latest N items.

```APIDOC
## GET /conversations/history

### Description
Retrieve the conversation history for this session. Supports fetching a limited number of the most recent items.

### Method
GET

### Endpoint
/conversations/history

### Parameters
#### Query Parameters
- **limit** (integer) - Optional - Maximum number of items to retrieve. If not specified, retrieves all items. When specified, returns the latest N items in chronological order.

### Request Example
```json
{
  "limit": 10
}
```

### Response
#### Success Response (200)
- **items** (list[object]) - List of input items representing the conversation history. Each item is an object.

#### Response Example
```json
{
  "items": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    },
    {
      "role": "assistant",
      "content": "I am doing well, thank you!"
    }
  ]
}
```
```

--------------------------------

### GET /api/agents/memory/session/items

Source: https://openai.github.io/openai-agents-python/ref/memory/sqlite_session

Retrieves the conversation history for a given session. It supports an optional limit to fetch the latest N items.

```APIDOC
## GET /api/agents/memory/session/items

### Description
Retrieves the conversation history for this session. You can specify a limit to get the most recent items.

### Method
GET

### Endpoint
/api/agents/memory/session/items

### Parameters
#### Query Parameters
- **limit** (int) - Optional - Maximum number of items to retrieve. If None, retrieves all items. When specified, returns the latest N items in chronological order.

### Response
#### Success Response (200)
- **items** (list[TResponseInputItem]) - List of input items representing the conversation history

#### Response Example
{
  "items": [
    {
      "role": "user",
      "content": "Hello, how can I help you?"
    },
    {
      "role": "assistant",
      "content": "I'm here to assist you with your inquiries."
    }
  ]
}
```

--------------------------------

### Create Branch From Turn

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/memory/advanced_sqlite_session

Creates a new branch starting from a specific user message turn within a session. This is useful for exploring alternative conversation paths or forking development.

```APIDOC
## POST /branches/from_turn

### Description
Creates a new branch starting from a specific user message turn. An optional name can be provided for the new branch; otherwise, it will be auto-generated.

### Method
POST

### Endpoint
/branches/from_turn

### Parameters
#### Path Parameters
None

#### Query Parameters
* **turn_number** (int) - Required - The turn number of the user message to branch from.
* **branch_name** (string) - Optional - A name for the new branch. If not provided, a name will be auto-generated.

### Request Example
```json
{
  "turn_number": 5,
  "branch_name": "experiment-branch"
}
```

### Response
#### Success Response (200)
- **branch_id** (string) - The unique identifier of the newly created branch.

#### Response Example
```json
{
  "branch_id": "branch_from_turn_5_1678886400"
}
```

#### Error Response
- **ValueError**: If the specified turn does not exist or does not contain a user message.
```

--------------------------------

### Forcing Tool Use with Model Settings (Python)

Source: https://openai.github.io/openai-agents-python/agents

Explains how to control tool usage in an agent by setting `ModelSettings.tool_choice`. This example forces the agent to use the 'get_weather' tool for retrieving weather information.

```python
from agents import Agent, Runner, function_tool, ModelSettings

@function_tool
def get_weather(city: str) -> str:
    """Returns weather info for the specified city."""
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Weather Agent",
    instructions="Retrieve weather details.",
    tools=[get_weather],
    model_settings=ModelSettings(tool_choice="get_weather")
)


```

--------------------------------

### MultiProvider Class Definition and Initialization (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/models/multi_provider

Defines the MultiProvider class, inheriting from ModelProvider. Its constructor initializes default or custom provider mappings and sets up the OpenAIProvider with configurable parameters like API key, base URL, and client.

```python
class MultiProvider(ModelProvider):
    """This ModelProvider maps to a Model based on the prefix of the model name. By default, the
    mapping is:
    - "openai/" prefix or no prefix -> OpenAIProvider. e.g. "openai/gpt-4.1", "gpt-4.1"
    - "litellm/" prefix -> LitellmProvider. e.g. "litellm/openai/gpt-4.1"

    You can override or customize this mapping.
    """

    def __init__(
        self,
        *,
        provider_map: MultiProviderMap | None = None,
        openai_api_key: str | None = None,
        openai_base_url: str | None = None,
        openai_client: AsyncOpenAI | None = None,
        openai_organization: str | None = None,
        openai_project: str | None = None,
        openai_use_responses: bool | None = None,
    ) -> None:
        """Create a new OpenAI provider.

        Args:
            provider_map: A MultiProviderMap that maps prefixes to ModelProviders. If not provided,
                we will use a default mapping. See the documentation for this class to see the
                default mapping.
            openai_api_key: The API key to use for the OpenAI provider. If not provided, we will use
                the default API key.
            openai_base_url: The base URL to use for the OpenAI provider. If not provided, we will
                use the default base URL.
            openai_client: An optional OpenAI client to use. If not provided, we will create a new
                OpenAI client using the api_key and base_url.
            openai_organization: The organization to use for the OpenAI provider.
            openai_project: The project to use for the OpenAI provider.
            openai_use_responses: Whether to use the OpenAI responses API.
        """
        self.provider_map = provider_map
        self.openai_provider = OpenAIProvider(
            api_key=openai_api_key,
            base_url=openai_base_url,
            openai_client=openai_client,
            organization=openai_organization,
            project=openai_project,
            use_responses=openai_use_responses,
        )

        self._fallback_providers: dict[str, ModelProvider] = {}

```

--------------------------------

### GET /session/items

Source: https://openai.github.io/openai-agents-python/ja/ref/memory/session

Retrieves the conversation history for the current session. You can optionally specify a limit to fetch only the latest items.

```APIDOC
## GET /session/items

### Description
Retrieve the conversation history for this session.

### Method
GET

### Endpoint
`/session/items`

### Query Parameters
- **limit** (int | None) - Optional - Maximum number of items to retrieve. If None, retrieves all items. When specified, returns the latest N items in chronological order.

### Response
#### Success Response (200)
- **items** (list[TResponseInputItem]) - List of input items representing the conversation history

#### Response Example
```json
{
  "items": [
    {
      "role": "user",
      "content": "Hello!"
    },
    {
      "role": "assistant",
      "content": "Hi there! How can I help you today?"
    }
  ]
}
```
```

--------------------------------

### GET /websites/openai_github_io_openai-agents-python/get_state

Source: https://openai.github.io/openai-agents-python/ko/ref/realtime/model

Retrieves the current playback state of the realtime model, including the item ID, content index, and elapsed milliseconds.

```APIDOC
## GET /websites/openai_github_io_openai-agents-python/get_state

### Description
Retrieves the current playback state of the realtime model, including the item ID, content index, and elapsed milliseconds.

### Method
GET

### Endpoint
/websites/openai_github_io_openai-agents-python/get_state

### Parameters
None

### Response
#### Success Response (200)
- **current_item_id** (str or null) - The ID of the currently playing item, or null if nothing is playing.
- **current_item_content_index** (int or null) - The index of the current audio content, or null.
- **elapsed_ms** (float or null) - The number of milliseconds played for the current item, or null.

### Response Example
```json
{
  "current_item_id": "audio_clip_1",
  "current_item_content_index": 0,
  "elapsed_ms": 1500.5
}
```
```

--------------------------------

### Create Branch From Turn API

Source: https://openai.github.io/openai-agents-python/zh/ref/extensions/memory/advanced_sqlite_session

Allows the creation of a new branch in the conversation history starting from a specified user message turn. This is useful for exploring alternative conversation paths.

```APIDOC
## POST /agents/extensions/memory/advanced_sqlite_session/create_branch_from_turn

### Description
Creates a new branch starting from a specific user message turn. This allows for exploring alternative conversation paths from a given point in the history.

### Method
POST

### Endpoint
/agents/extensions/memory/advanced_sqlite_session/create_branch_from_turn

### Parameters
#### Path Parameters
None

#### Query Parameters
- **turn_number** (int) - Required - The turn number of the user message to branch from.
- **branch_name** (str | None) - Optional - A name for the new branch. If not provided, a name will be auto-generated.

### Request Body
This endpoint does not use a request body. Parameters are passed as query parameters.

### Request Example
```json
{
  "turn_number": 5,
  "branch_name": "alternative_path_1"
}
```

### Response
#### Success Response (200)
- **branch_id** (str) - The unique identifier of the newly created branch.

#### Response Example
```json
{
  "branch_id": "branch_from_turn_5_1678886400"
}
```

#### Error Response
- **ValueError**: Returned if the specified turn does not exist or does not contain a user message.
```

--------------------------------

### Run Interactive Agent REPL Loop (Python)

Source: https://openai.github.io/openai-agents-python/repl

This Python script utilizes the `run_demo_loop` function from the OpenAI Agents SDK to start an interactive chat session directly in the terminal. It initializes an agent with a name and instructions, then facilitates a continuous conversation where the agent remembers history and streams responses. To exit, type 'quit' or 'exit', or use Ctrl-D.

```python
import asyncio
from agents import Agent, run_demo_loop

async def main() -> None:
    agent = Agent(name="Assistant", instructions="You are a helpful assistant.")
    await run_demo_loop(agent)

if __name__ == "__main__":
    asyncio.run(main())

```

--------------------------------

### Initial Model Settings Configuration (Python)

Source: https://openai.github.io/openai-agents-python/ko/ref/realtime/config

Sets the initial model settings for a realtime session connection. This allows pre-configuration of model behavior.

```python
initial_model_settings: NotRequired[
    RealtimeSessionModelSettings
]
```

--------------------------------

### Get All Function Tools

Source: https://openai.github.io/openai-agents-python/ko/ref/mcp/util

Retrieves all function tools available across a list of MCP servers. It ensures that tool names are unique across all provided servers to prevent conflicts.

```APIDOC
## GET /tools/all

### Description
Get all function tools from a list of MCP servers. This method aggregates tools from multiple servers and raises an error if duplicate tool names are found.

### Method
GET

### Endpoint
/tools/all

### Parameters
#### Query Parameters
- **servers** (list[MCPServer]) - Required - A list of MCP server configurations to fetch tools from.
- **convert_schemas_to_strict** (bool) - Required - Flag to determine if input schemas should be converted to a strict JSON schema format.
- **run_context** (RunContextWrapper[Any]) - Required - The context for the current run operation.
- **agent** (AgentBase) - Required - The agent instance performing the operation.

### Response
#### Success Response (200)
- **tools** (list[Tool]) - A list of available function tools.

#### Response Example
```json
[
  {
    "name": "example_tool",
    "description": "An example tool",
    "params_json_schema": {},
    "on_invoke_tool": "<function>",
    "strict_json_schema": false
  }
]
```
```

--------------------------------

### OpenAIRealtimeSIPModel: Build Initial Session Payload (Python)

Source: https://openai.github.io/openai-agents-python/ref/realtime/openai_realtime

Builds a session payload for the Realtime Calls API, mirroring what a RealtimeSession would send on connect. This is useful for accepting SIP-originated calls without duplicating session setup logic. It takes an agent, context, model configuration, run configuration, and optional overrides as input.

```python
class OpenAIRealtimeSIPModel(OpenAIRealtimeWebSocketModel):
    """Realtime model that attaches to SIP-originated calls using a call ID."""

    @staticmethod
    async def build_initial_session_payload(
        agent: RealtimeAgent[Any],
        *,
        context: TContext | None = None,
        model_config: RealtimeModelConfig | None = None,
        run_config: RealtimeRunConfig | None = None,
        overrides: RealtimeSessionModelSettings | None = None,
    ) -> OpenAISessionCreateRequest:
        """Build a session payload that mirrors what a RealtimeSession would send on connect.

        This helper can be used to accept SIP-originated calls by forwarding the returned payload to
        the Realtime Calls API without duplicating session setup logic.
        """
        run_config_settings = (run_config or {}).get("model_settings") or {}
        initial_model_settings = (model_config or {}).get("initial_model_settings") or {}
        base_settings: RealtimeSessionModelSettings = {
            **run_config_settings,
            **initial_model_settings,
        }

        context_wrapper = RunContextWrapper(context)
        merged_settings = await _build_model_settings_from_agent(
            agent=agent,
            context_wrapper=context_wrapper,
            base_settings=base_settings,
            starting_settings=initial_model_settings,
            run_config=run_config,
        )

        if overrides:
            merged_settings.update(overrides)

        model = OpenAIRealtimeWebSocketModel()
        return model._get_session_config(merged_settings)

    async def connect(self, options: RealtimeModelConfig) -> None:
        call_id = options.get("call_id")
        if not call_id:
            raise UserError("OpenAIRealtimeSIPModel requires `call_id` in the model configuration.")

        sip_options = options.copy()
        await super().connect(sip_options)
```

--------------------------------

### Tracer Initialization (__init__)

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing/processors

Initializes the tracing client with various configuration options for sending traces and spans to the OpenAI API. It supports custom endpoints, retry mechanisms, and delay strategies.

```APIDOC
## Tracer Initialization

### Description
Initializes the tracing client with configuration for API key, organization, project, endpoint, and retry parameters.

### Method
`__init__`

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Constructor Parameters
- **api_key** (`str | None`) - Optional - The API key for the "Authorization" header. Defaults to `os.environ["OPENAI_API_KEY"]` if not provided.
- **organization** (`str | None`) - Optional - The OpenAI organization to use. Defaults to `os.environ["OPENAI_ORG_ID"]` if not provided.
- **project** (`str | None`) - Optional - The OpenAI project to use. Defaults to `os.environ["OPENAI_PROJECT_ID"]` if not provided.
- **endpoint** (`str`) - Optional - The HTTP endpoint to which traces/spans are posted. Defaults to `'https://api.openai.com/v1/traces/ingest'`.
- **max_retries** (`int`) - Optional - Maximum number of retries upon failures. Defaults to `3`.
- **base_delay** (`float`) - Optional - Base delay (in seconds) for the first backoff. Defaults to `1.0`.
- **max_delay** (`float`) - Optional - Maximum delay (in seconds) for backoff growth. Defaults to `30.0`.

### Request Example
```python
from agents.tracing import Tracer

tracer = Tracer(
    api_key="sk-your-api-key",
    organization="org-your-org-id",
    project="proj-your-project-id",
    endpoint="https://api.openai.com/v1/traces/ingest",
    max_retries=5,
    base_delay=0.5,
    max_delay=60.0
)
```

### Response
N/A (This is a constructor)

### Error Handling
- Network or I/O errors during initialization are handled internally with retries.
```

--------------------------------

### GET /turn_usage

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/memory/advanced_sqlite_session

Retrieves usage statistics by turn, including full JSON token details. This endpoint can fetch usage for a specific turn or for all turns within a branch.

```APIDOC
## GET /turn_usage

### Description
Retrieves usage statistics by turn with full JSON token details. If `user_turn_number` is provided, it returns usage for that specific turn; otherwise, it returns usage for all turns in the specified or current branch.

### Method
GET

### Endpoint
/turn_usage

### Parameters
#### Query Parameters
- **user_turn_number** (int) - Optional - The specific turn number to retrieve usage statistics for. If omitted, all turns are returned.
- **branch_id** (str) - Optional - The ID of the branch to retrieve usage from. If omitted, the current branch is used.

### Request Example
```json
{
  "user_turn_number": 5,
  "branch_id": "branch-123"
}
```

### Response
#### Success Response (200)
- **requests** (int) - The number of requests made in the turn.
- **input_tokens** (int) - The total number of input tokens used.
- **output_tokens** (int) - The total number of output tokens used.
- **total_tokens** (int) - The total number of tokens used (input + output).
- **input_tokens_details** (object | null) - Detailed breakdown of input token usage, or null if not available.
- **output_tokens_details** (object | null) - Detailed breakdown of output token usage, or null if not available.
- **user_turn_number** (int) - The turn number (only present when fetching all turns).

#### Response Example (Single Turn)
```json
{
  "requests": 1,
  "input_tokens": 150,
  "output_tokens": 200,
  "total_tokens": 350,
  "input_tokens_details": {
    "model_a": 100,
    "model_b": 50
  },
  "output_tokens_details": {
    "model_a": 180,
    "model_b": 20
  }
}
```

#### Response Example (All Turns)
```json
[
  {
    "user_turn_number": 1,
    "requests": 1,
    "input_tokens": 100,
    "output_tokens": 120,
    "total_tokens": 220,
    "input_tokens_details": null,
    "output_tokens_details": null
  },
  {
    "user_turn_number": 2,
    "requests": 1,
    "input_tokens": 120,
    "output_tokens": 150,
    "total_tokens": 270,
    "input_tokens_details": {
      "model_a": 120
    },
    "output_tokens_details": {
      "model_a": 150
    }
  }
]
```

```

--------------------------------

### speech_span

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/create

Creates a new speech span for tracing text-to-speech operations. The span needs to be manually started and finished or used with a `with` statement.

```APIDOC
## POST /speech/span

### Description
Creates a new speech span for tracing text-to-speech operations. The span needs to be manually started and finished or used with a `with` statement.

### Method
POST

### Endpoint
`/speech/span`

### Parameters
#### Query Parameters
- **model** (str | None) - Optional - The name of the model used for the text-to-speech.
- **input** (str | None) - Optional - The text input of the text-to-speech.
- **output** (str | None) - Optional - The audio output of the text-to-speech as base64 encoded string of PCM audio bytes.
- **output_format** (str | None) - Optional - The format of the audio output (defaults to "pcm").
- **model_config** (Mapping[str, Any] | None) - Optional - The model configuration (hyperparameters) used.
- **first_content_at** (str | None) - Optional - The time of the first byte of the audio output.
- **span_id** (str | None) - Optional - The ID of the span. If not provided, an ID will be generated. Use `util.gen_span_id()` for guaranteed correct formatting.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, the current trace/span is used.
- **disabled** (bool) - Optional - If True, a Span will be returned but not recorded. Defaults to `False`.

### Request Example
```json
{
  "model": "tts-1",
  "input": "Hello, world!",
  "output_format": "mp3"
}
```

### Response
#### Success Response (200)
- **span** (Span[SpeechSpanData]) - The created speech span object.
```

--------------------------------

### Basic Trace Usage with Context Manager

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/traces

Illustrates the fundamental usage of the `trace` context manager for basic workflow tracing. It shows how to wrap code blocks to create a trace with a simple name, ensuring reliable cleanup and management of the trace lifecycle.

```python
# Basic trace usage
with trace("Order Processing") as t:
    validation_result = await Runner.run(validator, order_data)
    if validation_result.approved:
        await Runner.run(processor, order_data)
```

--------------------------------

### Define and Use Python Functions as Tools with OpenAI Agents SDK

Source: https://openai.github.io/openai-agents-python/tools

Demonstrates how to define Python functions decorated with `@function_tool` to be used as tools by the OpenAI Agents SDK. It shows automatic extraction of tool name, description from docstrings, and input schema generation from type hints. The example also includes creating an Agent with these tools and printing their details.

```python
import json

from typing_extensions import TypedDict, Any

from agents import Agent, FunctionTool, RunContextWrapper, function_tool


class Location(TypedDict):
    lat: float
    long: float

@function_tool  
async def fetch_weather(location: Location) -> str:
    
    """Fetch the weather for a given location.

    Args:
        location: The location to fetch the weather for.
    """
    # In real life, we'd fetch the weather from a weather API
    return "sunny"


@function_tool(name_override="fetch_data")  
def read_file(ctx: RunContextWrapper[Any], path: str, directory: str | None = None) -> str:
    """Read the contents of a file.

    Args:
        path: The path to the file to read.
        directory: The directory to read the file from.
    """
    # In real life, we'd read the file from the file system
    return "<file contents>"


agent = Agent(
    name="Assistant",
    tools=[fetch_weather, read_file],  
)

for tool in agent.tools:
    if isinstance(tool, FunctionTool):
        print(tool.name)
        print(tool.description)
        print(json.dumps(tool.params_json_schema, indent=2))
        print()

```

--------------------------------

### MCPServerStreamableHttp Initialization

Source: https://openai.github.io/openai-agents-python/ja/ref/mcp/server

Initializes a new MCPServerStreamableHttp instance with specified parameters and optional configurations.

```APIDOC
## MCPServerStreamableHttp

### Description
Initializes a new MCP server based on the Streamable HTTP transport.

### Method
__init__

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **params** (MCPServerStreamableHttpParams) - Required - The params that configure the server. This includes the URL of the server, the headers to send to the server, the timeout for the HTTP request, the timeout for the Streamable HTTP connection, whether we need to terminate on close, and an optional custom HTTP client factory.
- **cache_tools_list** (bool) - Optional - Whether to cache the tools list. If `True`, the tools list will be cached and only fetched from the server once. If `False`, the tools list will be fetched from the server on each call to `list_tools()`. The cache can be invalidated by calling `invalidate_tools_cache()`. You should set this to `True` if you know the server will not change its tools list, because it can drastically improve latency (by avoiding a round-trip to the server every time).
- **name** (str | None) - Optional - A readable name for the server. If not provided, we'll create one from the URL.
- **client_session_timeout_seconds** (float | None) - Optional - The read timeout passed to the MCP ClientSession.
- **tool_filter** (ToolFilter) - Optional - The tool filter to use for filtering tools.
- **use_structured_content** (bool) - Optional - Whether to use `tool_result.structured_content` when calling an MCP tool. Defaults to False for backwards compatibility - most MCP servers still include the structured content in the `tool_result.content`, and using it by default will cause duplicate content. You can set this to True if you know the server will not duplicate the structured content in the `tool_result.content`.
- **max_retry_attempts** (int) - Optional - Number of times to retry failed list_tools/call_tool calls. Defaults to no retries.
- **retry_backoff_seconds_base** (float) - Optional - The base delay, in seconds, for exponential backoff between retries.
- **message_handler** (MessageHandlerFnT | None) - Optional - Optional handler invoked for session messages as delivered by the ClientSession.

### Request Example
```json
{
  "params": {
    "url": "http://example.com/mcp",
    "headers": {"Authorization": "Bearer YOUR_TOKEN"},
    "timeout": 10,
    "sse_read_timeout": 300,
    "terminate_on_close": false,
    "httpx_client_factory": null 
  },
  "cache_tools_list": true,
  "name": "MyMCPStreamServer",
  "client_session_timeout_seconds": 10,
  "tool_filter": null,
  "use_structured_content": false,
  "max_retry_attempts": 3,
  "retry_backoff_seconds_base": 1.5,
  "message_handler": null
}
```

### Response
#### Success Response (200)
This method does not return a value directly upon initialization. It sets up the server instance.

#### Response Example
N/A
```

--------------------------------

### response_span

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/create

Creates a new response span for tracing. This span is not started automatically and requires manual start/finish or use within a `with` statement.

```APIDOC
## POST /agents/tracing/response_span

### Description
Creates a new response span to trace an agent's response. The span must be manually started and finished or managed using a context manager (`with response_span()`).

### Method
POST

### Endpoint
/agents/tracing/response_span

### Parameters
#### Query Parameters
- **response** (Response | None) - Optional - The OpenAI Response object to associate with the span.
- **span_id** (str | None) - Optional - The ID for the span. If not provided, a unique ID will be generated. It is recommended to use `util.gen_span_id()` for consistent formatting.
- **parent** (Trace | Span[Any] | None) - Optional - The parent trace or span. If omitted, the current trace/span will be used.
- **disabled** (bool) - Optional - If set to True, the span will be created but not recorded. Defaults to False.

### Request Body
(No explicit request body; parameters are passed as arguments)

### Response
#### Success Response (200)
- **Span[ResponseSpanData]** - The created response span object.

#### Response Example
```json
{
  "span": {
    "span_id": "generated_or_provided_id",
    "parent_id": "optional_parent_id",
    "data": {
      "response": { ... OpenAI Response Object ... }
    }
  }
}
```
```

--------------------------------

### Logging Usage in Run Hooks

Source: https://openai.github.io/openai-agents-python/usage

Provides an example of how to access and log token usage metrics within a custom `RunHooks` implementation, specifically in the `on_agent_end` hook. This allows for real-time monitoring and logging of agent performance and resource consumption at key lifecycle points.

```python
class MyHooks(RunHooks):
    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        u = context.usage
        print(f"{agent.name} → {u.requests} requests, {u.total_tokens} total tokens")
```

--------------------------------

### Basic Agent Configuration with Tools

Source: https://openai.github.io/openai-agents-python/agents

Demonstrates how to configure a basic agent with a name, instructions, model, and a custom function tool for retrieving weather information. The `get_weather` function is decorated with `@function_tool` to be usable by the agent.

```python
from agents import Agent, ModelSettings, function_tool

@function_tool
def get_weather(city: str) -> str:
    """returns weather info for the specified city."""
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Haiku agent",
    instructions="Always respond in haiku form",
    model="gpt-5-nano",
    tools=[get_weather],
)
```

--------------------------------

### Establish OpenAI Realtime API Connection (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/openai_realtime

This Python `async` function, `connect`, establishes a connection to the OpenAI Realtime API. It takes `RealtimeModelConfig` options, sets up the websocket URL, handles API keys and custom headers, and initiates a background task to listen for incoming messages. It also updates the session configuration based on initial model settings.

```python
async def connect(self, options: RealtimeModelConfig) -> None:
    """Establish a connection to the model and keep it alive."""
    assert self._websocket is None, "Already connected"
    assert self._websocket_task is None, "Already connected"

    model_settings: RealtimeSessionModelSettings = options.get("initial_model_settings", {})

    self._playback_tracker = options.get("playback_tracker", None)

    call_id = options.get("call_id")
    model_name = model_settings.get("model_name")
    if call_id and model_name:
        error_message =
            "Cannot specify both `call_id` and `model_name` "
            "when attaching to an existing realtime call."
        raise UserError(error_message)

    if model_name:
        self.model = model_name

    self._call_id = call_id
    api_key = await get_api_key(options.get("api_key"))

    if "tracing" in model_settings:
        self._tracing_config = model_settings["tracing"]
    else:
        self._tracing_config = "auto"

    if call_id:
        url = options.get("url", f"wss://api.openai.com/v1/realtime?call_id={call_id}")
    else:
        url = options.get("url", f"wss://api.openai.com/v1/realtime?model={self.model}")

    headers: dict[str, str] = {}
    if options.get("headers") is not None:
        # For customizing request headers
        headers.update(options["headers"])
    else:
        # OpenAI's Realtime API
        if not api_key:
            raise UserError("API key is required but was not provided.")

        headers.update({"Authorization": f"Bearer {api_key}"})

    self._websocket = await self._create_websocket_connection(
        url=url,
        headers=headers,
        transport_config=self._transport_config,
    )
    self._websocket_task = asyncio.create_task(self._listen_for_messages())
    await self._update_session_config(model_settings)
```

--------------------------------

### Tool Events API

Source: https://openai.github.io/openai-agents-python/ref/realtime/events

This section covers events related to tool calls made by agents. It includes events for when a tool call starts and when it ends.

```APIDOC
## Tool Events

### RealtimeToolStart

#### Description
An agent is starting a tool call.

### Method
Not Applicable (Event)

### Endpoint
Not Applicable (Event)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
* **agent** (RealtimeAgent) - Required - The agent that updated.
* **tool** (Tool) - Required - The tool being called.
* **arguments** (str) - Required - The arguments passed to the tool as a JSON string.
* **info** (RealtimeEventInfo) - Required - Common info for all events, such as the context.
* **type** (Literal["tool_start"]) - Required - The event type, fixed to "tool_start".

### Request Example
```json
{
  "agent": { ... },
  "tool": { ... },
  "arguments": "{\"key\": \"value\"}",
  "info": { ... },
  "type": "tool_start"
}
```

### Response
#### Success Response (200)
Not Applicable (Event)

#### Response Example
None

---

### RealtimeToolEnd

#### Description
An agent has ended a tool call.

### Method
Not Applicable (Event)

### Endpoint
Not Applicable (Event)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
* **agent** (RealtimeAgent) - Required - The agent that ended the tool call.
* **tool** (Tool) - Required - The tool that was called.
* **arguments** (str) - Required - The arguments passed to the tool as a JSON string.
* **output** (Any) - Required - The output of the tool call.
* **info** (RealtimeEventInfo) - Required - Common info for all events, such as the context.
* **type** (Literal["tool_end"]) - Required - The event type, fixed to "tool_end".

### Request Example
```json
{
  "agent": { ... },
  "tool": { ... },
  "arguments": "{\"key\": \"value\"}",
  "output": { ... },
  "info": { ... },
  "type": "tool_end"
}
```

### Response
#### Success Response (200)
Not Applicable (Event)

#### Response Example
None
```

--------------------------------

### Define RealtimeAgentStartEvent in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/events

Defines the RealtimeAgentStartEvent dataclass, which is emitted when a new agent has started. It includes the agent object and common event information.

```python
@dataclass
class RealtimeAgentStartEvent:
    """A new agent has started."""

    agent: RealtimeAgent
    """The new agent."""

    info: RealtimeEventInfo
    """Common info for all events, such as the context."""

    type: Literal["agent_start"] = "agent_start"

```

--------------------------------

### Initialize StreamedAudioResult in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/result

Initializes a new StreamedAudioResult instance. It takes TTS model, TTS settings, and voice pipeline configuration as required arguments. This setup is crucial for managing the streaming of voice and audio data.

```python
def __init__(
    self,
    tts_model: TTSModel,
    tts_settings: TTSModelSettings,
    voice_pipeline_config: VoicePipelineConfig,
):
    """Create a new `StreamedAudioResult` instance.

    Args:
        tts_model: The TTS model to use.
        tts_settings: The TTS settings to use.
        voice_pipeline_config: The voice pipeline config to use.
    """
    self.tts_model = tts_model
    self.tts_settings = tts_settings
    self.total_output_text = ""
    self.instructions = tts_settings.instructions
    self.text_generation_task: asyncio.Task[Any] | None = None

    self._voice_pipeline_config = voice_pipeline_config
    self._text_buffer = ""
    self._turn_text_buffer = ""
    self._queue: asyncio.Queue[VoiceStreamEvent] = asyncio.Queue()
    self._tasks: list[asyncio.Task[Any]] = []
    self._ordered_tasks: list[
        asyncio.Queue[VoiceStreamEvent | None]
    ] = []  # New: list to hold local queues for each text segment
    self._dispatcher_task: asyncio.Task[Any] | None = (
        None  # Task to dispatch audio chunks in order
    )

    self._done_processing = False
    self._buffer_size = tts_settings.buffer_size
    self._started_processing_turn = False
    self._first_byte_received = False
    self._generation_start_time: str | None = None
    self._completed_session = False
    self._stored_exception: BaseException | None = None
    self._tracing_span: Span[SpeechGroupSpanData] | None = None

```

--------------------------------

### Configure Agent Prompt in Python

Source: https://openai.github.io/openai-agents-python/ref/agent

This Python code snippet shows how to get the prompt for an agent. It utilizes a `PromptUtil` to convert the agent's `prompt` attribute into a model input, passing the `run_context` and the agent instance. This allows for dynamic configuration of agent prompts.

```python
from typing import TypeVar, Generic

# Assuming RunContextWrapper, ResponsePromptParam, PromptUtil, Prompt, DynamicPromptFunction are defined elsewhere
# class RunContextWrapper:
#     pass
# class ResponsePromptParam:
#     pass
# class PromptUtil:
#     @staticmethod
#     async def to_model_input(prompt, run_context, agent) -> ResponsePromptParam | None:
#         # Placeholder implementation
#         print(f"Converting prompt: {prompt} with context: {run_context} and agent: {agent}")
#         return ResponsePromptParam()

# class Prompt:
#     pass
# class DynamicPromptFunction:
#     pass

TContext = TypeVar("TContext")

class PromptUtil:
    @staticmethod
    async def to_model_input(prompt: 'Prompt | DynamicPromptFunction | None', run_context: 'RunContextWrapper[TContext]', agent: 'Agent[TContext]') -> 'ResponsePromptParam | None':
        # Placeholder implementation
        print(f"Converting prompt: {prompt} with context: {run_context} and agent: {agent}")
        if prompt is not None:
            return ResponsePromptParam()
        return None

class ResponsePromptParam:
    pass

class RunContextWrapper(Generic[TContext]):
    pass

class Agent(Generic[TContext]):
    def __init__(self, prompt: 'Prompt | DynamicPromptFunction | None'):
        self.prompt = prompt

    async def get_prompt(self, run_context: RunContextWrapper[TContext]) -> ResponsePromptParam | None:
        """Get the prompt for the agent."""
        return await PromptUtil.to_model_input(self.prompt, run_context, self)

# Example Usage:
# async def main():
#     # Assuming Prompt and RunContextWrapper are defined
#     mock_prompt = Prompt()
#     mock_context = RunContextWrapper()
#     mock_agent = Agent(prompt=mock_prompt)
#     result = await mock_agent.get_prompt(mock_context)
#     print(result)

# import asyncio
# asyncio.run(main())

```

--------------------------------

### Speech Span Creation

Source: https://openai.github.io/openai-agents-python/ref/tracing/create

Creates a new speech span for tracing text-to-speech operations. The span requires manual starting and finishing or usage within a `with` statement.

```APIDOC
## POST /speech_span

### Description
Creates a new speech span for tracing text-to-speech operations. The span will not be started automatically; you should either use `with speech_span() ...` or call `span.start()` and `span.finish()` manually.

### Method
POST

### Endpoint
`/speech_span`

### Parameters
#### Query Parameters
- **model** (str | None) - Optional - The name of the model used for the text-to-speech.
- **input** (str | None) - Optional - The text input of the text-to-speech.
- **output** (str | None) - Optional - The audio output of the text-to-speech as base64 encoded string of PCM audio bytes.
- **output_format** (str | None) - Optional - The format of the audio output (defaults to "pcm").
- **model_config** (Mapping[str, Any] | None) - Optional - The model configuration (hyperparameters) used.
- **first_content_at** (str | None) - Optional - The time of the first byte of the audio output.
- **span_id** (str | None) - Optional - The ID of the span. If not provided, an ID will be generated. It is recommended to use `util.gen_span_id()` for correct formatting.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, the current trace/span will be used as the parent.
- **disabled** (bool) - Optional - If True, a Span will be returned but not recorded. Defaults to False.

### Request Example
```json
{
  "model": "tts-1",
  "input": "Hello, world!",
  "output_format": "mp3"
}
```

### Response
#### Success Response (200)
- **Span[SpeechSpanData]** - Represents the created speech span.

#### Response Example
(This would typically be a Span object representation, not a simple JSON structure. The actual return type is `Span[SpeechSpanData]`.)
```
# Example of how to use it in code:
# from agents.tracing import speech_span
# 
# with speech_span(model="tts-1", input="Hello") as span:
#     # Perform speech synthesis operations
#     pass
```
```

--------------------------------

### AdvancedSQLiteSession Initialization

Source: https://openai.github.io/openai-agents-python/sessions/advanced_sqlite_session

Demonstrates how to initialize the AdvancedSQLiteSession with different configurations, including in-memory storage, persistent storage, and custom logging.

```APIDOC
## AdvancedSQLiteSession Initialization

### Description
Initializes the `AdvancedSQLiteSession` with various options for conversation storage and logging.

### Method
__init__

### Parameters
#### Path Parameters
- `session_id` (str) - Required - Unique identifier for the conversation session
- `db_path` (str | Path) - Optional - Path to SQLite database file. Defaults to `:memory:` for in-memory storage.
- `create_tables` (bool) - Optional - Whether to automatically create the advanced tables. Defaults to `False`.
- `logger` (logging.Logger | None) - Optional - Custom logger for the session. Defaults to module logger.

### Request Example
```python
from agents.extensions.memory import AdvancedSQLiteSession

# Basic initialization
session = AdvancedSQLiteSession(
    session_id="my_conversation",
    create_tables=True  # Auto-create advanced tables
)

# With persistent storage
session = AdvancedSQLiteSession(
    session_id="user_123",
    db_path="path/to/conversations.db",
    create_tables=True
)

# With custom logger
import logging
logger = logging.getLogger("my_app")
session = AdvancedSQLiteSession(
    session_id="session_456",
    create_tables=True,
    logger=logger
)
```
```

--------------------------------

### Handle Trace Start Event in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/provider

The `on_trace_start` method is invoked when a new trace begins. It iterates through registered processors, calling their respective `on_trace_start` methods to handle the event. Errors during processor execution are logged.

```python
def on_trace_start(self, trace: Trace) -> None:
    """
    Called when a trace is started.
    """
    for processor in self._processors:
        try:
            processor.on_trace_start(trace)
        except Exception as e:
            logger.error(f"Error in trace processor {processor} during on_trace_start: {e}")
```

--------------------------------

### Run LLM Start Callback in Python

Source: https://openai.github.io/openai-agents-python/ko/ref/lifecycle

The `on_llm_start` asynchronous method in `RunHooksBase` is called just before an LLM invocation occurs within an agent run. It receives context, the agent instance, the system prompt, and input items, allowing inspection or modification before the LLM call.

```python
async def on_llm_start(
    context: RunContextWrapper[TContext],
    agent: Agent[TContext],
    system_prompt: Optional[str],
    input_items: list[TResponseInputItem],
) -> None:
    pass
```

--------------------------------

### Initialize RealtimeSession in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/session

Initializes the RealtimeSession with a model, agent, and context. Supports optional model and run configurations, including guardrails. Dependencies include RealtimeModel, RealtimeAgent, and various configuration types.

```python
def __init__(
    self,
    model: RealtimeModel,
    agent: RealtimeAgent,
    context: TContext | None,
    model_config: RealtimeModelConfig | None = None,
    run_config: RealtimeRunConfig | None = None,
) -> None:
    """Initialize the session.

    Args:
        model: The model to use.
        agent: The current agent.
        context: The context object.
        model_config: Model configuration.
        run_config: Runtime configuration including guardrails.
    """
    self._model = model
    self._current_agent = agent
    self._context_wrapper = RunContextWrapper(context)
    self._event_info = RealtimeEventInfo(context=self._context_wrapper)
    self._history: list[RealtimeItem] = []
    self._model_config = model_config or {}
    self._run_config = run_config or {}
    initial_model_settings = self._model_config.get("initial_model_settings")
    run_config_settings = self._run_config.get("model_settings")
    self._base_model_settings: RealtimeSessionModelSettings = {
        **(run_config_settings or {}),
        **(initial_model_settings or {}),
    }
    self._event_queue: asyncio.Queue[RealtimeSessionEvent] = asyncio.Queue()
    self._closed = False
    self._stored_exception: BaseException | None = None

    # Guardrails state tracking
    self._interrupted_response_ids: set[str] = set()
    self._item_transcripts: dict[str, str] = {}  # item_id -> accumulated transcript
    self._item_guardrail_run_counts: dict[str, int] = {}  # item_id -> run count
    self._debounce_text_length = self._run_config.get("guardrails_settings", {}).get(
        "debounce_text_length", 100
    )

    self._guardrail_tasks: set[asyncio.Task[Any]] = set()
    self._tool_call_tasks: set[asyncio.Task[Any]] = set()
    self._async_tool_calls: bool = bool(self._run_config.get("async_tool_calls", True))
```

--------------------------------

### Handle Span Start Event in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/provider

This method, `on_span_start`, is triggered at the beginning of a span's execution. It delegates the event to all configured trace processors, enabling them to initiate span-specific logic. Any exceptions raised by processors are logged.

```python
def on_span_start(self, span: Span[Any]) -> None:
    """
    Called when a span is started.
    """
    for processor in self._processors:
        try:
            processor.on_span_start(span)
        except Exception as e:
            logger.error(f"Error in trace processor {processor} during on_span_start: {e}")
```

--------------------------------

### Configure MCP Servers for Agent (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/agent

Defines a list of Model Context Protocol (MCP) servers that the agent can use. Tools from these servers are included in the agent's available tools during execution. Note: Server lifecycle management (connect/cleanup) is the user's responsibility.

```python
mcp_servers: list[MCPServer] = field(default_factory=list)
```

--------------------------------

### GET /api/sessions/{session_id}/items

Source: https://openai.github.io/openai-agents-python/ja/ref/memory/sqlite_session

Retrieves the conversation history for a given session, optionally limited to the latest N items.

```APIDOC
## GET /api/sessions/{session_id}/items

### Description
Retrieve the conversation history for this session.

### Method
GET

### Endpoint
/api/sessions/{session_id}/items

### Parameters
#### Query Parameters
- **limit** (integer) - Optional - Maximum number of items to retrieve. If None, retrieves all items. When specified, returns the latest N items in chronological order.

### Response
#### Success Response (200)
- **items** (list[object]) - List of input items representing the conversation history

#### Response Example
{
  "items": [
    {
      "role": "user",
      "content": "Hello!"
    },
    {
      "role": "assistant",
      "content": "Hi there! How can I help you today?"
    }
  ]
}
```

--------------------------------

### Python: Tool Call Handling in RealtimeSession

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/session

Manages the execution of tool calls within the OpenAI agent framework. It identifies available tools and handoffs, initiates tool execution, and sends the output back to the model.

```python
async def _handle_tool_call(
        self,
        event: RealtimeModelToolCallEvent,
        *, 
        agent_snapshot: RealtimeAgent | None = None,
    ) -> None:
        """Handle a tool call event."""
        agent = agent_snapshot or self._current_agent
        tools, handoffs = await asyncio.gather(
            agent.get_all_tools(self._context_wrapper),
            self._get_handoffs(agent, self._context_wrapper),
        )
        function_map = {tool.name: tool for tool in tools if isinstance(tool, FunctionTool)}
        handoff_map = {handoff.tool_name: handoff for handoff in handoffs}

        if event.name in function_map:
            await self._put_event(
                RealtimeToolStart(
                    info=self._event_info,
                    tool=function_map[event.name],
                    agent=agent,
                    arguments=event.arguments,
                )
            )

            func_tool = function_map[event.name]
            tool_context = ToolContext(
                context=self._context_wrapper.context,
                usage=self._context_wrapper.usage,
                tool_name=event.name,
                tool_call_id=event.call_id,
                tool_arguments=event.arguments,
            )
            result = await func_tool.on_invoke_tool(tool_context, event.arguments)

            await self._model.send_event(
                RealtimeModelSendToolOutput(tool_call=event, output=str(result), start_response=True)
            )

            await self._put_event(
                RealtimeToolEnd(
                    info=self._event_info,
                    tool=func_tool,
                )
            )

```

--------------------------------

### Get Response using LitellmModel in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/litellm

Fetches a response from the configured LiteLLM model. It handles system instructions, user input, model settings, tools, output schemas, and tracing. The method abstracts the underlying LiteLLM API call and processes the response, logging it for debugging purposes unless explicitly disabled.

```python
    async def get_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: list[Handoff],
        tracing: ModelTracing,
        previous_response_id: str | None = None,  # unused
        conversation_id: str | None = None,  # unused
        prompt: Any | None = None,
    ) -> ModelResponse:
        with generation_span(
            model=str(self.model),
            model_config=model_settings.to_json_dict()
            | {"base_url": str(self.base_url or ""), "model_impl": "litellm"},
            disabled=tracing.is_disabled(),
        ) as span_generation:
            response = await self._fetch_response(
                system_instructions,
                input,
                model_settings,
                tools,
                output_schema,
                handoffs,
                span_generation,
                tracing,
                stream=False,
                prompt=prompt,
            )

            message: litellm.types.utils.Message | None = None
            first_choice: litellm.types.utils.Choices | None = None
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if isinstance(choice, litellm.types.utils.Choices):
                    first_choice = choice
                    message = first_choice.message

            if _debug.DONT_LOG_MODEL_DATA:
                logger.debug("Received model response")
            else:
                if message is not None:
                    logger.debug(
                        f"""LLM resp:\n{ 
                            json.dumps(message.model_dump(), indent=2, ensure_ascii=False)
                        }\n"""
                    )
                else:

```

--------------------------------

### Create Transcription Span

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing

Creates a new transcription span for speech-to-text processing. The span needs to be manually started and finished or used within a 'with' statement.

```APIDOC
## POST /v1/spans/transcription

### Description
Creates a new transcription span for speech-to-text processing. The span needs to be manually started and finished or used within a 'with' statement.

### Method
POST

### Endpoint
/v1/spans/transcription

### Parameters
#### Query Parameters
- **model** (str | None) - Optional - The name of the model used for the speech-to-text.
- **input** (str | None) - Optional - The audio input of the speech-to-text transcription, as a base64 encoded string of audio bytes.
- **input_format** (str | None) - Optional - The format of the audio input (defaults to "pcm").
- **output** (str | None) - Optional - The output of the speech-to-text transcription.
- **model_config** (Mapping[str, Any] | None) - Optional - The model configuration (hyperparameters) used.
- **span_id** (str | None) - Optional - The ID of the span. If not provided, a new ID will be generated.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, the current trace/span will be used.
- **disabled** (bool) - Optional - If True, the span will not be recorded.

### Request Example
```json
{
  "model": "whisper-1",
  "input": "base64_encoded_audio_data",
  "input_format": "mp3"
}
```

### Response
#### Success Response (200)
- **Span[TranscriptionSpanData]** - The newly created speech-to-text span.
```

--------------------------------

### Initialize Streamable HTTP Client with Parameters

Source: https://openai.github.io/openai-agents-python/ref/mcp/server

Initializes the Streamable HTTP client with various parameters including tool caching, session timeouts, retry configurations, and message handling. It sets up the client's internal state and names the instance based on the provided URL.

```python
class StreamableHTTP:
    def __init__(self, params, cache_tools_list, client_session_timeout_seconds, tool_filter, use_structured_content, max_retry_attempts, retry_backoff_seconds_base, message_handler=None, name=None):
        super().__init__(
            cache_tools_list,
            client_session_timeout_seconds,
            tool_filter,
            use_structured_content,
            max_retry_attempts,
            retry_backoff_seconds_base,
            message_handler=message_handler,
        )

        self.params = params
        self._name = name or f"streamable_http: {self.params['url']}"
```

--------------------------------

### Get Tool Usage

Source: https://openai.github.io/openai-agents-python/ko/ref/extensions/memory/advanced_sqlite_session

Retrieves a list of all tool usage, including the tool name, count, and the turn number in which it was used, for a specified branch. Defaults to the current branch if no branch ID is provided.

```APIDOC
## GET /tools/usage

### Description
Retrieves a list of all tool usage grouped by turn for a specified branch.

### Method
GET

### Endpoint
/tools/usage

### Parameters
#### Query Parameters
- **branch_id** (string) - Optional - The branch ID to retrieve tool usage from. Defaults to the current branch if not provided.

### Request Example
```json
{
  "branch_id": "optional_branch_id"
}
```

### Response
#### Success Response (200)
- Returns a list of tuples, where each tuple contains:
  - **tool_name** (string) - The name of the tool.
  - **usage_count** (integer) - The number of times the tool was used.
  - **turn_number** (integer) - The turn number in which the tool was used.

#### Response Example
```json
[
  ["get_weather", 1, 1],
  ["calculate_area", 2, 2]
]
```
```

--------------------------------

### RealtimeAgent Class Definition and Initialization

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/agent

Defines the RealtimeAgent class, inheriting from AgentBase and supporting generic context types. It outlines supported and unsupported configuration options for voice agents within a RealtimeSession, including instructions, prompts, handoffs, output guardrails, and hooks.

```python
from dataclasses import dataclass, field
from typing import Any, Generic, TContext, Callable, MaybeAwaitable, cast, Awaitable

from src.agents.base import AgentBase
from src.agents.realtime.hooks import RealtimeAgentHooks
from src.context import RunContextWrapper
from src.prompts import Prompt
from src.tools.handoff import Handoff
from src.types import OutputGuardrail

import inspect
import logging

logger = logging.getLogger(__name__)


@dataclass
class RealtimeAgent(AgentBase, Generic[TContext]):
    """A specialized agent instance that is meant to be used within a `RealtimeSession` to build
    voice agents. Due to the nature of this agent, some configuration options are not supported
    that are supported by regular `Agent` instances. For example:
    - `model` choice is not supported, as all RealtimeAgents will be handled by the same model
      within a `RealtimeSession`.
    - `modelSettings` is not supported, as all RealtimeAgents will be handled by the same model
      within a `RealtimeSession`.
    - `outputType` is not supported, as RealtimeAgents do not support structured outputs.
    - `toolUseBehavior` is not supported, as all RealtimeAgents will be handled by the same model
      within a `RealtimeSession`.
    - `voice` can be configured on an `Agent` level; however, it cannot be changed after the first
      agent within a `RealtimeSession` has spoken.

    See `AgentBase` for base parameters that are shared with `Agent`s.
    """

    instructions: (
        str
        | Callable[
            [RunContextWrapper[TContext], RealtimeAgent[TContext]],
            MaybeAwaitable[str],
        ]
        | None
    ) = None
    """The instructions for the agent. Will be used as the "system prompt" when this agent is
    invoked. Describes what the agent should do, and how it responds.

    Can either be a string, or a function that dynamically generates instructions for the agent. If
    you provide a function, it will be called with the context and the agent instance. It must
    return a string.
    """

    prompt: Prompt | None = None
    """A prompt object. Prompts allow you to dynamically configure the instructions, tools
    and other config for an agent outside of your code. Only usable with OpenAI models.
    """

    handoffs: list[RealtimeAgent[Any] | Handoff[TContext, RealtimeAgent[Any]]] = field(
        default_factory=list
    )
    """Handoffs are sub-agents that the agent can delegate to. You can provide a list of handoffs,
    and the agent can choose to delegate to them if relevant. Allows for separation of concerns and
    modularity.
    """

    output_guardrails: list[OutputGuardrail[TContext]] = field(default_factory=list)
    """A list of checks that run on the final output of the agent, after generating a response.
    Runs only if the agent produces a final output.
    """

    hooks: RealtimeAgentHooks | None = None
    """A class that receives callbacks on various lifecycle events for this agent.
    """

    def clone(self, **kwargs: Any) -> RealtimeAgent[TContext]:
        """Make a copy of the agent, with the given arguments changed. For example, you could do:
        ```
        new_agent = agent.clone(instructions="New instructions")
        ```
        """
        return dataclasses.replace(self, **kwargs)

    async def get_system_prompt(self, run_context: RunContextWrapper[TContext]) -> str | None:
        """Get the system prompt for the agent."""
        if isinstance(self.instructions, str):
            return self.instructions
        elif callable(self.instructions):
            if inspect.iscoroutinefunction(self.instructions):
                return await cast(Awaitable[str], self.instructions(run_context, self))
            else:
                return cast(str, self.instructions(run_context, self))
        elif self.instructions is not None:
            logger.error(f"Instructions must be a string or a function, got {self.instructions}")

        return None

```

--------------------------------

### Agent Start Callback in Python

Source: https://openai.github.io/openai-agents-python/ko/ref/lifecycle

The `on_agent_start` asynchronous method in `RunHooksBase` is called before an agent is invoked, particularly when the current agent changes. It receives the agent hook context and the agent instance that is about to be executed.

```python
async def on_agent_start(context: AgentHookContext[TContext], agent: TAgent) -> None:
    pass
```

--------------------------------

### Create Trace in Python

Source: https://openai.github.io/openai-agents-python/ref/tracing/create

Creates a new trace, which can be used as a context manager or started/finished manually. It allows for attaching metadata and configuring tracing export. The trace is not automatically started.

```python
def trace(
    workflow_name: str,
    trace_id: str | None = None,
    group_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    tracing: TracingConfig | None = None,
    disabled: bool = False,
) -> Trace:
    """
    Create a new trace. The trace will not be started automatically; you should either use
    it as a context manager (`with trace(...):`) or call `trace.start()` + `trace.finish()`
    manually.

    In addition to the workflow name and optional grouping identifier, you can provide
    an arbitrary metadata dictionary to attach additional user-defined information to
    the trace.

    Args:
        workflow_name: The name of the logical app or workflow. For example, you might provide
            "code_bot" for a coding agent, or "customer_support_agent" for a customer support agent.
        trace_id: The ID of the trace. Optional. If not provided, we will generate an ID. We
            recommend using `util.gen_trace_id()` to generate a trace ID, to guarantee that IDs are
            correctly formatted.
        group_id: Optional grouping identifier to link multiple traces from the same conversation
            or process. For instance, you might use a chat thread ID.
        metadata: Optional dictionary of additional metadata to attach to the trace.
        tracing: Optional tracing configuration for exporting this trace.
        disabled: If True, we will return a Trace but the Trace will not be recorded.

    Returns:
        The newly created trace object.
    """
    current_trace = get_trace_provider().get_current_trace()
    if current_trace:
        logger.warning(
            "Trace already exists. Creating a new trace, but this is probably a mistake."
        )

    return get_trace_provider().create_trace(
        name=workflow_name,
        trace_id=trace_id,
        group_id=group_id,
        metadata=metadata,
        tracing=tracing,
        disabled=disabled,
    )
```

--------------------------------

### Get Conversation by Turns

Source: https://openai.github.io/openai-agents-python/ko/ref/extensions/memory/advanced_sqlite_session

Retrieves the conversation history grouped by user turns for a specified branch. If no branch ID is provided, it defaults to the current branch.

```APIDOC
## GET /conversations/by_turns

### Description
Retrieves conversation history grouped by user turns for a specific branch.

### Method
GET

### Endpoint
/conversations/by_turns

### Parameters
#### Query Parameters
- **branch_id** (string) - Optional - The branch ID to retrieve the conversation from. Defaults to the current branch if not provided.

### Request Example
```json
{
  "branch_id": "optional_branch_id"
}
```

### Response
#### Success Response (200)
- **turn_number** (integer) - The turn number in the conversation.
- **messages** (array) - A list of messages within that turn.
  - **type** (string) - The type of message (e.g., 'user', 'assistant', 'tool').
  - **tool_name** (string) - The name of the tool used, if applicable.

#### Response Example
```json
{
  "1": [
    {
      "type": "user",
      "tool_name": null
    },
    {
      "type": "assistant",
      "tool_name": null
    }
  ],
  "2": [
    {
      "type": "tool_call",
      "tool_name": "get_weather"
    },
    {
      "type": "assistant",
      "tool_name": null
    }
  ]
}
```
```

--------------------------------

### Agent Configuration and Validation in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/agent

This Python code defines the configuration for an agent, including its name, tools, instructions, and model settings. It also includes validation logic within the `__post_init__` method to ensure that the provided configuration parameters are of the correct types, raising `TypeError` if they are not. This ensures the agent is initialized with valid settings.

```python
from typing import Any, Literal
from .models.interface import Model
from .models.settings import ModelSettings
from .schemas.base import AgentOutputSchemaBase
from .schemas.output import AgentOutputSchema
from .types import AgentHooks, StopAtTools, ToolsToFinalOutputFunction


class Agent:
    """A class that represents an agent.

    Attributes:
        name (str): The name of the agent.
        description (str | None): A description of the agent.
        output_type (type[Any] | AgentOutputSchemaBase | None): The type of the output object.
        hooks (AgentHooks[TContext] | None): A class that receives callbacks on various lifecycle events for this agent.
        tool_use_behavior (Literal["run_llm_again", "stop_on_first_tool"] | StopAtTools | ToolsToFinalOutputFunction): Configures how tool use is handled.
        reset_tool_choice (bool): Whether to reset the tool choice after a tool has been called.
    """

    name: str
    description: str | None = None
    output_type: type[Any] | AgentOutputSchemaBase | None = None
    """The type of the output object. If not provided, the output will be `str`. In most cases,
    you should pass a regular Python type (e.g. a dataclass, Pydantic model, TypedDict, etc).
    You can customize this in two ways:
    1. If you want non-strict schemas, pass `AgentOutputSchema(MyClass, strict_json_schema=False)`.
    2. If you want to use a custom JSON schema (i.e. without using the SDK's automatic schema) 
       creation, subclass and pass an `AgentOutputSchemaBase` subclass.
    """

    hooks: AgentHooks[TContext] | None = None
    """A class that receives callbacks on various lifecycle events for this agent.
    """

    tool_use_behavior: (
        Literal["run_llm_again", "stop_on_first_tool"] | StopAtTools | ToolsToFinalOutputFunction
    ) = "run_llm_again"
    """
    This lets you configure how tool use is handled.
    - "run_llm_again": The default behavior. Tools are run, and then the LLM receives the results
        and gets to respond.
    - "stop_on_first_tool": The output from the first tool call is treated as the final result.
        In other words, it isn’t sent back to the LLM for further processing but is used directly
        as the final output.
    - A StopAtTools object: The agent will stop running if any of the tools listed in
        `stop_at_tool_names` is called.
        The final output will be the output of the first matching tool call.
        The LLM does not process the result of the tool call.
    - A function: If you pass a function, it will be called with the run context and the list of
      tool results. It must return a `ToolsToFinalOutputResult`, which determines whether the tool
      calls result in a final output.

      NOTE: This configuration is specific to FunctionTools. Hosted tools, such as file search,
      web search, etc. are always processed by the LLM.
    """

    reset_tool_choice: bool = True
    """Whether to reset the tool choice to the default value after a tool has been called. Defaults
    to True. This ensures that the agent doesn't enter an infinite loop of tool usage.
    """

    def __post_init__(self):
        from typing import get_origin

        if not isinstance(self.name, str):
            raise TypeError(f"Agent name must be a string, got {type(self.name).__name__}")

        if self.handoff_description is not None and not isinstance(self.handoff_description, str):
            raise TypeError(
                f"Agent handoff_description must be a string or None, "
                f"got {type(self.handoff_description).__name__}"
            )

        if not isinstance(self.tools, list):
            raise TypeError(f"Agent tools must be a list, got {type(self.tools).__name__}")

        if not isinstance(self.mcp_servers, list):
            raise TypeError(
                f"Agent mcp_servers must be a list, got {type(self.mcp_servers).__name__}"
            )

        if not isinstance(self.mcp_config, dict):
            raise TypeError(
                f"Agent mcp_config must be a dict, got {type(self.mcp_config).__name__}"
            )

        if (
            self.instructions is not None
            and not isinstance(self.instructions, str)
            and not callable(self.instructions)
        ):
            raise TypeError(
                f"Agent instructions must be a string, callable, or None, "
                f"got {type(self.instructions).__name__}"
            )

        if (
            self.prompt is not None
            and not callable(self.prompt)
            and not hasattr(self.prompt, "get")
        ):
            raise TypeError(
                f"Agent prompt must be a Prompt, DynamicPromptFunction, or None, "
                f"got {type(self.prompt).__name__}"
            )

        if not isinstance(self.handoffs, list):
            raise TypeError(f"Agent handoffs must be a list, got {type(self.handoffs).__name__}")

        if self.model is not None and not isinstance(self.model, str):
            if not isinstance(self.model, Model):
                raise TypeError(
                    f"Agent model must be a string, Model, or None, got {type(self.model).__name__}"
                )

        if not isinstance(self.model_settings, ModelSettings):
            raise TypeError(
                f"Agent model_settings must be a ModelSettings instance, "
                f"got {type(self.model_settings).__name__}"
            )

        if (
            # The user sets a non-default model
            self.model is not None
            and (
                # The default model is gpt-5
                is_gpt_5_default() is True
                # However, the specified model is not a gpt-5 model
                and (

```

--------------------------------

### Server Configuration Parameters

Source: https://openai.github.io/openai-agents-python/zh/ref/mcp/server

This snippet shows how to retrieve server configuration parameters like timeouts and termination behavior. It uses a dictionary-like object `self.params` to get values, with default fallbacks.

```python
timeout=self.params.get("timeout", 5),
                sse_read_timeout=self.params.get("sse_read_timeout", 60 * 5),
                terminate_on_close=self.params.get("terminate_on_close", True),
            )
```

--------------------------------

### Create Handoff Span

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing

This endpoint allows you to create a new handoff span for tracing agent interactions. The span needs to be started and finished manually or used within a `with` statement.

```APIDOC
## POST /v1/spans/handoff

### Description
Creates a new handoff span. This span is not started automatically. You must use `with handoff_span() ...` or manually call `span.start()` and `span.finish()`.

### Method
POST

### Endpoint
/v1/spans/handoff

### Parameters
#### Query Parameters
- **from_agent** (string) - Optional - The name of the agent that is handing off.
- **to_agent** (string) - Optional - The name of the agent that is receiving the handoff.
- **span_id** (string) - Optional - The ID of the span. If not provided, an ID will be generated. It is recommended to use `util.gen_span_id()` for correctly formatted IDs.
- **parent** (Trace | Span[Any]) - Optional - The parent span or trace. If not provided, the current trace/span will be used as the parent.
- **disabled** (boolean) - Optional - If True, the created Span will not be recorded. Defaults to `False`.

### Request Body
This endpoint does not strictly require a request body, but it accepts parameters for span creation.

### Request Example
```json
{
  "from_agent": "AgentA",
  "to_agent": "AgentB",
  "span_id": "handoff-123",
  "disabled": false
}
```

### Response
#### Success Response (200)
- **span_id** (string) - The ID of the created handoff span.
- **status** (string) - The status of the span creation (e.g., 'created').

#### Response Example
```json
{
  "span_id": "handoff-123",
  "status": "created"
}
```
```

--------------------------------

### Agent Configuration with Prompt Template

Source: https://openai.github.io/openai-agents-python/agents

Shows how to configure an agent to use a pre-defined prompt template from the OpenAI platform. The `prompt` parameter accepts an object with `id`, `version`, and `variables` to specify the template and its dynamic values.

```python
from agents import Agent

agent = Agent(
    name="Prompted assistant",
    prompt={
        "id": "pmpt_123",
        "version": "1",
        "variables": {"poem_style": "haiku"},
    },
)
```

--------------------------------

### Create Trace

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing

Creates a new trace object. This trace can be used as a context manager or managed manually with start() and finish() methods. It allows for detailed logging and monitoring of workflow execution.

```APIDOC
## POST /trace

### Description
Creates a new trace for a given workflow. The trace is not automatically started and requires manual initiation using a context manager (`with trace(...)`) or explicit `start()` and `finish()` calls.

### Method
POST

### Endpoint
/trace

### Parameters
#### Query Parameters
- **workflow_name** (str) - Required - The name of the logical application or workflow (e.g., "code_bot").
- **trace_id** (str | None) - Optional - A unique identifier for the trace. If not provided, one will be generated.
- **group_id** (str | None) - Optional - An identifier to group related traces, such as a chat thread ID.
- **metadata** (dict[str, Any] | None) - Optional - A dictionary for attaching user-defined metadata to the trace.
- **tracing** (TracingConfig | None) - Optional - Configuration for exporting the trace.
- **disabled** (bool) - Optional - If True, the trace will be created but not recorded. Defaults to False.

### Request Body
(Not applicable for this function, parameters are passed as arguments)

### Response
#### Success Response (200)
- **Trace** (Trace) - The newly created trace object, which can be used for managing the trace lifecycle.
```

--------------------------------

### MultiProvider Model Retrieval Logic (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/models/multi_provider

Provides the `get_model` method, which takes a model name, determines its prefix, and uses either a custom provider from `provider_map` or a fallback provider (like OpenAI or Litellm) to retrieve the appropriate model instance.

```python
    def get_model(self, model_name: str | None) -> Model:
        """Returns a Model based on the model name. The model name can have a prefix, ending with
        a "/", which will be used to look up the ModelProvider. If there is no prefix, we will use
        the OpenAI provider.

        Args:
            model_name: The name of the model to get.

        Returns:
            A Model.
        """
        prefix, model_name = self._get_prefix_and_model_name(model_name)

        if prefix and self.provider_map and (provider := self.provider_map.get_provider(prefix)):
            return provider.get_model(model_name)
        else:
            return self._get_fallback_provider(prefix).get_model(model_name)

```

--------------------------------

### Get Tool Usage by Turn (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/memory/advanced_sqlite_session

Fetches all tool usage instances, grouped by turn, for a given branch. This asynchronous function utilizes a synchronous helper for database interaction, ensuring non-blocking operations. It returns a list of tuples, each containing the tool name, its usage count, and the corresponding turn number.

```python
async def get_tool_usage(self, branch_id: str | None = None) -> list[tuple[str, int, int]]:
    """Get all tool usage by turn for specified branch.

    Args:
        branch_id: Branch to get tool usage from (current branch if None).

    Returns:
        List of tuples containing (tool_name, usage_count, turn_number).
    """
    if branch_id is None:
        branch_id = self._current_branch_id

    def _get_tool_usage_sync():
        """Synchronous helper to get tool usage statistics."""
        conn = self._get_connection()
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                SELECT tool_name, COUNT(*), user_turn_number
                FROM message_structure
                WHERE session_id = ? AND branch_id = ? AND message_type IN (
                    'tool_call', 'function_call', 'computer_call', 'file_search_call',
                    'web_search_call', 'code_interpreter_call', 'custom_tool_call',
                    'mcp_call', 'mcp_approval_request'
                )
                GROUP BY tool_name, user_turn_number
                ORDER BY user_turn_number
            """,
                (self.session_id, branch_id),
            )
            return cursor.fetchall()

    return await asyncio.to_thread(_get_tool_usage_sync)
```

--------------------------------

### Implement Input Guardrail with Agent

Source: https://openai.github.io/openai-agents-python/guardrails

This snippet demonstrates how to create an input guardrail that uses an agent to check user input. It defines a Pydantic model for the guardrail's output and an agent to perform the check. The guardrail function then runs this agent and returns a GuardrailFunctionOutput.

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent( 
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered=result.final_output.is_math_homework,
    )


agent = Agent(  
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
)

async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except InputGuardrailTripwireTriggered:
        print("Math homework guardrail tripped")

```

--------------------------------

### Class Method: run_sync

Source: https://openai.github.io/openai-agents-python/zh/ref/run

Synchronously runs an agent workflow starting from a specified agent. This method is suitable for non-async environments and executes the agent loop until a final output is produced.

```APIDOC
## Class Method: run_sync

### Description
Runs a workflow synchronously, starting at the given agent. This method wraps the `run` method and is not suitable for environments with an existing event loop (e.g., async functions, Jupyter notebooks, FastAPI).

The agent executes in a loop: invoking the agent, checking for final output, handling agent handoffs, and executing tool calls.

Exceptions can be raised if `max_turns` is exceeded or a guardrail tripwire is triggered. Note that only the first agent's input guardrails are evaluated.

### Method
`classmethod`

### Endpoint
N/A (This is a class method, not a REST endpoint)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None

### Request Example
```python
# This is a conceptual example, actual usage requires Agent and other types to be defined.
# from agents import Agent, RunResult
# from typing import TypeVar, Generic

# TContext = TypeVar('TContext')
# TResponseInputItem = TypeVar('TResponseInputItem')

# class MyAgent(Agent[TContext]):
#     pass

# starting_agent = MyAgent()
# input_data = "Hello agent!"
# result: RunResult = MyAgent.run_sync(starting_agent, input_data)
```

### Response
#### Success Response (200)
- **RunResult** (object) - A run result object containing all inputs, guardrail results, and the final output of the last agent. The specific output type can vary due to agent handoffs.

#### Response Example
```json
{
  "inputs": [...],
  "guardrail_results": [...],
  "output": "..."
}
```

### Parameters Details:
- **starting_agent** (`Agent[TContext]`) - Required - The agent instance to begin the workflow.
- **input** (`str | list[TResponseInputItem]`) - Required - The initial input provided to the agent. Can be a single string or a list of input items.
- **context** (`TContext | None`) - Optional - The context object to be used during agent execution. Defaults to `None`.
- **max_turns** (`int`) - Optional - The maximum number of turns (AI invocations including tool calls) allowed in the agent run. Defaults to `DEFAULT_MAX_TURNS`.
- **hooks** (`RunHooks[TContext] | None`) - Optional - An object for receiving callbacks during various lifecycle events of the agent run. Defaults to `None`.
- **run_config** (`RunConfig | None`) - Optional - Global configuration settings for the entire agent run. Defaults to `None`.
- **previous_response_id** (`str | None`) - Optional - The ID of a previous response, useful for OpenAI models via the Responses API to avoid re-passing input from the prior turn. Defaults to `None`.
- **auto_previous_response_id** (`bool`) - Optional - If `True`, automatically uses the previous response ID when available. Defaults to `False`.
- **conversation_id** (`str | None`) - Optional - The ID of a stored conversation, if applicable. Defaults to `None`.
- **session** (`Session | None`) - Optional - A session object for managing conversation history automatically. Defaults to `None`.
```

--------------------------------

### Initialize AdvancedSQLiteSession

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/memory/advanced_sqlite_session

Initializes the AdvancedSQLiteSession with a session ID, optional database path, table creation flag, and logger. It sets up the session and optionally creates structure tables.

```python
def __init__(
    self,
    *,
    session_id: str,
    db_path: str | Path = ":memory:",
    create_tables: bool = False,
    logger: logging.Logger | None = None,
    **kwargs,
):
    """Initialize the AdvancedSQLiteSession.

    Args:
        session_id: The ID of the session
        db_path: The path to the SQLite database file. Defaults to `:memory:` for in-memory storage
        create_tables: Whether to create the structure tables
        logger: The logger to use. Defaults to the module logger
        **kwargs: Additional keyword arguments to pass to the superclass
    """  # noqa: E501
    super().__init__(session_id, db_path, **kwargs)
    if create_tables:
        self._init_structure_tables()
    self._current_branch_id = "main"
    self._logger = logger or logging.getLogger(__name__)

```

--------------------------------

### Get Prompt - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/mcp/server

Abstract method to retrieve a specific prompt from the server by its name, optionally with arguments. It returns a GetPromptResult. This asynchronous method is part of the server's API.

```python
import abc
from typing import Any

from .get_prompt_result import GetPromptResult


class MCPBase(abc.ABC):
    @abc.abstractmethod
    async def get_prompt(self, name: str, arguments: dict[str, Any] | None = None) -> GetPromptResult:
        """Get a specific prompt from the server."""
        pass

```

--------------------------------

### GET /items

Source: https://openai.github.io/openai-agents-python/zh/ref/extensions/memory/advanced_sqlite_session

Retrieves conversation items from the current or a specified branch. This endpoint allows fetching a list of items, optionally limited by a count and filtered by a specific branch ID.

```APIDOC
## GET /items

### Description
Retrieves conversation items from the current or a specified branch. This endpoint allows fetching a list of items, optionally limited by a count and filtered by a specific branch ID.

### Method
GET

### Endpoint
/items

### Parameters
#### Query Parameters
- **limit** (integer) - Optional - Maximum number of items to return. If not provided, returns all items.
- **branch_id** (string) - Optional - The ID of the branch to retrieve items from. If not provided, uses the current branch.

### Request Example
```json
{
  "limit": 10,
  "branch_id": "develop"
}
```

### Response
#### Success Response (200)
- **items** (list[object]) - A list of conversation items. Each item is a JSON object representing a message.

#### Response Example
```json
{
  "items": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    },
    {
      "role": "assistant",
      "content": "I'm doing well, thank you! How can I help you today?"
    }
  ]
}
```
```

--------------------------------

### agent_span

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing/create

Creates a new agent span for tracing agent activities. The span requires manual start and finish operations or can be used with a `with` statement.

```APIDOC
## POST /agent_span

### Description
Creates a new agent span to track agent activities. This span is not started automatically; users must explicitly call `span.start()` and `span.finish()` or use a `with agent_span() ...` block.

### Method
POST

### Endpoint
/agent_span

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **name** (str) - Required - The name of the agent.
- **handoffs** (list[str] | None) - Optional - A list of agent names to which this agent can hand off control.
- **tools** (list[str] | None) - Optional - A list of tool names available to this agent.
- **output_type** (str | None) - Optional - The name of the output type produced by the agent.
- **span_id** (str | None) - Optional - The ID of the span. If not provided, an ID will be generated. It is recommended to use `util.gen_span_id()` for correctly formatted IDs.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, the current trace/span will be used as the parent.
- **disabled** (bool) - Optional - If True, the span will be created but not recorded. Defaults to False.

### Request Example
```json
{
  "name": "MyAgent",
  "handoffs": ["OtherAgent"],
  "tools": ["Tool1", "Tool2"],
  "output_type": "string",
  "span_id": "generated-span-id",
  "parent": null,
  "disabled": false
}
```

### Response
#### Success Response (200)
- **Span[AgentSpanData]** - The newly created agent span, containing span details and data.

#### Response Example
```json
{
  "span_id": "generated-span-id",
  "name": "MyAgent",
  "type": "agent",
  "start_time": "2023-10-27T10:00:00Z",
  "end_time": null,
  "status": "running",
  "events": [],
  "attributes": {
    "handoffs": ["OtherAgent"],
    "tools": ["Tool1", "Tool2"],
    "output_type": "string"
  }
}
```
```

--------------------------------

### Include Handoff Instructions in Agent Prompt (Python)

Source: https://openai.github.io/openai-agents-python/handoffs

Shows how to integrate recommended handoff instructions into an agent's prompt using `RECOMMENDED_PROMPT_PREFIX` from `agents.extensions.handoff_prompt`. This helps LLMs understand and process handoff information correctly.

```python
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

billing_agent = Agent(
    name="Billing agent",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX}
    <Fill in the rest of your prompt here>.",
)
```

--------------------------------

### Define Agent Handoffs (Python)

Source: https://openai.github.io/openai-agents-python/quickstart

This Python code defines a 'Triage Agent' that can hand off tasks to other specialist agents like 'History Tutor' and 'Math Tutor'. The `handoffs` parameter is a list of agents the triage agent can delegate to.

```python
from agents import Agent

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent]
)
```

--------------------------------

### VoicePipeline Initialization and Execution (Python)

Source: https://openai.github.io/openai-agents-python/ko/ref/voice/pipeline

Initializes and runs the VoicePipeline, which processes audio input through transcription, a workflow, and text-to-speech synthesis. It supports both single audio inputs and streamed audio inputs.

```python
class VoicePipeline:
    """An opinionated voice agent pipeline. It works in three steps:
    1. Transcribe audio input into text.
    2. Run the provided `workflow`, which produces a sequence of text responses.
    3. Convert the text responses into streaming audio output.
    """

    def __init__(
        self,
        *,
        workflow: VoiceWorkflowBase,
        stt_model: STTModel | str | None = None,
        tts_model: TTSModel | str | None = None,
        config: VoicePipelineConfig | None = None,
    ):
        """Create a new voice pipeline.

        Args:
            workflow: The workflow to run. See `VoiceWorkflowBase`.
            stt_model: The speech-to-text model to use. If not provided, a default OpenAI
                model will be used.
            tts_model: The text-to-speech model to use. If not provided, a default OpenAI
                model will be used.
            config: The pipeline configuration. If not provided, a default configuration will be
                used.
        """
        self.workflow = workflow
        self.stt_model = stt_model if isinstance(stt_model, STTModel) else None
        self.tts_model = tts_model if isinstance(tts_model, TTSModel) else None
        self._stt_model_name = stt_model if isinstance(stt_model, str) else None
        self._tts_model_name = tts_model if isinstance(tts_model, str) else None
        self.config = config or VoicePipelineConfig()

    async def run(self, audio_input: AudioInput | StreamedAudioInput) -> StreamedAudioResult:
        """Run the voice pipeline.

        Args:
            audio_input: The audio input to process. This can either be an `AudioInput` instance,
                which is a single static buffer, or a `StreamedAudioInput` instance, which is a
                stream of audio data that you can append to.

        Returns:
            A `StreamedAudioResult` instance. You can use this object to stream audio events and
            play them out.
        """
        if isinstance(audio_input, AudioInput):
            return await self._run_single_turn(audio_input)
        elif isinstance(audio_input, StreamedAudioInput):
            return await self._run_multi_turn(audio_input)
        else:
            raise UserError(f"Unsupported audio input type: {type(audio_input)}")

    def _get_tts_model(self) -> TTSModel:
        if not self.tts_model:
            self.tts_model = self.config.model_provider.get_tts_model(self._tts_model_name)
        return self.tts_model

    def _get_stt_model(self) -> STTModel:
        if not self.stt_model:
            self.stt_model = self.config.model_provider.get_stt_model(self._stt_model_name)
        return self.stt_model

    async def _process_audio_input(self, audio_input: AudioInput) -> str:
        model = self._get_stt_model()
        return await model.transcribe(
            audio_input,
            self.config.stt_settings,
            self.config.trace_include_sensitive_data,
            self.config.trace_include_sensitive_audio_data,
        )

    async def _run_single_turn(self, audio_input: AudioInput) -> StreamedAudioResult:
        # Since this is single turn, we can use the TraceCtxManager to manage starting/ending the
        # trace
        with TraceCtxManager(
            workflow_name=self.config.workflow_name or "Voice Agent",
            trace_id=None,  # Automatically generated
            group_id=self.config.group_id,
            metadata=self.config.trace_metadata,
            tracing=self.config.tracing,
            disabled=self.config.tracing_disabled,
        ):
            input_text = await self._process_audio_input(audio_input)

            output = StreamedAudioResult(
                self._get_tts_model(), self.config.tts_settings, self.config
            )

            async def stream_events():
                try:
                    async for text_event in self.workflow.run(input_text):
                        await output._add_text(text_event)
                    await output._turn_done()
                    await output._done()

```

--------------------------------

### Get Speech-to-Text Model (Python)

Source: https://openai.github.io/openai-agents-python/ref/voice/models/openai_model_provider

Retrieves a Speech-to-Text (STT) model from the OpenAI provider. If no model name is specified, it defaults to `DEFAULT_STT_MODEL`. This function requires an initialized OpenAI client.

```python
def get_stt_model(self, model_name: str | None) -> STTModel:
    """Get a speech-to-text model by name.

    Args:
        model_name: The name of the model to get.

    Returns:
        The speech-to-text model.
    """
    return OpenAISTTModel(model_name or DEFAULT_STT_MODEL, self._get_client())
```

--------------------------------

### Get Text-to-Speech Model (Python)

Source: https://openai.github.io/openai-agents-python/ref/voice/models/openai_model_provider

Retrieves a Text-to-Speech (TTS) model from the OpenAI provider. If no model name is specified, it defaults to `DEFAULT_TTS_MODEL`. This function requires an initialized OpenAI client.

```python
def get_tts_model(self, model_name: str | None) -> TTSModel:
    """Get a text-to-speech model by name.

    Args:
        model_name: The name of the model to get.

    Returns:
        The text-to-speech model.
    """
    return OpenAITTSModel(model_name or DEFAULT_TTS_MODEL, self._get_client())
```

--------------------------------

### Get All Function Tools from MCP Servers (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/mcp/util

Retrieves all function tools from a list of MCP servers. It checks for duplicate tool names across servers to prevent conflicts. Dependencies include MCPServer, RunContextWrapper, AgentBase, and Tool.

```python
class MCPUtil:
    """Set of utilities for interop between MCP and Agents SDK tools."""

    @classmethod
    async def get_all_function_tools(
        cls,
        servers: list["MCPServer"],
        convert_schemas_to_strict: bool,
        run_context: RunContextWrapper[Any],
        agent: "AgentBase",
    ) -> list[Tool]:
        """Get all function tools from a list of MCP servers."""
        tools = []
        tool_names: set[str] = set()
        for server in servers:
            server_tools = await cls.get_function_tools(
                server, convert_schemas_to_strict, run_context, agent
            )
            server_tool_names = {tool.name for tool in server_tools}
            if len(server_tool_names & tool_names) > 0:
                raise UserError(
                    f"Duplicate tool names found across MCP servers: "
                    f"{server_tool_names & tool_names}"
                )
            tool_names.update(server_tool_names)
            tools.extend(server_tools)

        return tools
```

--------------------------------

### Initialize OpenAI Voice Model Provider (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/voice/models/openai_provider

Initializes the OpenAIVoiceModelProvider with optional OpenAI client configurations. It supports direct client injection or lazy initialization using API keys, base URLs, organization, and project details. Dependencies include the `AsyncOpenAI` client and potentially shared HTTP client configurations.

```python
class OpenAIVoiceModelProvider(VoiceModelProvider):
    """A voice model provider that uses OpenAI models."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        openai_client: AsyncOpenAI | None = None,
        organization: str | None = None,
        project: str | None = None,
    ) -> None:
        """Create a new OpenAI voice model provider.

        Args:
            api_key: The API key to use for the OpenAI client. If not provided, we will use the
                default API key.
            base_url: The base URL to use for the OpenAI client. If not provided, we will use the
                default base URL.
            openai_client: An optional OpenAI client to use. If not provided, we will create a new
                OpenAI client using the api_key and base_url.
            organization: The organization to use for the OpenAI client.
            project: The project to use for the OpenAI client.
        """
        if openai_client is not None:
            assert api_key is None and base_url is None,
                ("Don't provide api_key or base_url if you provide openai_client")
            self._client: AsyncOpenAI | None = openai_client
        else:
            self._client = None
            self._stored_api_key = api_key
            self._stored_base_url = base_url
            self._stored_organization = organization
            self._stored_project = project

    # We lazy load the client in case you never actually use OpenAIProvider(). Otherwise
    # AsyncOpenAI() raises an error if you don't have an API key set.
    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = _openai_shared.get_default_openai_client() or AsyncOpenAI(
                api_key=self._stored_api_key or _openai_shared.get_default_openai_key(),
                base_url=self._stored_base_url,
                organization=self._stored_organization,
                project=self._stored_project,
                http_client=shared_http_client(),
            )

        return self._client
```

--------------------------------

### Span Management Methods

Source: https://openai.github.io/openai-agents-python/ref/tracing

Abstract methods for controlling the lifecycle of a tracing span. The `start` method initiates the span, optionally marking it as the current span, while the `finish` method terminates the span, with an option to reset the current span.

```python
@abc.abstractmethod
def start(self, mark_as_current: bool = False):
    """
    Start the span.

    Args:
        mark_as_current: If true, the span will be marked as the current span.
    """
    pass
```

```python
@abc.abstractmethod
def finish(self, reset_current: bool = False) -> None:
    """
    Finish the span.

    Args:
        reset_current: If true, the span will be reset as the current span.
    """
    pass
```

--------------------------------

### OpenAI Voice Model Provider Initialization

Source: https://openai.github.io/openai-agents-python/ko/ref/voice/models/openai_model_provider

Initializes a new OpenAI voice model provider. You can provide an existing OpenAI client or specify API key, base URL, organization, and project details.

```APIDOC
## POST /voice/models/openai

### Description
Initializes a new OpenAI voice model provider. This allows for configuration via an existing OpenAI client or by providing API credentials and organizational details.

### Method
POST

### Endpoint
/voice/models/openai

### Parameters
#### Query Parameters
- **api_key** (str) - Optional - The API key to use for the OpenAI client. If not provided, the default API key will be used.
- **base_url** (str) - Optional - The base URL to use for the OpenAI client. If not provided, the default base URL will be used.
- **organization** (str) - Optional - The organization to use for the OpenAI client.
- **project** (str) - Optional - The project to use for the OpenAI client.

#### Request Body
- **openai_client** (AsyncOpenAI) - Optional - An existing OpenAI client instance. If provided, `api_key` and `base_url` should not be set.

### Request Example
```json
{
  "openai_client": "<existing_openai_client_object>",
  "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "base_url": "https://api.openai.com/v1",
  "organization": "org-xxxxxxxx",
  "project": "proj-xxxxxxxx"
}
```

### Response
#### Success Response (200)
- **message** (str) - Confirmation message indicating successful initialization.

#### Response Example
```json
{
  "message": "OpenAI voice model provider initialized successfully."
}
```
```

--------------------------------

### Agent Specific Start Callback in Python

Source: https://openai.github.io/openai-agents-python/ko/ref/lifecycle

The `on_start` asynchronous method in `AgentHooksBase` is called before an agent is invoked. This hook is specific to the agent instance and is triggered each time the running agent is changed to this particular agent.

```python
async def on_start(context: AgentHookContext[TContext], agent: TAgent) -> None:
    pass
```

--------------------------------

### Get All Turn Usage Details (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/memory/advanced_sqlite_session

Retrieves a list of detailed usage statistics for all turns within a session and branch, ordered by turn number. Each entry includes token counts and detailed JSON breakdowns for input and output tokens. Requires a database connection and session/branch identifiers.

```python
else:
                query = """
                    SELECT user_turn_number, requests, input_tokens, output_tokens,
                           total_tokens, input_tokens_details, output_tokens_details
                    FROM turn_usage
                    WHERE session_id = ? AND branch_id = ?
                    ORDER BY user_turn_number
                """

                with closing(conn.cursor()) as cursor:
                    cursor.execute(query, (self.session_id, branch_id))
```

--------------------------------

### Convert Tools and Handoffs in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/models/openai_responses

Converts a list of tools and handoffs into a format suitable for the OpenAI API. It enforces a limit of one computer tool and processes each tool and handoff individually, returning converted tools and associated includes.

```python
class Converter:
    @classmethod
    def convert_tools(
        cls,
        tools: list[Tool],
        handoffs: list[Handoff[Any, Any]],
    ) -> ConvertedTools:
        converted_tools: list[ToolParam] = []
        includes: list[ResponseIncludable] = []

        computer_tools = [tool for tool in tools if isinstance(tool, ComputerTool)]
        if len(computer_tools) > 1:
            raise UserError(f"You can only provide one computer tool. Got {len(computer_tools)}")

        for tool in tools:
            converted_tool, include = cls._convert_tool(tool)
            converted_tools.append(converted_tool)
            if include:
                includes.append(include)

        for handoff in handoffs:
            converted_tools.append(cls._convert_handoff_tool(handoff))

        return ConvertedTools(tools=converted_tools, includes=includes)
```

--------------------------------

### Initialize OpenAI Voice Model Provider (Python)

Source: https://openai.github.io/openai-agents-python/ref/voice/models/openai_model_provider

Initializes the OpenAI voice model provider. It accepts an API key, base URL, an optional pre-configured OpenAI client, organization, and project. If an OpenAI client is provided, API key and base URL should not be specified.

```python
def __init__(
    self,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    openai_client: AsyncOpenAI | None = None,
    organization: str | None = None,
    project: str | None = None,
) -> None:
    """Create a new OpenAI voice model provider.

    Args:
        api_key: The API key to use for the OpenAI client. If not provided, we will use the
            default API key.
        base_url: The base URL to use for the OpenAI client. If not provided, we will use the
            default base URL.
        openai_client: An optional OpenAI client to use. If not provided, we will create a new
            OpenAI client using the api_key and base_url.
        organization: The organization to use for the OpenAI client.
        project: The project to use for the OpenAI client.
    """
    if openai_client is not None:
        assert api_key is None and base_url is None,
            ("Don't provide api_key or base_url if you provide openai_client")
        self._client: AsyncOpenAI | None = openai_client
    else:
        self._client = None
        self._stored_api_key = api_key
        self._stored_base_url = base_url
        self._stored_organization = organization
        self._stored_project = project

```

--------------------------------

### Get Conversation Turns API

Source: https://openai.github.io/openai-agents-python/ko/ref/extensions/memory/advanced_sqlite_session

Retrieves user message turns from a specified branch for analysis and branching decisions. It provides a summary and full content of user messages along with timestamps.

```APIDOC
## GET /conversations/turns

### Description
Retrieves a list of user conversation turns from a specific branch. Each turn includes its number, truncated content, full content, creation timestamp, and a flag indicating if branching is possible.

### Method
GET

### Endpoint
/conversations/turns

### Parameters
#### Query Parameters
- **branch_id** (string) - Optional - The ID of the branch to retrieve turns from. If not provided, the current branch is used.

### Response
#### Success Response (200)
- **turns** (list[dict]) - A list of dictionaries, where each dictionary represents a conversation turn and contains the following keys:
  - **turn** (integer): The turn number within the branch.
  - **content** (string): A truncated version of the user's message content.
  - **full_content** (string): The complete user message content.
  - **timestamp** (string): The date and time when the turn was created.
  - **can_branch** (boolean): Indicates if the turn can be used for branching (always true for user messages).

#### Response Example
```json
{
  "turns": [
    {
      "turn": 1,
      "content": "Hello, how can I help you today?",
      "full_content": "Hello, how can I help you today?",
      "timestamp": "2023-10-27T10:00:00Z",
      "can_branch": true
    },
    {
      "turn": 2,
      "content": "I need assistance with my account.",
      "full_content": "I need assistance with my account.",
      "timestamp": "2023-10-27T10:05:00Z",
      "can_branch": true
    }
  ]
}
```
```

--------------------------------

### Implement Custom Tool Output Handler

Source: https://openai.github.io/openai-agents-python/agents

This example demonstrates how to create a custom function to process tool results. The function determines if the output is final or if the LLM should continue processing, providing fine-grained control over tool use behavior.

```python
from agents import Agent, Runner, function_tool, FunctionToolResult, RunContextWrapper
from agents.agent import ToolsToFinalOutputResult
from typing import List, Any

@function_tool
def get_weather(city: str) -> str:
    """Returns weather info for the specified city."""
    return f"The weather in {city} is sunny"

def custom_tool_handler(
    context: RunContextWrapper[Any],
    tool_results: List[FunctionToolResult]
) -> ToolsToFinalOutputResult:
    """Processes tool results to decide final output."""
    for result in tool_results:
        if result.output and "sunny" in result.output:
            return ToolsToFinalOutputResult(
                is_final_output=True,
                final_output=f"Final weather: {result.output}"
            )
    return ToolsToFinalOutputResult(
        is_final_output=False,
        final_output=None
    )

agent = Agent(
    name="Weather Agent",
    instructions="Retrieve weather details.",
    tools=[get_weather],
    tool_use_behavior=custom_tool_handler
)

```

--------------------------------

### Tracing Configuration in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/run

Configuration object for tracing behavior during an agent run. This allows for detailed setup of how traces are generated and managed. This attribute is a class attribute and an instance attribute.

```python
tracing: TracingConfig | None = None

```

--------------------------------

### Dynamic Agent Instructions (Python)

Source: https://openai.github.io/openai-agents-python/agents

Shows how to provide dynamic instructions to an agent using a function. This function receives the agent and context, allowing for context-aware prompt generation, such as including the user's name in the instructions.

```python
from agents import Agent, RunContextWrapper, UserContext

def dynamic_instructions(
    context: RunContextWrapper[UserContext], agent: Agent[UserContext]
) -> str:
    return f"The user's name is {context.context.name}. Help them with their questions."


agent = Agent[UserContext](
    name="Triage agent",
    instructions=dynamic_instructions,
)

```

--------------------------------

### Agent Configuration with Specific Output Type

Source: https://openai.github.io/openai-agents-python/agents

Explains how to configure an agent to produce structured outputs instead of plain text using the `output_type` parameter. This example uses a Pydantic `BaseModel` to define the structure of a `CalendarEvent`.

```python
from pydantic import BaseModel
from agents import Agent


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

agent = Agent(
    name="Calendar extractor",
    instructions="Extract calendar events from text",
    output_type=CalendarEvent,
)
```

--------------------------------

### Get Agent Prompt - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/agent

An asynchronous method `get_prompt` that retrieves the prompt for an agent. It utilizes `PromptUtil.to_model_input` to format the prompt based on the provided `RunContextWrapper`. This function is part of the agent's interface for interacting with the language model.

```python
async def get_prompt(
    self, run_context: RunContextWrapper[TContext]
) -> ResponsePromptParam | None:
    """Get the prompt for the agent."""
    return await PromptUtil.to_model_input(self.prompt, run_context, self)
```

--------------------------------

### ComputerProvider

Source: https://openai.github.io/openai-agents-python/ref/tool

Configures create/dispose hooks for per-run computer lifecycle management.

```APIDOC
## ComputerProvider

### Description
Configures create/dispose hooks for per-run computer lifecycle management.

### Parameters
#### Request Body
- **create** (ComputerCreate[ComputerT]) - Required - The function to create a computer.
- **dispose** (ComputerDispose[ComputerT] | None) - Optional - The function to dispose a computer.

### Request Example
```python
from typing import Any, TypeVar
from agents.tool import ComputerCreate, ComputerDispose, ComputerProvider

ComputerT = TypeVar("ComputerT")

class MyComputer:
    pass

async def create_my_computer(run_context: Any) -> MyComputer:
    return MyComputer()

def dispose_my_computer(run_context: Any, computer: MyComputer) -> None:
    print("Disposing computer")

computer_provider = ComputerProvider(
    create=create_my_computer,
    dispose=dispose_my_computer
)
```

### Response
#### Success Response (200)
- **create** (ComputerCreate[ComputerT]) - The function to create a computer.
- **dispose** (ComputerDispose[ComputerT] | None) - The function to dispose a computer.

#### Response Example
```json
{
  "create": "<function create_my_computer at 0x...>",
  "dispose": "<function dispose_my_computer at 0x...>"
}
```
```

--------------------------------

### Convert LiteLLM Annotations to OpenAI Format

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/litellm

Converts annotations from a LiteLLM message to the OpenAI format. This method specifically handles URL citations, extracting start index, end index, URL, and title. It returns a list of OpenAI-compatible annotations or None if no annotations are present.

```python
class LitellmConverter:
    @classmethod
    def convert_annotations_to_openai(
        cls, message: litellm.types.utils.Message
    ) -> list[Annotation] | None:
        annotations: list[litellm.types.llms.openai.ChatCompletionAnnotation] | None = message.get(
            "annotations", None
        )
        if not annotations:
            return None

        return [
            Annotation(
                type="url_citation",
                url_citation=AnnotationURLCitation(
                    start_index=annotation["url_citation"]["start_index"],
                    end_index=annotation["url_citation"]["end_index"],
                    url=annotation["url_citation"]["url"],
                    title=annotation["url_citation"]["title"],
                ),
            )
            for annotation in annotations
        ]
```

--------------------------------

### Get AsyncOpenAI Client (Python)

Source: https://openai.github.io/openai-agents-python/ref/models/openai_chatcompletions

This method provides an asynchronous client for the OpenAI API. It ensures that a single client instance is reused across calls to maintain efficiency and connection pooling.

```python
def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI()
        return self._client
```

--------------------------------

### Tracer Initialization

Source: https://openai.github.io/openai-agents-python/ref/tracing/processors

Initializes the tracer with API key, organization, project, endpoint, and retry configurations.

```APIDOC
## POST /v1/traces/ingest

### Description
Initializes the tracer with API key, organization, project, endpoint, and retry configurations. This is the primary method for setting up the tracing client.

### Method
POST

### Endpoint
/v1/traces/ingest

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **api_key** (str | None) - Optional - The API key for the "Authorization" header. Defaults to `os.environ["OPENAI_API_KEY"]` if not provided.
- **organization** (str | None) - Optional - The OpenAI organization to use. Defaults to `os.environ["OPENAI_ORG_ID"]` if not provided.
- **project** (str | None) - Optional - The OpenAI project to use. Defaults to `os.environ["OPENAI_PROJECT_ID"]` if not provided.
- **endpoint** (str) - Optional - The HTTP endpoint to which traces/spans are posted. Defaults to `'https://api.openai.com/v1/traces/ingest'`.
- **max_retries** (int) - Optional - Maximum number of retries upon failures. Defaults to `3`.
- **base_delay** (float) - Optional - Base delay (in seconds) for the first backoff. Defaults to `1.0`.
- **max_delay** (float) - Optional - Maximum delay (in seconds) for backoff growth. Defaults to `30.0`.

### Request Example
```json
{
  "api_key": "sk-your_api_key",
  "organization": "org-your_organization",
  "project": "proj-your_project",
  "endpoint": "https://api.openai.com/v1/traces/ingest",
  "max_retries": 5,
  "base_delay": 2.0,
  "max_delay": 60.0
}
```

### Response
#### Success Response (200)
This method does not return a specific success response body, but initializes the tracer.

#### Response Example
None
```

--------------------------------

### Get Conversation Turns (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/memory/advanced_sqlite_session

Retrieves user turns and their content from a specified branch or the current branch. It fetches data from 'message_structure' and 'agent_messages' tables, returning a list of dictionaries with turn details.

```python
async def get_conversation_turns(self, branch_id: str | None = None) -> list[dict[str, Any]]:
    """Get user turns with content for easy browsing and branching decisions.

    Args:
        branch_id: Branch to get turns from (current branch if None).

    Returns:
        List of dicts with turn info containing:
            - 'turn': Branch turn number
            - 'content': User message content (truncated)
            - 'full_content': Full user message content
            - 'timestamp': When the turn was created
            - 'can_branch': Always True (all user messages can branch)
    """
    if branch_id is None:
        branch_id = self._current_branch_id

    def _get_turns_sync():
        """Synchronous helper to get conversation turns."""
        conn = self._get_connection()
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    ms.branch_turn_number,
                    am.message_data,
                    ms.created_at
                FROM message_structure ms
                JOIN agent_messages am ON ms.message_id = am.id
                WHERE ms.session_id = ? AND ms.branch_id = ?
                AND ms.message_type = 'user'
                ORDER BY ms.branch_turn_number
            """,
                (self.session_id, branch_id),
            )

            turns = []
            for row in cursor.fetchall():
                turn_num, message_data, created_at = row
                try:
                    content = json.loads(message_data).get("content", "")
                    turns.append(
                        {
                            "turn": turn_num,
                            "content": content[:100] + "..." if len(content) > 100 else content,
                            "full_content": content,
                            "timestamp": created_at,
                            "can_branch": True,
                        }
                    )
                except (json.JSONDecodeError, AttributeError):
                    continue

            return turns

    return await asyncio.to_thread(_get_turns_sync)
```

--------------------------------

### Get All Mappings from MultiProviderMap (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/models/multi_provider

Implements the `get_mapping` method for the MultiProviderMap class. This method returns a shallow copy of the internal dictionary that stores the prefix to ModelProvider mappings. It takes no arguments and returns a dictionary.

```python
def get_mapping(self) -> dict[str, ModelProvider]:
    """Returns a copy of the current prefix -> ModelProvider mapping."""
    return self._mapping.copy()

```

--------------------------------

### Get Response Format Configuration in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/models/openai_responses

Determines the response format configuration based on an agent's output schema. It returns a JSON schema configuration if the schema is not plain text, otherwise it returns an 'omit' value.

```python
class Converter:
    @classmethod
    def get_response_format(
        cls,
        output_schema: AgentOutputSchemaBase | None
    ) -> ResponseTextConfigParam | Omit:
        if output_schema is None or output_schema.is_plain_text():
            return omit
        else:
            return {
                "format": {
                    "type": "json_schema",
                    "name": "final_output",
                    "schema": output_schema.json_schema(),
                    "strict": output_schema.is_strict_json_schema(),
                }
            }
```

--------------------------------

### Agent Span Creation

Source: https://openai.github.io/openai-agents-python/ref/tracing/create

This section details the `agent_span` function used for creating new agent spans. Spans are not started automatically and require manual start/finish calls or usage within a `with` statement.

```APIDOC
## POST /agent_span

### Description
Creates a new agent span. The span needs to be explicitly started and finished, or used within a context manager.

### Method
POST

### Endpoint
/agent_span

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **name** (str) - Required - The name of the agent.
- **handoffs** (list[str] | None) - Optional - A list of agent names to which this agent could hand off control.
- **tools** (list[str] | None) - Optional - A list of tool names available to this agent.
- **output_type** (str | None) - Optional - The name of the output type produced by the agent.
- **span_id** (str | None) - Optional - The ID of the span. If not provided, an ID will be generated.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, the current trace/span is used.
- **disabled** (bool) - Optional - If True, the span will not be recorded. Defaults to False.

### Request Example
```json
{
  "name": "MyAgent",
  "handoffs": ["ResponderAgent"],
  "tools": ["SearchTool"],
  "output_type": "TextResponse",
  "span_id": "generated-or-provided-id",
  "parent": null,
  "disabled": false
}
```

### Response
#### Success Response (200)
- **Span[AgentSpanData]** - The newly created agent span object.
```

--------------------------------

### Run Async Realtime Session in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/runner

Starts and returns a realtime session for bidirectional communication with a realtime model. This method is asynchronous and requires an `async with` block for proper session management. It takes optional context and model configuration as input.

```python
async def run(
    self, *, context: TContext | None = None, model_config: RealtimeModelConfig | None = None
) -> RealtimeSession:
    """Start and returns a realtime session.

    Returns:
        RealtimeSession: A session object that allows bidirectional communication with the
        realtime model.

    Example:
        ```python
        runner = RealtimeRunner(agent)
        async with await runner.run() as session:
            await session.send_message("Hello")
            async for event in session:
                print(event)
        ```
    """
    # Create and return the connection
    session = RealtimeSession(
        model=self._model,
        agent=self._starting_agent,
        context=context,
        model_config=model_config,
        run_config=self._config,
    )

    return session

```

--------------------------------

### Prepare and Send LLM Request with OpenAI Python SDK

Source: https://openai.github.io/openai-agents-python/ja/ref/models/openai_responses

This snippet demonstrates how to prepare and send a request to the OpenAI LLM API using the Python SDK. It handles various parameters such as model settings, tools, streaming, and response formatting. It also includes conditional logging for debugging purposes.

```python
if model_settings.top_logprobs is not None:
            include_set.add("message.output_text.logprobs")
        include = cast(list[ResponseIncludable], list(include_set))

        if _debug.DONT_LOG_MODEL_DATA:
            logger.debug("Calling LLM")
        else:
            input_json = json.dumps(
                list_input,
                indent=2,
                ensure_ascii=False,
            )
            tools_json = json.dumps(
                converted_tools_payload,
                indent=2,
                ensure_ascii=False,
            )
            logger.debug(
                f"Calling LLM {self.model} with input:\n"
                f"{input_json}\n"
                f"Tools:\n{tools_json}\n"
                f"Stream: {stream}\n"
                f"Tool choice: {tool_choice}\n"
                f"Response format: {response_format}\n"
                f"Previous response id: {previous_response_id}\n"
                f"Conversation id: {conversation_id}\n"
            )

        extra_args = dict(model_settings.extra_args or {})
        if model_settings.top_logprobs is not None:
            extra_args["top_logprobs"] = model_settings.top_logprobs
        if model_settings.verbosity is not None:
            if response_format is not omit:
                response_format["verbosity"] = model_settings.verbosity  # type: ignore [index]
            else:
                response_format = {"verbosity": model_settings.verbosity}

        stream_param: Literal[True] | Omit = True if stream else omit

        response = await self._client.responses.create(
            previous_response_id=self._non_null_or_omit(previous_response_id),
            conversation=self._non_null_or_omit(conversation_id),
            instructions=self._non_null_or_omit(system_instructions),
            model=model_param,
            input=list_input,
            include=include,
            tools=tools_param,
            prompt=self._non_null_or_omit(prompt),
            temperature=self._non_null_or_omit(model_settings.temperature),
            top_p=self._non_null_or_omit(model_settings.top_p),
            truncation=self._non_null_or_omit(model_settings.truncation),
            max_output_tokens=self._non_null_or_omit(model_settings.max_tokens),
            tool_choice=tool_choice,
            parallel_tool_calls=parallel_tool_calls,
            stream=cast(Any, stream_param),
            extra_headers=self._merge_headers(model_settings),
            extra_query=model_settings.extra_query,
            extra_body=model_settings.extra_body,
            text=response_format,
            store=self._non_null_or_omit(model_settings.store),
            prompt_cache_retention=self._non_null_or_omit(model_settings.prompt_cache_retention),
            reasoning=self._non_null_or_omit(model_settings.reasoning),
            metadata=self._non_null_or_omit(model_settings.metadata),
            **extra_args,
        )
        return cast(Union[Response, AsyncStream[ResponseStreamEvent]], response)
```

--------------------------------

### generation_span API

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing/create

Creates a new generation span to capture model generation details. The span is not started automatically and requires manual start/finish or usage within a 'with' statement.

```APIDOC
## generation_span

### Description
Create a new generation span. The span will not be started automatically, you should either do `with generation_span() ...` or call `span.start()` + `span.finish()` manually.

This span captures the details of a model generation, including the input message sequence, any generated outputs, the model name and configuration, and usage data. If you only need to capture a model response identifier, use `response_span()` instead.

### Method
(Function Signature - Not an HTTP Method)

### Endpoint
(N/A - Python Function)

### Parameters
#### Path Parameters
(None)

#### Query Parameters
(None)

#### Request Body
(N/A - Python Function Parameters)
- **input** (`Sequence[Mapping[str, Any]] | None`) - Optional - The sequence of input messages sent to the model.
- **output** (`Sequence[Mapping[str, Any]] | None`) - Optional - The sequence of output messages received from the model.
- **model** (`str | None`) - Optional - The model identifier used for the generation.
- **model_config** (`Mapping[str, Any] | None`) - Optional - The model configuration (hyperparameters) used.
- **usage** (`dict[str, Any] | None`) - Optional - A dictionary of usage information (input tokens, output tokens, etc.).
- **span_id** (`str | None`) - Optional - The ID of the span. Optional. If not provided, we will generate an ID. We recommend using `util.gen_span_id()` to generate a span ID, to guarantee that IDs are correctly formatted.
- **parent** (`Trace | Span[Any] | None`) - Optional - The parent span or trace. If not provided, we will automatically use the current trace/span as the parent.
- **disabled** (`bool`) - Optional - If True, we will return a Span but the Span will not be recorded. Default: `False`

### Request Example
```python
# Using a 'with' statement
with generation_span(model="gpt-4") as span:
    # Perform model generation here
    pass

# Manual start and finish
span = generation_span(model="gpt-4")
span.start()
# Perform model generation here
span.finish()
```

### Response
#### Success Response (200)
- **Span[GenerationSpanData]** - The newly created generation span.
```

--------------------------------

### Python Session Management: Ensure Compaction Candidates

Source: https://openai.github.io/openai-agents-python/ref/memory/openai_responses_compaction_session

Implements lazy loading and caching for session compaction candidates. It retrieves history, selects candidates, and caches them for future use, logging the initialization details.

```python
async def _ensure_compaction_candidates(
        self,
    ) -> tuple[list[TResponseInputItem], list[TResponseInputItem]]:
        """Lazy-load and cache compaction candidates."""
        if self._compaction_candidate_items is not None and self._session_items is not None:
            return (self._compaction_candidate_items[:], self._session_items[:])

        history = await self.underlying_session.get_items()
        candidates = select_compaction_candidate_items(history)
        self._compaction_candidate_items = candidates
        self._session_items = history

        logger.debug(
            f"candidates: initialized (history={len(history)}, candidates={len(candidates)})"
        )
        return (candidates[:], history[:])
```

--------------------------------

### Transcription Span API

Source: https://openai.github.io/openai-agents-python/ref/tracing/create

This endpoint allows for the creation of a new transcription span for speech-to-text processing. The span needs to be explicitly started and finished or used within a `with` statement.

```APIDOC
## POST /v1/transcription_span

### Description
Creates a new transcription span for speech-to-text. The span is not started automatically; manual start/finish or `with` statement usage is required.

### Method
POST

### Endpoint
/v1/transcription_span

### Parameters
#### Query Parameters
- **model** (str | None) - Optional - The name of the model used for the speech-to-text.
- **input** (str | None) - Optional - The audio input of the speech-to-text transcription, as a base64 encoded string of audio bytes.
- **input_format** (str | None) - Optional - The format of the audio input. Defaults to "pcm".
- **output** (str | None) - Optional - The output of the speech-to-text transcription.
- **model_config** (Mapping[str, Any] | None) - Optional - The model configuration (hyperparameters) used.
- **span_id** (str | None) - Optional - The ID of the span. If not provided, an ID will be generated.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, the current trace/span is used.
- **disabled** (bool) - Optional - If True, the Span will not be recorded. Defaults to False.

### Request Example
```json
{
  "model": "whisper-1",
  "input": "BASE64_ENCODED_AUDIO_BYTES",
  "input_format": "mp3",
  "model_config": {
    "temperature": 0.7
  }
}
```

### Response
#### Success Response (200)
- **span** (Span[TranscriptionSpanData]) - The newly created speech-to-text span.
```

--------------------------------

### Fetch MCP Tools - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/agent

Asynchronously fetches available tools from MCP servers. It utilizes `MCPUtil.get_all_function_tools` and accepts a `RunContextWrapper` for context. The function returns a list of `Tool` objects.

```python
async def get_mcp_tools(self, run_context: RunContextWrapper[TContext]) -> list[Tool]:
    """Fetches the available tools from the MCP servers."""
    convert_schemas_to_strict = self.mcp_config.get("convert_schemas_to_strict", False)
    return await MCPUtil.get_all_function_tools(
        self.mcp_servers, convert_schemas_to_strict, run_context, self
    )
```

--------------------------------

### SingleAgentVoiceWorkflow on_start method in Python

Source: https://openai.github.io/openai-agents-python/zh/ref/voice/workflow

Implements the optional `on_start` asynchronous method for `SingleAgentVoiceWorkflow`. This method is intended to be executed before any user input is received, potentially for delivering greetings or instructions via text-to-speech. The default behavior is to do nothing.

```python
async def on_start(self) -> AsyncIterator[str]:
    """
    Optional method that runs before any user input is received. Can be used
    to deliver a greeting or instruction via TTS. Defaults to doing nothing.
    """
    return
    yield
```

--------------------------------

### Initialize AsyncOpenAI Client in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/models/openai_responses

This Python snippet shows how to lazily initialize an asynchronous OpenAI client. It checks if the client instance already exists and creates a new `AsyncOpenAI` object if it's `None`.

```python
def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI()
        return self._client
```

--------------------------------

### Get Metadata for State Operations with TTL

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/memory/dapr_session

Retrieves metadata for state operations, including the TTL (Time To Live) in seconds if it's configured. Returns an empty dictionary if TTL is not set.

```python
def _get_metadata(self) -> dict[str, str]:
        """Get metadata for state operations including TTL if configured."""
        metadata = {}
        if self._ttl is not None:
            metadata["ttlInSeconds"] = str(self._ttl)
        return metadata
```

--------------------------------

### Get Current Trace in Python

Source: https://openai.github.io/openai-agents-python/ref/tracing/create

Retrieves the currently active trace, if one exists. This is useful for inspecting or modifying the active trace within the current execution context.

```python
def get_current_trace() -> Trace | None:
    """Returns the currently active trace, if present."""
    return get_trace_provider().get_current_trace()
```

--------------------------------

### OpenAITTSModel Initialization (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/models/openai_tts

Constructor for the OpenAITTSModel. It takes the model name and an asynchronous OpenAI client instance as required arguments to set up the text-to-speech functionality.

```python
def __init__(
    self,
    model: str,
    openai_client: AsyncOpenAI,
):
    """Create a new OpenAI text-to-speech model.

    Args:
        model: The name of the model to use.
        openai_client: The OpenAI client to use.
    """
    self.model = model
    self._client = openai_client

```

--------------------------------

### SQLAlchemySession: Get Items

Source: https://openai.github.io/openai-agents-python/ref/extensions/memory/sqlalchemy_session

Retrieves conversation history items from the database for a given session. It supports retrieving all items or a specified number of the latest items, ordered chronologically.

```python
async def get_items(self, limit: int | None = None) -> list[TResponseInputItem]:
    """Retrieve the conversation history for this session.

    Args:
        limit: Maximum number of items to retrieve. If None, retrieves all items.
               When specified, returns the latest N items in chronological order.

    Returns:
        List of input items representing the conversation history
    """
    await self._ensure_tables()
    async with self._session_factory() as sess:
        if limit is None:
            stmt = (
                select(self._messages.c.message_data)
                .where(self._messages.c.session_id == self.session_id)
                .order_by(
                    self._messages.c.created_at.asc(),
                    self._messages.c.id.asc(),
                )
            )
        else:
            stmt = (
                select(self._messages.c.message_data)
                .where(self._messages.c.session_id == self.session_id)
                # Use DESC + LIMIT to get the latest N
                # then reverse later for chronological order.
                .order_by(
                    self._messages.c.created_at.desc(),
                    self._messages.c.id.desc(),
                )
                .limit(limit)
            )

        result = await sess.execute(stmt)
        rows: list[str] = [row[0] for row in result.all()]

        if limit is not None:
            rows.reverse()

        items: list[TResponseInputItem] = []
        for raw in rows:
            try:
                items.append(await self._deserialize_item(raw))
            except json.JSONDecodeError:
                # Skip corrupted rows
                continue
        return items
```

--------------------------------

### Initialize MCPServerStdio with Stdio Transport Parameters

Source: https://openai.github.io/openai-agents-python/ja/ref/mcp/server

Initializes the MCPServerStdio class, which acts as an MCP server using stdio for communication. It takes various parameters to configure the server, including command, arguments, environment variables, working directory, text encoding, and session timeouts. Dependencies include `_MCPServerWithClientSession` and `StdioServerParameters`.

```python
class MCPServerStdio(_MCPServerWithClientSession):
    """MCP server implementation that uses the stdio transport. See the [spec]
    (https://spec.modelcontextprotocol.io/specification/2024-11-05/basic/transports/#stdio) for
    details.
    """

    def __init__(
        self,
        params: MCPServerStdioParams,
        cache_tools_list: bool = False,
        name: str | None = None,
        client_session_timeout_seconds: float | None = 5,
        tool_filter: ToolFilter = None,
        use_structured_content: bool = False,
        max_retry_attempts: int = 0,
        retry_backoff_seconds_base: float = 1.0,
        message_handler: MessageHandlerFnT | None = None,
    ):
        """Create a new MCP server based on the stdio transport.

        Args:
            params: The params that configure the server. This includes the command to run to
                start the server, the args to pass to the command, the environment variables to
                set for the server, the working directory to use when spawning the process, and
                the text encoding used when sending/receiving messages to the server.
            cache_tools_list: Whether to cache the tools list. If `True`, the tools list will be
                cached and only fetched from the server once. If `False`, the tools list will be
                fetched from the server on each call to `list_tools()`. The cache can be
                invalidated by calling `invalidate_tools_cache()`. You should set this to `True`
                if you know the server will not change its tools list, because it can drastically
                improve latency (by avoiding a round-trip to the server every time).
            name: A readable name for the server. If not provided, we'll create one from the
                command.
            client_session_timeout_seconds: the read timeout passed to the MCP ClientSession.
            tool_filter: The tool filter to use for filtering tools.
            use_structured_content: Whether to use `tool_result.structured_content` when calling an
                MCP tool. Defaults to False for backwards compatibility - most MCP servers still
                include the structured content in the `tool_result.content`, and using it by
                default will cause duplicate content. You can set this to True if you know the
                server will not duplicate the structured content in the `tool_result.content`.
            max_retry_attempts: Number of times to retry failed list_tools/call_tool calls.
                Defaults to no retries.
            retry_backoff_seconds_base: The base delay, in seconds, for exponential
                backoff between retries.
            message_handler: Optional handler invoked for session messages as delivered by the
                ClientSession.
        """
        super().__init__(
            cache_tools_list,
            client_session_timeout_seconds,
            tool_filter,
            use_structured_content,
            max_retry_attempts,
            retry_backoff_seconds_base,
            message_handler=message_handler,
        )

        self.params = StdioServerParameters(
            command=params["command"],
            args=params.get("args", []),
            env=params.get("env"),
            cwd=params.get("cwd"),
            encoding=params.get("encoding", "utf-8"),
            encoding_error_handler=params.get("encoding_error_handler", "strict"),
        )

        self._name = name or f"stdio: {self.params.command}"
```

--------------------------------

### Get Function Tools from a Single MCP Server (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/mcp/util

Fetches all function tools from a single MCP server. It uses an MCP span for tracing and converts the raw MCP tools into Agents SDK Tool objects. Dependencies include MCPServer, RunContextWrapper, AgentBase, Tool, and mcp_tools_span.

```python
class MCPUtil:
    """Set of utilities for interop between MCP and Agents SDK tools."""

    @classmethod
    async def get_function_tools(
        cls,
        server: "MCPServer",
        convert_schemas_to_strict: bool,
        run_context: RunContextWrapper[Any],
        agent: "AgentBase",
    ) -> list[Tool]:
        """Get all function tools from a single MCP server."""

        with mcp_tools_span(server=server.name) as span:
            tools = await server.list_tools(run_context, agent)
            span.span_data.result = [tool.name for tool in tools]

        return [cls.to_function_tool(tool, server, convert_schemas_to_strict) for tool in tools]
```

--------------------------------

### Get Deferred Compaction Response ID

Source: https://openai.github.io/openai-agents-python/ko/ref/memory/openai_responses_compaction_session

Retrieves the response ID that has been deferred for compaction. If no compaction is currently deferred, it returns None. This is a helper function to check the status of deferred compaction.

```python
def _get_deferred_compaction_response_id(self) -> str | None:
        return self._deferred_response_id
```

--------------------------------

### Get Trace Provider with Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing

Retrieves the globally configured trace provider. This function is essential for accessing the active tracing mechanism. It raises a RuntimeError if the trace provider has not been set.

```python
def get_trace_provider() -> TraceProvider:
    """Get the global trace provider used by tracing utilities."""
    if GLOBAL_TRACE_PROVIDER is None:
        raise RuntimeError("Trace provider not set")
    return GLOBAL_TRACE_PROVIDER

```

--------------------------------

### Agent Span Creation API

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing

This API allows for the creation of new agent spans, which are used for tracing agent activities. Spans are not started automatically and require manual start/finish calls or usage within a `with` statement.

```APIDOC
## POST /agent_span

### Description
Creates a new agent span for tracing purposes. The span needs to be manually started and finished, or used with a context manager.

### Method
POST

### Endpoint
/agent_span

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **name** (str) - Required - The name of the agent.
- **handoffs** (list[str] | None) - Optional - A list of agent names to which this agent could hand off control. Defaults to None.
- **tools** (list[str] | None) - Optional - A list of tool names available to this agent. Defaults to None.
- **output_type** (str | None) - Optional - The name of the output type produced by the agent. Defaults to None.
- **span_id** (str | None) - Optional - The ID of the span. If not provided, an ID will be generated. Defaults to None.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. If not provided, the current trace/span is used. Defaults to None.
- **disabled** (bool) - Optional - If True, the span will not be recorded. Defaults to False.

### Request Example
```json
{
  "name": "MyAgent",
  "handoffs": ["OtherAgent"],
  "tools": ["Tool1"],
  "output_type": "response",
  "span_id": "generated-span-id",
  "parent": null,
  "disabled": false
}
```

### Response
#### Success Response (200)
- **Span[AgentSpanData]** - The newly created agent span.

#### Response Example
```json
{
  "span_id": "generated-span-id",
  "name": "MyAgent",
  "data": {
    "handoffs": ["OtherAgent"],
    "tools": ["Tool1"],
    "output_type": "response"
  },
  "start_time": "2023-10-27T10:00:00Z",
  "end_time": null
}
```
```

--------------------------------

### Retrieve Conversation History Markers

Source: https://openai.github.io/openai-agents-python/ja/ref/handoffs

The `get_conversation_history_wrappers` function returns the current start and end markers used for summarizing nested conversations. These markers define the boundaries for extracting and processing conversation history.

```python
def get_conversation_history_wrappers() -> tuple[str, str]:
    """Return the current start/end markers used for the nested conversation summary."""

    return (_conversation_history_start, _conversation_history_end)
```

--------------------------------

### Validate Agent Initialization Parameters in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/agent

This code snippet demonstrates the validation logic within an agent's initialization process. It checks for correct types and formats of various parameters, including model settings, input/output guardrails, output type, hooks, tool use behavior, and reset tool choice. Type errors are raised if the parameters do not meet the expected criteria.

```python
if (
                    isinstance(self.model, str) is False
                    or gpt_5_reasoning_settings_required(self.model) is False  # type: ignore
                )
                # The model settings are not customized for the specified model
                and self.model_settings == get_default_model_settings():
            # In this scenario, we should use a generic model settings
            # because non-gpt-5 models are not compatible with the default gpt-5 model settings.
            # This is a best-effort attempt to make the agent work with non-gpt-5 models.
            self.model_settings = ModelSettings()

        if not isinstance(self.input_guardrails, list):
            raise TypeError(
                f"Agent input_guardrails must be a list, got {type(self.input_guardrails).__name__}"
            )

        if not isinstance(self.output_guardrails, list):
            raise TypeError(
                f"Agent output_guardrails must be a list, "
                f"got {type(self.output_guardrails).__name__}"
            )

        if self.output_type is not None:
            from .agent_output import AgentOutputSchemaBase

            if not (
                isinstance(self.output_type, (type, AgentOutputSchemaBase))
                or get_origin(self.output_type) is not None
            ):
                raise TypeError(
                    f"Agent output_type must be a type, AgentOutputSchemaBase, or None, "
                    f"got {type(self.output_type).__name__}"
                )

        if self.hooks is not None:
            from .lifecycle import AgentHooksBase

            if not isinstance(self.hooks, AgentHooksBase):
                raise TypeError(
                    f"Agent hooks must be an AgentHooks instance or None, "
                    f"got {type(self.hooks).__name__}"
                )

        if (
            not (
                isinstance(self.tool_use_behavior, str)
                and self.tool_use_behavior in ["run_llm_again", "stop_on_first_tool"]
            )
            and not isinstance(self.tool_use_behavior, dict)
            and not callable(self.tool_use_behavior)
        ):
            raise TypeError(
                f"Agent tool_use_behavior must be 'run_llm_again', 'stop_on_first_tool', "
                f"StopAtTools dict, or callable, got {type(self.tool_use_behavior).__name__}"
            )

        if not isinstance(self.reset_tool_choice, bool):
            raise TypeError(
                f"Agent reset_tool_choice must be a boolean, "
                f"got {type(self.reset_tool_choice).__name__}"
            )
```

--------------------------------

### Initialize SQLAlchemySession from URL in OpenAI Agents Python

Source: https://openai.github.io/openai-agents-python/sessions

Demonstrates creating a production-ready SQLAlchemySession using a database URL. This method allows connection to various SQLAlchemy-supported databases and optionally creates necessary tables.

```python
from agents.extensions.memory import SQLAlchemySession

# Using database URL
session = SQLAlchemySession.from_url(
    "user_123",
    url="postgresql+asyncpg://user:pass@localhost/db",
    create_tables=True
)

```

--------------------------------

### Get Current Time in ISO 8601 Format (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/util

Returns the current time formatted as an ISO 8601 string. This function relies on the trace provider to supply the time information.

```python
def time_iso() -> str:
    """Return the current time in ISO 8601 format."""
    return get_trace_provider().time_iso()
```

--------------------------------

### Configure Available Tools for Realtime Sessions (Python)

Source: https://openai.github.io/openai-agents-python/ko/ref/realtime/config

Provides a list of tools that are available for the model to call during realtime sessions.

```python
tools: NotRequired[list[Tool]]
```

--------------------------------

### Run Agent Asynchronously with Runner.run() in Python

Source: https://openai.github.io/openai-agents-python/running_agents

Demonstrates how to run an agent asynchronously using the `Runner.run()` method. This method takes an `Agent` object and user input, returning a `RunResult` upon completion. Ensure the `agents` library is installed and imported.

```python
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")

    result = await Runner.run(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)
    # Code within the code,
    # Functions calling themselves,
    # Infinite loop's dance

```

--------------------------------

### Per-Request Usage Tracking

Source: https://openai.github.io/openai-agents-python/usage

Illustrates how to access and iterate through `request_usage_entries` to get detailed token usage for each individual API request made during a run. This is useful for granular cost analysis and understanding context window consumption per interaction.

```python
result = await Runner.run(agent, "What's the weather in Tokyo?")

for i, request in enumerate(result.context_wrapper.usage.request_usage_entries):
    print(f"Request {i + 1}: {request.input_tokens} in, {request.output_tokens} out")
```

--------------------------------

### RealtimeSession: Establish and Use Real-time Model Connection (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/session

Demonstrates how to establish a real-time session with a model using RealtimeRunner and interact with it by sending messages and audio, and then processing streamed events. This involves using an asynchronous context manager for the session.

```python
runner = RealtimeRunner(agent)
async with await runner.run() as session:
    # Send messages
    await session.send_message("Hello")
    await session.send_audio(audio_bytes)

    # Stream events
    async for event in session:
        if event.type == "audio":
            # Handle audio event
            pass

```

--------------------------------

### Configure OpenAI Realtime Session with Model Settings

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/openai_realtime

This function configures a session for the OpenAI Realtime API, processing various model settings such as audio configuration, tools, instructions, prompts, and token limits. It prepares the `session_create_request` object based on the provided `model_settings` dictionary.

```python
        audio=OpenAIRealtimeAudioConfig(
            input=OpenAIRealtimeAudioInput(**audio_input_args),
            output=OpenAIRealtimeAudioOutput(**audio_output_args),
        ),
        tools=cast(
            Any,
            self._tools_to_session_tools(
                tools=model_settings.get("tools", []),
                handoffs=model_settings.get("handoffs", []),
            ),
        ),
    )

    if "instructions" in model_settings:
        session_create_request.instructions = model_settings.get("instructions")

    if "prompt" in model_settings:
        _passed_prompt: Prompt = model_settings["prompt"]
        variables: dict[str, Any] | None = _passed_prompt.get("variables")
        session_create_request.prompt = ResponsePrompt(
            id=_passed_prompt["id"],
            variables=variables,
            version=_passed_prompt.get("version"),
        )

    if "max_output_tokens" in model_settings:
        session_create_request.max_output_tokens = cast(
            Any, model_settings.get("max_output_tokens")
        )

    if "tool_choice" in model_settings:
        session_create_request.tool_choice = cast(Any, model_settings.get("tool_choice"))

    return session_create_request
```

--------------------------------

### Get MCPServerStdio Name

Source: https://openai.github.io/openai-agents-python/zh/ref/mcp/server

Provides a readable name for the MCPServerStdio instance. This property returns the name assigned during initialization or a default name derived from the server's command.

```python
@property
def name(self) -> str:
        """A readable name for the server."""
        return self._name
```

--------------------------------

### Get Function Tools from a Single MCP Server (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/mcp/util

This class method fetches all function tools from a specified MCP server. It utilizes an MCP span for tracing and then converts each retrieved tool into the Agents SDK's FunctionTool format. Dependencies include MCPServer, RunContextWrapper, and AgentBase.

```python
@classmethod
async def get_function_tools(
    cls,
    server: "MCPServer",
    convert_schemas_to_strict: bool,
    run_context: RunContextWrapper[Any],
    agent: "AgentBase",
) -> list[Tool]:
    """Get all function tools from a single MCP server."""

    with mcp_tools_span(server=server.name) as span:
        tools = await server.list_tools(run_context, agent)
        span.span_data.result = [tool.name for tool in tools]

    return [cls.to_function_tool(tool, server, convert_schemas_to_strict) for tool in tools]
```

--------------------------------

### Get Speech-to-Text Model (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/models/openai_model_provider

Retrieves a speech-to-text (STT) model by its name. If no model name is provided, a default STT model is used. This function requires an initialized OpenAI client to function.

```python
def get_stt_model(self, model_name: str | None) -> STTModel:
    """Get a speech-to-text model by name.

    Args:
        model_name: The name of the model to get.

    Returns:
        The speech-to-text model.
    """
    return OpenAISTTModel(model_name or DEFAULT_STT_MODEL, self._get_client())

```

--------------------------------

### Get Response using LitellmModel in Python

Source: https://openai.github.io/openai-agents-python/ko/ref/extensions/litellm

Fetches a response from the configured LiteLLM model. It handles system instructions, user input, model settings, tools, output schemas, and tracing for model generations. The method logs the received model response for debugging purposes.

```python
    async def get_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: ModelSettings,
        tools: list[Tool],
        output_schema: AgentOutputSchemaBase | None,
        handoffs: list[Handoff],
        tracing: ModelTracing,
        previous_response_id: str | None = None,  # unused
        conversation_id: str | None = None,  # unused
        prompt: Any | None = None,
    ) -> ModelResponse:
        with generation_span(
            model=str(self.model),
            model_config=model_settings.to_json_dict()
            | {"base_url": str(self.base_url or ""), "model_impl": "litellm"},
            disabled=tracing.is_disabled(),
        ) as span_generation:
            response = await self._fetch_response(
                system_instructions,
                input,
                model_settings,
                tools,
                output_schema,
                handoffs,
                span_generation,
                tracing,
                stream=False,
                prompt=prompt,
            )

            message: litellm.types.utils.Message | None = None
            first_choice: litellm.types.utils.Choices | None = None
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if isinstance(choice, litellm.types.utils.Choices):
                    first_choice = choice
                    message = first_choice.message

            if _debug.DONT_LOG_MODEL_DATA:
                logger.debug("Received model response")
            else:
                if message is not None:
                    logger.debug(
                        f"""LLM resp:
{                        json.dumps(message.model_dump(), indent=2, ensure_ascii=False)
                        }
"""
                    )
                else:

```

--------------------------------

### Merge Assistant Content in Python

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/session

Merges new assistant content with existing content, prioritizing new audio content with transcripts and preserving existing text content if new text is empty. Handles audio and text types distinctly.

```python
assistant_new_content.append(ac)
                                continue
                            assistant_current = assistant_existing_content[idx]
                            if ac.type == "audio":
                                if ac.transcript is None:
                                    assistant_new_content.append(assistant_current)
                                else:
                                    assistant_new_content.append(ac)
                            else:  # text
                                cur_text = (
                                    assistant_current.text
                                    if isinstance(assistant_current, AssistantText)
                                    else None
                                )
                                if cur_text is not None and ac.text is None:
                                    assistant_new_content.append(assistant_current)
                                else:
                                    assistant_new_content.append(ac)
                        updated_assistant = event.model_copy(
                            update={"content": assistant_new_content}
                        )
                        new_history[existing_index] = updated_assistant
```

--------------------------------

### Initialize OpenAI Responses Compaction Session (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/memory/openai_responses_compaction_session

Initializes the compaction session with session details, an underlying session store, and optional OpenAI client, model, compaction mode, and a custom trigger hook. It validates the session type and model name, ensuring compatibility with OpenAI's compaction API.

```python
def __init__(
    self,
    session_id: str,
    underlying_session: Session,
    *,
    client: AsyncOpenAI | None = None,
    model: str = "gpt-4.1",
    compaction_mode: OpenAIResponsesCompactionMode = "auto",
    should_trigger_compaction: Callable[[dict[str, Any]], bool] | None = None,
):
    """Initialize the compaction session.

    Args:
        session_id: Identifier for this session.
        underlying_session: Session store that holds the compacted history. Cannot be
            OpenAIConversationsSession.
        client: OpenAI client for responses.compact API calls. Defaults to
            get_default_openai_client() or new AsyncOpenAI().
        model: Model to use for responses.compact. Defaults to "gpt-4.1". Must be an
            OpenAI model name (gpt-*, o*, or ft:gpt-*).
        compaction_mode: Controls how the compaction request provides conversation
            history. "auto" (default) uses input when the last response was not
            stored or no response_id is available.
        should_trigger_compaction: Custom decision hook. Defaults to triggering when
            10+ compaction candidates exist.
    """
    if isinstance(underlying_session, OpenAIConversationsSession):
        raise ValueError(
            "OpenAIResponsesCompactionSession cannot wrap OpenAIConversationsSession "
            "because it manages its own history on the server."
        )

    if not is_openai_model_name(model):
        raise ValueError(f"Unsupported model for OpenAI responses compaction: {model}")

    self.session_id = session_id
    self.underlying_session = underlying_session
    self._client = client
    self.model = model
    self.compaction_mode = compaction_mode
    self.should_trigger_compaction = (
        should_trigger_compaction or default_should_trigger_compaction
    )

    # cache for incremental candidate tracking
    self._compaction_candidate_items: list[TResponseInputItem] | None = None
    self._session_items: list[TResponseInputItem] | None = None
    self._response_id: str | None = None
    self._deferred_response_id: str | None = None
    self._last_unstored_response_id: str | None = None

```

--------------------------------

### Get OpenAI Text-to-Speech Model in Python

Source: https://openai.github.io/openai-agents-python/ref/voice/models/openai_provider

Retrieves a text-to-speech (TTS) model from the OpenAIVoiceModelProvider. If no model name is provided, it defaults to `DEFAULT_TTS_MODEL`. This method ensures an OpenAI client is ready before returning the TTS model.

```python
def get_tts_model(self, model_name: str | None) -> TTSModel:
    """Get a text-to-speech model by name.

    Args:
        model_name: The name of the model to get.

    Returns:
        The text-to-speech model.
    """
    return OpenAITTSModel(model_name or DEFAULT_TTS_MODEL, self._get_client())
```

--------------------------------

### Get Text-to-Speech Model (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/models/openai_model_provider

Retrieves a text-to-speech (TTS) model by its name. If no model name is specified, a default TTS model is utilized. This method depends on a properly configured OpenAI client.

```python
def get_tts_model(self, model_name: str | None) -> TTSModel:
    """Get a text-to-speech model by name.

    Args:
        model_name: The name of the model to get.

    Returns:
        The text-to-speech model.
    """
    return OpenAITTSModel(model_name or DEFAULT_TTS_MODEL, self._get_client())

```

--------------------------------

### Using OpenAIConversationsSession for Agent Conversations

Source: https://openai.github.io/openai-agents-python/sessions

Shows how to integrate the Agents SDK with OpenAI's Conversations API using `OpenAIConversationsSession`. This allows agents to leverage OpenAI's managed conversation history. The example demonstrates creating a new conversation and optionally resuming a previous one using a conversation ID.

```python
from agents import Agent, Runner, OpenAIConversationsSession

# Create agent
agent = Agent(
    name="Assistant",
    instructions="Reply very concisely.",
)

# Create a new conversation
session = OpenAIConversationsSession()

# Optionally resume a previous conversation by passing a conversation ID
# session = OpenAIConversationsSession(conversation_id="conv_123")

# Start conversation
result = await Runner.run(
    agent,
    "What city is the Golden Gate Bridge in?",
    session=session
)
print(result.final_output)  # "San Francisco"

# Continue the conversation
result = await Runner.run(
    agent,
    "What state is it in?",
    session=session
)
print(result.final_output)  # "California"

```

--------------------------------

### AgentHooksBase: Handoff and Tool Callbacks (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/lifecycle

Provides methods for handling agent handoffs and tool invocations specific to an agent. `on_handoff` tracks transitions between agents, while `on_tool_start` and `on_tool_end` monitor tool usage.

```python
class AgentHooksBase[TContext, TAgent]:
    async def on_handoff(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        source: TAgent,
    ) -> None:
        """Called when the agent is being handed off to. The `source` is the agent that is handing off to this agent."""
        pass

    async def on_tool_start(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        tool: Tool,
    ) -> None:
        """Called immediately before a local tool is invoked."""
        pass

    async def on_tool_end(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        tool: Tool,
        result: str,
    ) -> None:
        """Called immediately after a local tool is invoked."""
        pass

```

--------------------------------

### Get Workflow Name from NoOpTrace in Python

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/traces

Retrieves the human-readable name of the workflow associated with the trace. For the NoOpTrace, this property consistently returns 'no-op' since no specific workflow is being traced.

```python
@property
def name(self) -> str:
    """The workflow name for this trace.

    Returns:
        str: Human-readable name describing this workflow.
    """
    return "no-op"

```

--------------------------------

### Get Trace ID from NoOpTrace in Python

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing/traces

Retrieves the unique identifier for a trace. For the NoOpTrace implementation, this property always returns the string 'no-op' as no actual trace data is recorded.

```python
@property
def trace_id(self) -> str:
    """The trace's unique identifier.

    Returns:
        str: A unique ID for this trace.
    """
    return "no-op"

```

--------------------------------

### FunctionTool Creation and Decorator Logic (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/tool

This snippet shows the process of creating a `FunctionTool` instance using a schema and the `_create_function_tool` helper. It also details how the `@function_tool` decorator handles both direct function wrapping and decorator usage with parentheses.

```python
return FunctionTool(
            name=schema.name,
            description=schema.description or "",
            params_json_schema=schema.params_json_schema,
            on_invoke_tool=_on_invoke_tool,
            strict_json_schema=strict_mode,
            is_enabled=is_enabled,
            tool_input_guardrails=tool_input_guardrails,
            tool_output_guardrails=tool_output_guardrails,
        )

    # If func is actually a callable, we were used as @function_tool with no parentheses
    if callable(func):
        return _create_function_tool(func)

    # Otherwise, we were used as @function_tool(...), so return a decorator
    def decorator(real_func: ToolFunction[...]) -> FunctionTool:
        return _create_function_tool(real_func)

    return decorator
```

--------------------------------

### Set Global Trace Provider - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/setup

Sets the global trace provider for tracing utilities. This function takes a `TraceProvider` object as input and assigns it to a global variable. It is crucial for initializing the tracing mechanism.

```python
def set_trace_provider(provider: TraceProvider) -> None:
    """Set the global trace provider used by tracing utilities."""
    global GLOBAL_TRACE_PROVIDER
    GLOBAL_TRACE_PROVIDER = provider
```

--------------------------------

### run_compaction

Source: https://openai.github.io/openai-agents-python/ko/ref/memory/openai_responses_compaction_session

Runs the compaction process for OpenAI responses. This method is asynchronous and can be configured with various arguments to control the compaction mode and storage behavior.

```APIDOC
## POST /run_compaction

### Description
Runs the compaction process for OpenAI responses using the `responses.compact` API. This method is asynchronous and can be configured with various arguments to control the compaction mode and storage behavior.

### Method
POST

### Endpoint
/run_compaction

### Parameters
#### Query Parameters
- **args** (OpenAIResponsesCompactionArgs | None) - Optional - Arguments to control the compaction process, including `response_id`, `compaction_mode`, and `store`.

### Request Body
```json
{
  "response_id": "string",
  "compaction_mode": "string",
  "store": "boolean",
  "force": "boolean"
}
```

### Response
#### Success Response (200)
- **None** - This method does not return a value upon successful execution.

#### Response Example
```json
null
```
```

--------------------------------

### Handle Response Created and Done Events in Python

Source: https://openai.github.io/openai-agents-python/ko/ref/realtime/openai_realtime

Manages the start and end of a response from the realtime model. 'response.created' sets an internal flag and emits a `RealtimeModelTurnStartedEvent`. 'response.done' clears the flag and emits a `RealtimeModelTurnEndedEvent`.

```python
elif parsed.type == "response.created":
            self._ongoing_response = True
            await self._emit_event(RealtimeModelTurnStartedEvent())
        elif parsed.type == "response.done":
            self._ongoing_response = False
            await self._emit_event(RealtimeModelTurnEndedEvent())
```

--------------------------------

### Add Text and Initiate Audio Streaming in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/result

This method appends new text to a buffer, splits it into sentences, and initiates audio streaming tasks. It manages text buffers and ensures that the audio dispatching task is running.

```python
async def _add_text(self, text: str):
        await self._start_turn()

        self._text_buffer += text
        self.total_output_text += text
        self._turn_text_buffer += text

        combined_sentences, self._text_buffer = self.tts_settings.text_splitter(self._text_buffer)

        if len(combined_sentences) >= 20:
            local_queue: asyncio.Queue[VoiceStreamEvent | None] = asyncio.Queue()
            self._ordered_tasks.append(local_queue)
            self._tasks.append(
                asyncio.create_task(self._stream_audio(combined_sentences, local_queue))
            )
            if self._dispatcher_task is None:
                self._dispatcher_task = asyncio.create_task(self._dispatch_audio())
```

--------------------------------

### Get All Function Tools from MCP Servers (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/mcp/util

This class method retrieves all function tools available across a list of MCP servers. It ensures that tool names are unique across all servers to prevent conflicts. Dependencies include MCPServer, RunContextWrapper, and AgentBase.

```python
@classmethod
async def get_all_function_tools(
    cls,
    servers: list["MCPServer"],
    convert_schemas_to_strict: bool,
    run_context: RunContextWrapper[Any],
    agent: "AgentBase",
) -> list[Tool]:
    """Get all function tools from a list of MCP servers."""
    tools = []
    tool_names: set[str] = set()
    for server in servers:
        server_tools = await cls.get_function_tools(
            server, convert_schemas_to_strict, run_context, agent
        )
        server_tool_names = {tool.name for tool in server_tools}
        if len(server_tool_names & tool_names) > 0:
            raise UserError(
                f"Duplicate tool names found across MCP servers: "
                f"{server_tool_names & tool_names}"
            )
        tool_names.update(server_tool_names)
        tools.extend(server_tools)

    return tools
```

--------------------------------

### Conditionally Enable Agent Tools with `is_enabled`

Source: https://openai.github.io/openai-agents-python/tools

This example shows how to conditionally enable or disable agent tools at runtime using the `is_enabled` parameter. It defines a `LanguageContext` and a `french_enabled` function to control tool availability. The orchestrator agent uses these tools, demonstrating dynamic filtering based on context. The `is_enabled` parameter can accept boolean values or callable functions (sync or async).

```python
import asyncio
from agents import Agent, AgentBase, Runner, RunContextWrapper
from pydantic import BaseModel

class LanguageContext(BaseModel):
    language_preference: str = "french_spanish"

def french_enabled(ctx: RunContextWrapper[LanguageContext], agent: AgentBase) -> bool:
    """Enable French for French+Spanish preference."""
    return ctx.context.language_preference == "french_spanish"

# Create specialized agents
spanish_agent = Agent(
    name="spanish_agent",
    instructions="You respond in Spanish. Always reply to the user's question in Spanish.",
)

french_agent = Agent(
    name="french_agent",
    instructions="You respond in French. Always reply to the user's question in French.",
)

# Create orchestrator with conditional tools
orchestrator = Agent(
    name="orchestrator",
    instructions=(
        "You are a multilingual assistant. You use the tools given to you to respond to users. "
        "You must call ALL available tools to provide responses in different languages. "
        "You never respond in languages yourself, you always use the provided tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="respond_spanish",
            tool_description="Respond to the user's question in Spanish",
            is_enabled=True,  # Always enabled
        ),
        french_agent.as_tool(
            tool_name="respond_french",
            tool_description="Respond to the user's question in French",
            is_enabled=french_enabled,
        ),
    ],
)

async def main():
    context = RunContextWrapper(LanguageContext(language_preference="french_spanish"))
    result = await Runner.run(orchestrator, "How are you?", context=context.context)
    print(result.final_output)

asyncio.run(main())

```

--------------------------------

### Get OpenAI Speech-to-Text Model in Python

Source: https://openai.github.io/openai-agents-python/ref/voice/models/openai_provider

Retrieves a speech-to-text (STT) model from the OpenAIVoiceModelProvider. If no model name is specified, it defaults to `DEFAULT_STT_MODEL`. This method ensures that an OpenAI client is available before returning the STT model.

```python
def get_stt_model(self, model_name: str | None) -> STTModel:
    """Get a speech-to-text model by name.

    Args:
        model_name: The name of the model to get.

    Returns:
        The speech-to-text model.
    """
    return OpenAISTTModel(model_name or DEFAULT_STT_MODEL, self._get_client())
```

--------------------------------

### Realtime Agent Attributes

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/agent

This section details the various attributes that can be configured for a RealtimeAgent, including instructions, prompt, handoffs, output guardrails, hooks, name, handoff description, tools, MCP servers, and MCP configuration.

```APIDOC
## Realtime Agent Attributes

### Instructions
- **Type**: `str` | `Callable` | `None`
- **Description**: The instructions for the agent, used as the system prompt. Can be a static string or a function that dynamically generates instructions based on context and agent instance.

### Prompt
- **Type**: `Prompt` | `None`
- **Description**: A prompt object for dynamically configuring instructions, tools, and other settings. Only usable with OpenAI models.

### Handoffs
- **Type**: `list[RealtimeAgent | Handoff]`
- **Description**: A list of sub-agents (handoffs) that the agent can delegate to. This allows for modularity and separation of concerns.

### Output Guardrails
- **Type**: `list[OutputGuardrail]`
- **Description**: A list of checks applied to the agent's final output after generating a response.

### Hooks
- **Type**: `RealtimeAgentHooks` | `None`
- **Description**: A class that receives callbacks for various agent lifecycle events.

### Name
- **Type**: `str`
- **Description**: The unique name of the agent.

### Handoff Description
- **Type**: `str` | `None`
- **Description**: A description of the agent used when it acts as a handoff, informing an LLM about its purpose and when to invoke it.

### Tools
- **Type**: `list[Tool]`
- **Description**: A list of tools available for the agent to use.

### MCP Servers
- **Type**: `list[MCPServer]`
- **Description**: A list of Model Context Protocol servers that the agent can utilize. Tools from these servers are included when the agent runs. Note: The lifecycle of these servers (connect/cleanup) must be managed externally or via `MCPServerManager`.

### MCP Config
- **Type**: `MCPConfig`
- **Description**: Configuration settings for MCP servers.
```

--------------------------------

### Create Database Tables for Conversation History (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/memory/sqlite_session

Initializes the 'sessions' and 'messages' tables in the SQLite database. It ensures the existence of these tables and sets up foreign key constraints and indexes for efficient data management. This function is crucial for the initial setup of the conversation history storage.

```python
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON {self.sessions_table} (session_id)
            )
        """
        )

        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.messages_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_data TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES {self.sessions_table} (session_id)
                    ON DELETE CASCADE
            )
        """
        )

        conn.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{self.messages_table}_session_id
            ON {self.messages_table} (session_id, id)
        """
        )

        conn.commit()
```

--------------------------------

### Realtime Input Audio Transcription Configuration (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/config

Defines the configuration for transcribing input audio in realtime sessions. It allows specifying the language, transcription model, and an optional prompt to guide the transcription process. This configuration is crucial for accurately converting spoken language into text for agent processing.

```python
class RealtimeInputAudioTranscriptionConfig(TypedDict):
    """Configuration for audio transcription in realtime sessions."""

    language: NotRequired[str]
    """The language code for transcription."""

    model: NotRequired[Literal["gpt-4o-transcribe", "gpt-4o-mini-transcribe", "whisper-1"] | str]
    """The transcription model to use."""

    prompt: NotRequired[str]
    """An optional prompt to guide transcription."""

```

--------------------------------

### Get Tool Usage by Turn (Python)

Source: https://openai.github.io/openai-agents-python/ko/ref/extensions/memory/advanced_sqlite_session

Fetches tool usage statistics for a given branch within a session. It counts the occurrences of various tool call types per user turn and returns a list of tuples, each containing the tool name, its usage count, and the corresponding turn number. Supports fetching for the current branch if branch_id is omitted.

```python
async def get_tool_usage(self, branch_id: str | None = None) -> list[tuple[str, int, int]]:
        """Get all tool usage by turn for specified branch.

        Args:
            branch_id: Branch to get tool usage from (current branch if None).

        Returns:
            List of tuples containing (tool_name, usage_count, turn_number).
        """
        if branch_id is None:
            branch_id = self._current_branch_id

        def _get_tool_usage_sync():
            """Synchronous helper to get tool usage statistics."""
            conn = self._get_connection()
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    """
                    SELECT tool_name, COUNT(*), user_turn_number
                    FROM message_structure
                    WHERE session_id = ? AND branch_id = ? AND message_type IN (
                        'tool_call', 'function_call', 'computer_call', 'file_search_call',
                        'web_search_call', 'code_interpreter_call', 'custom_tool_call',
                        'mcp_call', 'mcp_approval_request'
                    )
                    GROUP BY tool_name, user_turn_number
                    ORDER BY user_turn_number
                """,
                    (self.session_id, branch_id),
                )
                return cursor.fetchall()

        return await asyncio.to_thread(_get_tool_usage_sync)
```

--------------------------------

### Agent Handoffs for Delegation (Python)

Source: https://openai.github.io/openai-agents-python/agents

Illustrates the handoff pattern where an agent can delegate conversations to specialized sub-agents. The triage agent, for example, directs users to booking or refund agents based on their queries, enabling modular agent design.

```python
from agents import Agent

booking_agent = Agent(...)
refund_agent = Agent(...)

triage_agent = Agent(
    name="Triage agent",
    instructions=(
        "Help the user with their questions. "
        "If they ask about booking, hand off to the booking agent. "
        "If they ask about refunds, hand off to the refund agent."
    ),
    handoffs=[booking_agent, refund_agent],
)

```

--------------------------------

### Get Current Mapping from MultiProviderMap

Source: https://openai.github.io/openai-agents-python/ko/ref/models/multi_provider

The `get_mapping` method returns a shallow copy of the current dictionary that maps model name prefixes to `ModelProvider` objects. This prevents external modification of the internal mapping.

```python
def get_mapping(self) -> dict[str, ModelProvider]:
    """Returns a copy of the current prefix -> ModelProvider mapping."""
    return self._mapping.copy()
```

--------------------------------

### List Tools on Server (Python)

Source: https://openai.github.io/openai-agents-python/ref/mcp/server

Abstract method to list available tools on the server. It takes an optional run context and agent as input and returns a list of Tool objects. This method is part of the MCP server interface.

```python
import abc
from typing import Any, List

# Assuming these types are defined elsewhere
class RunContextWrapper:
    pass

class AgentBase:
    pass

class Tool:
    pass

class MCPTool(Tool):
    pass

class MCPBaseServer(abc.ABC):
    @abc.abstractmethod
    async def list_tools(self, run_context: RunContextWrapper[Any] | None = None, agent: AgentBase | None = None) -> list[MCPTool]:
        """List the tools available on the server."""
        pass

```

--------------------------------

### Prepare Tools for LLM API Calls (Python)

Source: https://openai.github.io/openai-agents-python/ref/extensions/litellm

Converts internal tool representations into the format required by LLM APIs, including support for parallel tool calls and handoff tools. It also handles tool choice and response format conversions.

```python
parallel_tool_calls = (
    True
    if model_settings.parallel_tool_calls and tools and len(tools) > 0
    else False
    if model_settings.parallel_tool_calls is False
    else None
)
tool_choice = Converter.convert_tool_choice(model_settings.tool_choice)
response_format = Converter.convert_response_format(output_schema)

converted_tools = [Converter.tool_to_openai(tool) for tool in tools] if tools else []

for handoff in handoffs:
    converted_tools.append(Converter.convert_handoff_tool(handoff))

converted_tools = _to_dump_compatible(converted_tools)
```

--------------------------------

### VoicePipelineConfig Dataclass Definition

Source: https://openai.github.io/openai-agents-python/ref/voice/pipeline_config

Defines the configuration structure for a VoicePipeline. It includes settings for model providers, tracing behavior, workflow naming, group identification, and STT/TTS configurations. Defaults are provided for most attributes to simplify setup.

```python
@dataclass
class VoicePipelineConfig:
    """Configuration for a `VoicePipeline`."""

    model_provider: VoiceModelProvider = field(default_factory=OpenAIVoiceModelProvider)
    """The voice model provider to use for the pipeline. Defaults to OpenAI."""

    tracing_disabled: bool = False
    """Whether to disable tracing of the pipeline. Defaults to `False`."""

    tracing: TracingConfig | None = None
    """Tracing configuration for this pipeline."""

    trace_include_sensitive_data: bool = True
    """Whether to include sensitive data in traces. Defaults to `True`. This is specifically for the
      voice pipeline, and not for anything that goes on inside your Workflow."""

    trace_include_sensitive_audio_data: bool = True
    """Whether to include audio data in traces. Defaults to `True`."""

    workflow_name: str = "Voice Agent"
    """The name of the workflow to use for tracing. Defaults to `Voice Agent`."""

    group_id: str = field(default_factory=gen_group_id)
    """
    A grouping identifier to use for tracing, to link multiple traces from the same conversation
    or process. If not provided, we will create a random group ID.
    """

    trace_metadata: dict[str, Any] | None = None
    """
    An optional dictionary of additional metadata to include with the trace.
    """

    stt_settings: STTModelSettings = field(default_factory=STTModelSettings)
    """The settings to use for the STT model."""

    tts_settings: TTSModelSettings = field(default_factory=TTSModelSettings)
    """The settings to use for the TTS model."""

```

--------------------------------

### Create SQLAlchemy Session from URL (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/extensions/memory/sqlalchemy_session

The `from_url` class method instantiates a SQLAlchemySession using a provided database URL. It accepts session ID, the URL string, and optional engine keyword arguments for SQLAlchemy's create_async_engine. It returns a configured SQLAlchemySession instance.

```python
from sqlalchemy.ext.asyncio import create_async_engine

# Assuming SQLAlchemySession and TResponseInputItem are defined elsewhere
# class SQLAlchemySession:
#     def __init__(self, session_id: str, engine, **kwargs):
#         self.session_id = session_id
#         self._engine = engine
#         # ... other initializations ...

#     @classmethod
#     def from_url(
#         cls,
#         session_id: str,
#         *, 
#         url: str,
#         engine_kwargs: dict[str, Any] | None = None,
#         **kwargs: Any,
#     ) -> SQLAlchemySession:
#         """Create a session from a database URL string."""
#         engine_kwargs = engine_kwargs or {}
#         engine = create_async_engine(url, **engine_kwargs)
#         return cls(session_id, engine=engine, **kwargs)

# Example Usage:
# session = SQLAlchemySession.from_url(
#     session_id="my_conversation_id",
#     url="postgresql+asyncpg://user:pass@host/db"
# )
```

--------------------------------

### Start Transcription Turn in Python

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/models/openai_stt

Initiates a new transcription turn by creating a tracing span. This span captures model configuration details such as temperature, language, prompt, and turn detection settings for logging and analysis.

```python
def _start_turn(self) -> None:
    self._tracing_span = transcription_span(
        model=self._model,
        model_config={
            "temperature": self._settings.temperature,
            "language": self._settings.language,
            "prompt": self._settings.prompt,
            "turn_detection": self._turn_detection,
        },
    )
    self._tracing_span.start()
```

--------------------------------

### List Tools - Python

Source: https://openai.github.io/openai-agents-python/ko/ref/mcp/server

Abstract method to list available tools on the server. It takes an optional run_context and agent as input and returns a list of Tool objects.

```python
import abc
from typing import Any, List

from ..client.run_context import RunContextWrapper
from ..tools.tool import Tool
from .base import AgentBase
from .mcp_tool import MCPTool


class MCPBase(abc.ABC):
    @abc.abstractmethod
    async def list_tools(self, run_context: RunContextWrapper[Any] | None = None, agent: AgentBase | None = None) -> List[MCPTool]:
        """List the tools available on the server."""
        pass

```

--------------------------------

### Function Span Creation

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/create

This describes the `function_span` function used to create a new function span. Spans are not started automatically and require manual start/finish calls or usage within a `with` statement.

```APIDOC
## POST /function_span

### Description
Creates a new function span for tracing. This span is not automatically started; you must use `with function_span() ...` or manually call `span.start()` and `span.finish()`.

### Method
POST

### Endpoint
`/function_span`

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **name** (str) - Required - The name of the function.
- **input** (str | None) - Optional - The input to the function.
- **output** (str | None) - Optional - The output of the function.
- **span_id** (str | None) - Optional - The ID of the span. If not provided, an ID will be generated.
- **parent** (Trace | Span[Any] | None) - Optional - The parent span or trace. Defaults to the current trace/span.
- **disabled** (bool) - Optional - If True, the span will not be recorded. Defaults to `False`.

### Request Example
```json
{
  "name": "my_function",
  "input": "some_input_data",
  "parent": null,
  "span_id": null,
  "disabled": false
}
```

### Response
#### Success Response (200)
- **Span[FunctionSpanData]** - The newly created function span.

#### Response Example
```json
{
  "span_id": "generated_span_id",
  "name": "my_function",
  "input": "some_input_data",
  "output": null,
  "parent_id": "current_parent_id",
  "start_time": "timestamp",
  "end_time": null
}
```
```

--------------------------------

### Synchronous Agent Workflow Execution with Runner.run_sync

Source: https://openai.github.io/openai-agents-python/ja/ref/run

The `run_sync` method provides a synchronous way to execute an agent workflow. It accepts the same parameters as the `run` method, including the starting agent, input, context, and other configuration options. This method is suitable for environments where asynchronous operations are not preferred or possible.

```python
    @classmethod
    def run_sync(
        cls,
        starting_agent: Agent[TContext],
        input: str | list[TResponseInputItem],
        *,
        context: TContext | None = None,
        max_turns: int = DEFAULT_MAX_TURNS,
        hooks: RunHooks[TContext] | None = None,
        run_config: RunConfig | None = None,
        previous_response_id: str | None = None,
        auto_previous_response_id: bool = False,
        conversation_id: str | None = None,

```

--------------------------------

### Create Guardrail Span

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing

Creates a new guardrail span. This span can be used to track specific guardrail operations within a trace. The span requires manual start and finish calls or can be used with a context manager.

```APIDOC
## POST /tracing/guardrail_span

### Description
Create a new guardrail span. The span will not be started automatically, you should either do `with guardrail_span() ...` or call `span.start()` + `span.finish()` manually.

### Method
POST

### Endpoint
/tracing/guardrail_span

### Parameters
#### Query Parameters
None

#### Request Body
- **name** (string) - Required - The name of the guardrail.
- **triggered** (boolean) - Optional - Whether the guardrail was triggered. Defaults to `False`.
- **span_id** (string | null) - Optional - The ID of the span. If not provided, an ID will be generated.
- **parent** (Trace | Span[Any] | null) - Optional - The parent span or trace. If not provided, the current trace/span will be used as the parent.
- **disabled** (boolean) - Optional - If True, the Span will not be recorded. Defaults to `False`.

### Request Example
```json
{
  "name": "input_validation",
  "triggered": true,
  "span_id": "span-abc",
  "parent": {
    "id": "trace-123"
  },
  "disabled": false
}
```

### Response
#### Success Response (200)
- **span_id** (string) - The ID of the created span.
- **name** (string) - The name of the guardrail span.
- **start_time** (string) - The start time of the span.

#### Response Example
```json
{
  "span_id": "span-abc",
  "name": "input_validation",
  "start_time": "2023-10-27T10:05:00Z"
}
```
```

--------------------------------

### Database Table Initialization and Indexing (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/memory

Initializes the messages and sessions tables in the database and creates an index for efficient querying of session messages. It handles foreign key constraints and ensures data integrity.

```python
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.messages_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_data TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES {self.sessions_table} (session_id)
                    ON DELETE CASCADE
            )
        """
        )

        conn.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{self.messages_table}_session_id
            ON {self.messages_table} (session_id, id)
        """
        )

        conn.commit()
```

--------------------------------

### Copy Messages Between Branches (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/memory/advanced_sqlite_session

Inserts copies of existing messages into a new branch within the same session. It determines the starting sequence number for the new branch and appends new entries to the 'message_structure' table.

```python
async def _copy_sync(self):
    """Synchronous helper to copy messages to a new branch."""
    conn = self._get_connection()
    with closing(conn.cursor()) as cursor:
        # Get the starting sequence number for the new branch
        cursor.execute(
            """
            SELECT MAX(sequence_number) FROM message_structure
            WHERE session_id = ? AND branch_id = ?
            """,
            (self.session_id, new_branch_id),
        )

        seq_start = cursor.fetchone()[0]

        # Insert copied messages with new branch_id
        new_structure_data = []
        for i, (
            msg_id,
            msg_type,
            _,
            user_turn,
            branch_turn,
            tool_name,
        ) in enumerate(messages_to_copy):
            new_structure_data.append(
                (
                    self.session_id,
                    msg_id,  # Same message_id (sharing the actual message data)
                    new_branch_id,
                    msg_type,
                    seq_start + i + 1,  # New sequence number
                    user_turn,  # Keep same global turn number
                    branch_turn,  # Keep same branch turn number
                    tool_name,
                )
            )

        cursor.executemany(
            """
            INSERT INTO message_structure
            (session_id, message_id, branch_id, message_type, sequence_number,
             user_turn_number, branch_turn_number, tool_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            new_structure_data,
        )

    conn.commit()

await asyncio.to_thread(_copy_sync)
```

--------------------------------

### on_trace_start

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/processor_interface

This method is called synchronously when a new trace begins execution. It should return quickly to avoid blocking the execution. Any errors encountered should be handled internally.

```APIDOC
## on_trace_start

### Description
Called when a new trace begins execution.

### Method
`on_trace_start`

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **trace** (`Trace`) - Required - The trace that started. Contains workflow name and metadata.

### Request Example
```json
{
  "trace": { "workflow_name": "example_workflow", "metadata": {} }
}
```

### Response
#### Success Response (200)
None

#### Response Example
```json
null
```

### Notes
- Called synchronously on trace start
- Should return quickly to avoid blocking execution
- Any errors should be caught and handled internally
```

--------------------------------

### Get Server Name Property (Python)

Source: https://openai.github.io/openai-agents-python/ref/mcp/server

Retrieves a readable name for the server. This property is defined within the server class and returns a string representing the server's name.

```python
    @property
    def name(self) -> str:
        """A readable name for the server."""
        return self._name
```

```python
name: str
```

--------------------------------

### BatchTraceProcessor Initialization and Thread Management

Source: https://openai.github.io/openai-agents-python/ref/tracing/processors

Initializes the BatchTraceProcessor with configuration for queue size, batch size, schedule delay, and export trigger ratio. It also manages a background worker thread for asynchronous export, ensuring the thread is started only when necessary using a double-checked locking pattern.

```python
class BatchTraceProcessor(TracingProcessor):
    """Some implementation notes:
    1. Using Queue, which is thread-safe.
    2. Using a background thread to export spans, to minimize any performance issues.
    3. Spans are stored in memory until they are exported.
    """

    def __init__(
        self,
        exporter: TracingExporter,
        max_queue_size: int = 8192,
        max_batch_size: int = 128,
        schedule_delay: float = 5.0,
        export_trigger_ratio: float = 0.7,
    ):
        """
        Args:
            exporter: The exporter to use.
            max_queue_size: The maximum number of spans to store in the queue. After this, we will
                start dropping spans.
            max_batch_size: The maximum number of spans to export in a single batch.
            schedule_delay: The delay between checks for new spans to export.
            export_trigger_ratio: The ratio of the queue size at which we will trigger an export.
        """
        self._exporter = exporter
        self._queue: queue.Queue[Trace | Span[Any]] = queue.Queue(maxsize=max_queue_size)
        self._max_queue_size = max_queue_size
        self._max_batch_size = max_batch_size
        self._schedule_delay = schedule_delay
        self._shutdown_event = threading.Event()

        # The queue size threshold at which we export immediately.
        self._export_trigger_size = max(1, int(max_queue_size * export_trigger_ratio))

        # Track when we next *must* perform a scheduled export
        self._next_export_time = time.time() + self._schedule_delay

        # We lazily start the background worker thread the first time a span/trace is queued.
        self._worker_thread: threading.Thread | None = None
        self._thread_start_lock = threading.Lock()

    def _ensure_thread_started(self) -> None:
        # Fast path without holding the lock
        if self._worker_thread and self._worker_thread.is_alive():
            return

        # Double-checked locking to avoid starting multiple threads
        with self._thread_start_lock:
            if self._worker_thread and self._worker_thread.is_alive():
                return

            self._worker_thread = threading.Thread(target=self._run, daemon=True)
            self._worker_thread.start()
```

--------------------------------

### Get Trace ID - Python

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing

Retrieves the globally unique identifier for a trace. This ID is formatted as 'trace_<32_alphanumeric>' and is used to link spans to their parent trace for lookup in the dashboard.

```python
trace_id: str

# Returns:
# Name | Type | Description
# `str` |  `str` |  The trace's unique ID in the format 'trace_<32_alphanumeric>'
```

--------------------------------

### Use Non-OpenAI Models with LiteLLM Prefix

Source: https://openai.github.io/openai-agents-python/models

Utilize non-OpenAI models by prefixing their names with 'litellm/'. This enables the Agents SDK to route requests through LiteLLM to the specified model, such as Anthropic's Claude or Google's Gemini. Ensure LiteLLM is installed and the model names are correctly formatted.

```python
from agents import Agent

claude_agent = Agent(model="litellm/anthropic/claude-3-5-sonnet-20240620")
gemini_agent = Agent(model="litellm/gemini/gemini-2.5-flash-preview-04-17")
```

--------------------------------

### RealtimeAgent Class Definition and Initialization

Source: https://openai.github.io/openai-agents-python/ref/realtime/agent

Defines the RealtimeAgent class, inheriting from AgentBase and Generic. It outlines supported and unsupported configurations for voice agents within a RealtimeSession, including dynamic instructions and handoffs.

```python
from dataclasses import dataclass, field
from typing import Any, Generic, TContext, Callable, MaybeAwaitable, cast, Awaitable

from ...base import AgentBase, RunContextWrapper
from ...tools.output_guardrail import OutputGuardrail
from ...prompts import Prompt
from .handoff import Handoff, RealtimeAgent
from .hooks import RealtimeAgentHooks

import inspect
import logging

logger = logging.getLogger(__name__) # pylint: disable=invalid-name


@dataclass
class RealtimeAgent(AgentBase, Generic[TContext]):
    """A specialized agent instance that is meant to be used within a `RealtimeSession` to build
    voice agents. Due to the nature of this agent, some configuration options are not supported
    that are supported by regular `Agent` instances. For example:
    - `model` choice is not supported, as all RealtimeAgents will be handled by the same model
      within a `RealtimeSession`.
    - `modelSettings` is not supported, as all RealtimeAgents will be handled by the same model
      within a `RealtimeSession`.
    - `outputType` is not supported, as RealtimeAgents do not support structured outputs.
    - `toolUseBehavior` is not supported, as all RealtimeAgents will be handled by the same model
      within a `RealtimeSession`.
    - `voice` can be configured on an `Agent` level; however, it cannot be changed after the first
      agent within a `RealtimeSession` has spoken.

    See `AgentBase` for base parameters that are shared with `Agent`s.
    """

    instructions: (
        str
        | Callable[
            [RunContextWrapper[TContext], RealtimeAgent[TContext]],
            MaybeAwaitable[str],
        ]
        | None
    ) = None
    """The instructions for the agent. Will be used as the "system prompt" when this agent is
    invoked. Describes what the agent should do, and how it responds.

    Can either be a string, or a function that dynamically generates instructions for the agent. If
    you provide a function, it will be called with the context and the agent instance. It must
    return a string.
    """

    prompt: Prompt | None = None
    """A prompt object. Prompts allow you to dynamically configure the instructions, tools
    and other config for an agent outside of your code. Only usable with OpenAI models.
    """

    handoffs: list[RealtimeAgent[Any] | Handoff[TContext, RealtimeAgent[Any]]] = field(
        default_factory=list
    )
    """Handoffs are sub-agents that the agent can delegate to. You can provide a list of handoffs,
    and the agent can choose to delegate to them if relevant. Allows for separation of concerns and
    modularity.
    """

    output_guardrails: list[OutputGuardrail[TContext]] = field(default_factory=list)
    """A list of checks that run on the final output of the agent, after generating a response.
    Runs only if the agent produces a final output.
    """

    hooks: RealtimeAgentHooks | None = None
    """A class that receives callbacks on various lifecycle events for this agent.
    """

    def clone(self, **kwargs: Any) -> RealtimeAgent[TContext]:
        """Make a copy of the agent, with the given arguments changed. For example, you could do:
        ```
        new_agent = agent.clone(instructions="New instructions")
        ```
        """
        return dataclasses.replace(self, **kwargs)

    async def get_system_prompt(self, run_context: RunContextWrapper[TContext]) -> str | None:
        """Get the system prompt for the agent."""
        if isinstance(self.instructions, str):
            return self.instructions
        elif callable(self.instructions):
            if inspect.iscoroutinefunction(self.instructions):
                return await cast(Awaitable[str], self.instructions(run_context, self))
            else:
                return cast(str, self.instructions(run_context, self))
        elif self.instructions is not None:
            logger.error(f"Instructions must be a string or a function, got {self.instructions}")

        return None

```

--------------------------------

### Get Model by Name - Python

Source: https://openai.github.io/openai-agents-python/ko/ref/models/interface

Abstract method to retrieve a model by its name. It takes the model name as an argument and returns a Model object. This is a core function for model providers to expose available models.

```python
import abc

# Assuming Model is defined elsewhere
class Model:
    pass

class ModelProvider(abc.ABC):
    @abc.abstractmethod
    def get_model(self, model_name: str | None) -> Model:
        """Get a model by name.

        Args:
            model_name: The name of the model to get.

        Returns:
            The model.
        """
        pass

```

--------------------------------

### Get Trace Name - Python

Source: https://openai.github.io/openai-agents-python/ko/ref/tracing

Retrieves the human-readable name of a workflow trace. This name should be descriptive and is used for grouping and filtering traces in the dashboard, helping to identify the purpose of the trace.

```Python
name: str

"""
Get the human-readable name of this workflow trace.

Returns:
    str: The workflow name (e.g., "Customer Service", "Data Processing")

Notes:
  * Should be descriptive and meaningful
  * Used for grouping and filtering in the dashboard
  * Helps identify the purpose of the trace
"""
pass
```

--------------------------------

### Set up HTTP with SSE MCP Server (Deprecated)

Source: https://openai.github.io/openai-agents-python/mcp

This snippet illustrates how to instantiate an MCP server using the Server-Sent Events (SSE) transport with `MCPServerSse`. While functional, SSE is deprecated in favor of Streamable HTTP or stdio for new integrations. The API is similar to Streamable HTTP servers.

```python
from agents import Agent, Runner
from agents.model_settings import ModelSettings
from agents.mcp import MCPServerSse

workspace_id = "demo-workspace"

async with MCPServerSse(
    name="SSE Python Server",
    params={
        "url": "http://localhost:8000/sse",
        "headers": {"X-Workspace": workspace_id},
    },
    cache_tools_list=True,
) as server:
    agent = Agent(
        name="Assistant",
        mcp_servers=[server],
        model_settings=ModelSettings(tool_choice="required"),
    )
    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)


```

--------------------------------

### Create MCP List Tools Span (Python)

Source: https://openai.github.io/openai-agents-python/ref/tracing

Creates a new span for MCP list tools operations. Spans are not automatically started and require manual start/finish calls or usage within a `with` statement. It accepts optional parameters for server, result, span ID, parent span/trace, and a disabled flag.

```python
def mcp_tools_span(
    server: str | None = None,
    result: list[str] | None = None,
    span_id: str | None = None,
    parent: Trace | Span[Any] | None = None,
    disabled: bool = False,
) -> Span[MCPListToolsSpanData]:
    """Create a new MCP list tools span. The span will not be started automatically, you should
    either do `with mcp_tools_span() ...` or call `span.start()` + `span.finish()` manually.

    Args:
        server: The name of the MCP server.
        result: The result of the MCP list tools call.
        span_id: The ID of the span. Optional. If not provided, we will generate an ID. We
            recommend using `util.gen_span_id()` to generate a span ID, to guarantee that IDs are
            correctly formatted.
        parent: The parent span or trace. If not provided, we will automatically use the current
            trace/span as the parent.
        disabled: If True, we will return a Span but the Span will not be recorded.
    """
    return get_trace_provider().create_span(
        span_data=MCPListToolsSpanData(server=server, result=result),
        span_id=span_id,
        parent=parent,
        disabled=disabled,
    )

```

--------------------------------

### Get Specific Turn Usage Details (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/extensions/memory/advanced_sqlite_session

Fetches detailed usage statistics for a specific user turn within a session and branch. It includes token counts and detailed JSON breakdowns for input and output tokens. Returns an empty dictionary if the turn is not found.

```python
if user_turn_number is not None:
                query = """
                    SELECT requests, input_tokens, output_tokens, total_tokens,
                           input_tokens_details, output_tokens_details
                    FROM turn_usage
                    WHERE session_id = ? AND branch_id = ? AND user_turn_number = ?
                """

                with closing(conn.cursor()) as cursor:
                    cursor.execute(query, (self.session_id, branch_id, user_turn_number))
                    row = cursor.fetchone()

                    if row:
                        # Parse JSON details if present
                        input_details = None
                        output_details = None

                        if row[4]:  # input_tokens_details
                            try:
                                input_details = json.loads(row[4])
                            except json.JSONDecodeError:
                                pass

                        if row[5]:  # output_tokens_details
                            try:
                                output_details = json.loads(row[5])
                            except json.JSONDecodeError:
                                pass

                        return {
                            "requests": row[0],
                            "input_tokens": row[1],
                            "output_tokens": row[2],
                            "total_tokens": row[3],
                            "input_tokens_details": input_details,
                            "output_tokens_details": output_details,
                        }
                    return {}
```

--------------------------------

### Manage Transcription Turn with Tracing (Python)

Source: https://openai.github.io/openai-agents-python/ref/voice/models/openai_stt

Handles the start and end of a transcription turn, including setting up and finishing tracing spans. It can optionally include sensitive data and audio in the trace logs based on configuration.

```python
    def _start_turn(self) -> None:
        self._tracing_span = transcription_span(
            model=self._model,
            model_config={
                "temperature": self._settings.temperature,
                "language": self._settings.language,
                "prompt": self._settings.prompt,
                "turn_detection": self._turn_detection,
            },
        )
        self._tracing_span.start()

    def _end_turn(self, _transcript: str) -> None:
        if len(_transcript) < 1:
            return

        if self._tracing_span:
            # Only encode audio if tracing is enabled AND buffer is not empty
            if self._trace_include_sensitive_audio_data and self._turn_audio_buffer:
                self._tracing_span.span_data.input = _audio_to_base64(self._turn_audio_buffer)

            self._tracing_span.span_data.input_format = "pcm"

            if self._trace_include_sensitive_data:
                self._tracing_span.span_data.output = _transcript

            self._tracing_span.finish()
            self._turn_audio_buffer = []
            self._tracing_span = None
```

--------------------------------

### AdvancedSQLiteSession Initialization

Source: https://openai.github.io/openai-agents-python/zh/ref/extensions/memory/advanced_sqlite_session

Initializes the AdvancedSQLiteSession with provided parameters, including session ID, database path, and table creation options.

```APIDOC
## AdvancedSQLiteSession `__init__`

### Description
Initializes the AdvancedSQLiteSession with provided parameters, including session ID, database path, and table creation options.

### Method
`__init__`

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **session_id** (str) - Required - The ID of the session
- **db_path** (str | Path) - Optional - The path to the SQLite database file. Defaults to `:memory:` for in-memory storage
- **create_tables** (bool) - Optional - Whether to create the structure tables
- **logger** (Logger | None) - Optional - The logger to use. Defaults to the module logger
- **kwargs** () - Optional - Additional keyword arguments to pass to the superclass

### Request Example
```json
{
  "session_id": "your_session_id",
  "db_path": ":memory:",
  "create_tables": false,
  "logger": null
}
```

### Response
#### Success Response (None)
This method does not return a value.

#### Response Example
None
```

--------------------------------

### Integrate Realtime Agents with SIP Calls in Python

Source: https://openai.github.io/openai-agents-python/realtime/guide

This Python code shows how to integrate realtime agents with phone calls using the Realtime Calls API and `OpenAIRealtimeSIPModel`. It sets up a `RealtimeRunner` with the SIP model and configures call-specific settings like turn detection. The session handles media negotiation over SIP and automatically closes when the caller hangs up.

```python
from agents.realtime import RealtimeAgent, RealtimeRunner
from agents.realtime.openai_realtime import OpenAIRealtimeSIPModel

# Assuming 'agent' is a pre-configured RealtimeAgent instance
agent = RealtimeAgent(name="Assistant", instructions="...") # Example agent

runner = RealtimeRunner(
    starting_agent=agent,
    model=OpenAIRealtimeSIPModel(),
)

# call_id_from_webhook would be received from an incoming call webhook
call_id_from_webhook = "your_call_id_here"

async with await runner.run(
    model_config={
        "call_id": call_id_from_webhook,
        "initial_model_settings": {
            "turn_detection": {"type": "semantic_vad", "interrupt_response": True},
        },
    },
) as session:
    async for event in session:
        # Handle session events
        pass

```

--------------------------------

### OpenAI Responses Compaction Session Initialization

Source: https://openai.github.io/openai-agents-python/ja/ref/memory/openai_responses_compaction_session

Initializes the compaction session with various configuration options for managing OpenAI conversation history.

```APIDOC
## POST /__init__ (OpenAI Responses Compaction Session)

### Description
Initializes the compaction session. This session is used to manage and compact conversation history for OpenAI models, providing options for client, model, compaction strategy, and custom triggering logic.

### Method
POST

### Endpoint
/__init__

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **session_id** (str) - Required - Identifier for this session.
- **underlying_session** (Session) - Required - Session store that holds the compacted history. Cannot be OpenAIConversationsSession.
- **client** (AsyncOpenAI | None) - Optional - OpenAI client for responses.compact API calls. Defaults to get_default_openai_client() or new AsyncOpenAI().
- **model** (str) - Optional - Model to use for responses.compact. Defaults to "gpt-4.1". Must be an OpenAI model name (gpt-*, o*, or ft:gpt-*).
- **compaction_mode** (OpenAIResponsesCompactionMode) - Optional - Controls how the compaction request provides conversation history. "auto" (default) uses input when the last response was not stored or no response_id is available.
- **should_trigger_compaction** (Callable[[dict[str, Any]], bool] | None) - Optional - Custom decision hook. Defaults to triggering when 10+ compaction candidates exist.

### Request Example
```json
{
  "session_id": "example_session_id",
  "underlying_session": { /* Session object */ },
  "client": null, // or an AsyncOpenAI client instance
  "model": "gpt-4.1",
  "compaction_mode": "auto",
  "should_trigger_compaction": null // or a callable function
}
```

### Response
#### Success Response (200)
This method initializes the session and does not return a specific value, but rather sets up the internal state of the `OpenAIResponsesCompactionSession` object.

#### Response Example
(No explicit response body for initialization, object state is modified.)
```

--------------------------------

### Get Output Type Name - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/agent_output

Retrieves the string representation of the output type. This function is useful for debugging or logging purposes, providing a human-readable name for the expected output format.

```python
def name(self) -> str:
    """The name of the output type."""
    return _type_to_str(self.output_type)
```

--------------------------------

### Check if GPT-5 Reasoning Settings are Required (Python)

Source: https://openai.github.io/openai-agents-python/ko/ref/models/default_models

Determines if a given model name corresponds to a GPT-5 model that requires specific reasoning settings. It checks if the model name starts with 'gpt-5' but excludes 'gpt-5-chat-latest'.

```python
def gpt_5_reasoning_settings_required(model_name: str) -> bool:
    """
    Returns True if the model name is a GPT-5 model and reasoning settings are required.
    """
    if model_name.startswith("gpt-5-chat"):
        # gpt-5-chat-latest does not require reasoning settings
        return False
    # matches any of gpt-5 models
    return model_name.startswith("gpt-5")
```

--------------------------------

### RealtimeSession Initialization API

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/session

Initializes a new RealtimeSession with the specified model, agent, and context. Optional configurations for the model and runtime can also be provided.

```APIDOC
## __init__ RealtimeSession

### Description
Initializes the session with a model, agent, and context. Optional model and run configurations can be provided.

### Method
__init__

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (`RealtimeModel`) - Required - The model to use.
- **agent** (`RealtimeAgent`) - Required - The current agent.
- **context** (`TContext | None`) - Required - The context object.
- **model_config** (`RealtimeModelConfig | None`) - Optional - Model configuration. Defaults to None.
- **run_config** (`RealtimeRunConfig | None`) - Optional - Runtime configuration including guardrails. Defaults to None.

### Request Example
```python
# This is a constructor, not a typical request example.
# Initialization requires object instances:
# session = RealtimeSession(model=my_model, agent=my_agent, context=my_context)
```

### Response
#### Success Response (None)
This is a constructor, no return value.

#### Response Example
None
```

--------------------------------

### POST /connect

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/model

Establishes a connection to the realtime model. This method should be called before sending any events or adding listeners.

```APIDOC
## POST /connect

### Description
Establish a connection to the model and keep it alive.

### Method
POST

### Endpoint
/connect

#### Parameters

##### Request Body
- **options** (RealtimeModelConfig) - Required - Configuration options for the realtime model connection.
```

--------------------------------

### RealtimeSession enter Method

Source: https://openai.github.io/openai-agents-python/zh/ref/realtime/session

Provides a non-context manager way to enter the session, requiring manual closing.

```APIDOC
## enter RealtimeSession

### Description
Manually enters the session's asynchronous context. It's recommended to use the `async with` statement instead. If this method is used, `close()` must be called manually to ensure proper session termination.

### Method
enter (async)

### Endpoint
N/A (Instance method)

### Parameters
None

### Request Example
```python
session = RealtimeSession(model=my_model, agent=my_agent, context=my_context)
await session.enter()
try:
    # Use the session here
    await session.send_message("Hello")
finally:
    await session.close() # Manual closing is required
```

### Response
#### Success Response (200)
- **enter**: Returns the `RealtimeSession` instance.

#### Response Example
```json
{
  "message": "Session entered successfully."
}
```
```

--------------------------------

### Create Custom Function Tools with OpenAI Agents SDK

Source: https://openai.github.io/openai-agents-python/tools

Illustrates how to manually create a `FunctionTool` instance when direct Python function integration is not desired. This method requires explicit definition of the tool's name, description, parameter schema using Pydantic, and an asynchronous invocation function (`on_invoke_tool`).

```python
from typing import Any

from pydantic import BaseModel

from agents import RunContextWrapper, FunctionTool


def do_some_work(data: str) -> str:
    return "done"


class FunctionArgs(BaseModel):
    username: str
    age: int


async def run_function(ctx: RunContextWrapper[Any], args: str) -> str:
    parsed = FunctionArgs.model_validate_json(args)
    return do_some_work(data=f"{parsed.username} is {parsed.age} years old")


tool = FunctionTool(
    name="process_user",
    description="Processes extracted user data",
    params_json_schema=FunctionArgs.model_json_schema(),
    on_invoke_tool=run_function,
)

```

--------------------------------

### Run Response Compaction - Python

Source: https://openai.github.io/openai-agents-python/ja/ref/memory/openai_responses_compaction_session

Executes the response compaction process. It determines the compaction mode, checks if compaction should be triggered based on force or decision hooks, and then calls the OpenAI client's `responses.compact` API. The output is processed and added back to the session.

```python
async def run_compaction(self, args: OpenAIResponsesCompactionArgs | None = None) -> None:
        """Run compaction using responses.compact API."""
        if args and args.get("response_id"):
            self._response_id = args["response_id"]
        requested_mode = args.get("compaction_mode") if args else None
        if args and "store" in args:
            store = args["store"]
            if store is False and self._response_id:
                self._last_unstored_response_id = self._response_id
            elif store is True and self._response_id == self._last_unstored_response_id:
                self._last_unstored_response_id = None
        else:
            store = None
        resolved_mode = self._resolve_compaction_mode_for_response(
            response_id=self._response_id,
            store=store,
            requested_mode=requested_mode,
        )

        if resolved_mode == "previous_response_id" and not self._response_id:
            raise ValueError(
                "OpenAIResponsesCompactionSession.run_compaction requires a response_id "
                "when using previous_response_id compaction."
            )

        compaction_candidate_items, session_items = await self._ensure_compaction_candidates()

        force = args.get("force", False) if args else False
        should_compact = force or self.should_trigger_compaction(
            {
                "response_id": self._response_id,
                "compaction_mode": resolved_mode,
                "compaction_candidate_items": compaction_candidate_items,
                "session_items": session_items,
            }
        )

        if not should_compact:
            logger.debug(
                f"skip: decision hook declined compaction for {self._response_id} "
                f"(mode={resolved_mode})"
            )
            return

        self._deferred_response_id = None
        logger.debug(
            f"compact: start for {self._response_id} using {self.model} (mode={resolved_mode})"
        )

        compact_kwargs: dict[str, Any] = {"model": self.model}
        if resolved_mode == "previous_response_id":
            compact_kwargs["previous_response_id"] = self._response_id
        else:
            compact_kwargs["input"] = session_items

        compacted = await self.client.responses.compact(**compact_kwargs)

        await self.underlying_session.clear_session()
        output_items: list[TResponseInputItem] = []
        if compacted.output:
            for item in compacted.output:
                if isinstance(item, dict):
                    output_items.append(item)
                else:
                    # Suppress Pydantic literal warnings: responses.compact can return
                    # user-style input_text content inside ResponseOutputMessage.
                    output_items.append(
                        item.model_dump(exclude_unset=True, warnings=False)  # type: ignore
                    )

        if output_items:
            await self.underlying_session.add_items(output_items)

        self._compaction_candidate_items = select_compaction_candidate_items(output_items)
        self._session_items = output_items

        logger.debug(
            f"compact: done for {self._response_id} "
            f"(mode={resolved_mode}, output={len(output_items)}, "
            f"candidates={len(self._compaction_candidate_items)})"
        )

```

--------------------------------

### Get Trace Name - Python

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing

Retrieves the human-readable name of a workflow trace. This name should be descriptive and is used for grouping and filtering traces in the dashboard, helping to identify the trace's purpose.

```python
name: str

# Returns:
# Name | Type | Description
# `str` |  `str` |  The workflow name (e.g., "Customer Service", "Data Processing")
```

--------------------------------

### Get Provider from MultiProviderMap by Prefix (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/models/multi_provider

Implements the `get_provider` method for the MultiProviderMap class. This method retrieves the ModelProvider associated with a given prefix. It takes a string prefix as input and returns either a ModelProvider object or None if the prefix is not found.

```python
def get_provider(self, prefix: str) -> ModelProvider | None:
    """Returns the ModelProvider for the given prefix.

    Args:
        prefix: The prefix of the model name e.g. "openai" or "my_prefix".
    """
    return self._mapping.get(prefix)

```

--------------------------------

### Update Model Settings from Agent Configuration (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/realtime/session

This asynchronous function retrieves and merges model settings from both base configurations and specific agent settings. It fetches system prompts, tools, and handoffs from the agent, applies them to the updated settings, and incorporates any provided starting settings. It also handles the disabling of tracing based on configuration.

```python
    async def _get_updated_model_settings_from_agent(
        self,
        starting_settings: RealtimeSessionModelSettings | None,
        agent: RealtimeAgent,
    ) -> RealtimeSessionModelSettings:
        # Start with the merged base settings from run and model configuration.
        updated_settings = self._base_model_settings.copy()

        if agent.prompt is not None:
            updated_settings["prompt"] = agent.prompt

        instructions, tools, handoffs = await asyncio.gather(
            agent.get_system_prompt(self._context_wrapper),
            agent.get_all_tools(self._context_wrapper),
            self._get_handoffs(agent, self._context_wrapper),
        )
        updated_settings["instructions"] = instructions or ""
        updated_settings["tools"] = tools or []
        updated_settings["handoffs"] = handoffs or []

        # Apply starting settings (from model config) next
        if starting_settings:
            updated_settings.update(starting_settings)

        disable_tracing = self._run_config.get("tracing_disabled", False)
        if disable_tracing:
            updated_settings["tracing"] = None

        return updated_settings

```

--------------------------------

### Get Trace Name in Python

Source: https://openai.github.io/openai-agents-python/zh/ref/tracing/traces

Retrieves the human-readable name for a trace, typically representing the workflow it belongs to. This property is part of the tracing mechanism. For no-operation traces, it returns 'no-op'.

```python
name: str

"""The workflow name for this trace.

Returns:
    str: Human-readable name describing this workflow.
"""
return "no-op"
```

--------------------------------

### Realtime Model Configuration Definition (Python)

Source: https://openai.github.io/openai-agents-python/ko/ref/realtime/config

Defines options for connecting to a realtime model. Includes parameters for API keys, URLs, headers, initial model settings, playback tracking, and call IDs.

```python
class RealtimeModelConfig(TypedDict):
    """Options for connecting to a realtime model."""

    api_key: NotRequired[str | Callable[[], MaybeAwaitable[str]]]
    """The API key (or function that returns a key) to use when connecting. If unset, the model will
try to use a sane default. For example, the OpenAI Realtime model will try to use the
`OPENAI_API_KEY`  environment variable.
"""

    url: NotRequired[str]
    """The URL to use when connecting. If unset, the model will use a sane default. For example,
the OpenAI Realtime model will use the default OpenAI WebSocket URL.
"""

    headers: NotRequired[dict[str, str]]
    """The headers to use when connecting. If unset, the model will use a sane default.
    Note that, when you set this, authorization header won't be set under the hood.
    e.g., {"api-key": "your api key here"} for Azure OpenAI Realtime WebSocket connections.
    """

    initial_model_settings: NotRequired[RealtimeSessionModelSettings]
    """The initial model settings to use when connecting."""

    playback_tracker: NotRequired[RealtimePlaybackTracker]
    """The playback tracker to use when tracking audio playback progress. If not set, the model will
    use a default implementation that assumes audio is played immediately, at realtime speed.

    A playback tracker is useful for interruptions. The model generates audio much faster than
    realtime playback speed. So if there's an interruption, its useful for the model to know how
    much of the audio has been played by the user. In low-latency scenarios, it's fine to assume
    that audio is played back immediately at realtime speed. But in scenarios like phone calls or
    other remote interactions, you can set a playback tracker that lets the model know when audio
    is played to the user.
    """

    call_id: NotRequired[str]
    """Attach to an existing realtime call instead of creating a new session.

    When provided, the transport connects using the `call_id` query string parameter rather than a
    model name. This is used for SIP-originated calls that are accepted via the Realtime Calls API.
    """

```

--------------------------------

### Convert Standard Tools to JSON (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/models/openai_responses

Converts various tool types including FileSearchTool, ComputerTool, and others into a dictionary representation suitable for serialization. It handles specific attributes for each tool type, such as search parameters or computer dimensions. Raises a UserError for unknown tool types.

```python
def _convert_tool(self, tool):
            """
            Convert tool to a JSON serializable format.
            """
            if isinstance(tool, SearchTool):
                converted_tool = {
                    "type": "search",
                    "user_location": tool.user_location,
                    "search_context_size": tool.search_context_size,
                }
                includes = None
            elif isinstance(tool, FileSearchTool):
                converted_tool = {
                    "type": "file_search",
                    "vector_store_ids": tool.vector_store_ids,
                }
                if tool.max_num_results:
                    converted_tool["max_num_results"] = tool.max_num_results
                if tool.ranking_options:
                    converted_tool["ranking_options"] = tool.ranking_options
                if tool.filters:
                    converted_tool["filters"] = tool.filters

                includes = "file_search_call.results" if tool.include_search_results else None
            elif isinstance(tool, ComputerTool):
                computer = tool.computer
                if not isinstance(computer, (Computer, AsyncComputer)):
                    raise UserError(
                        "Computer tool is not initialized for serialization. Call "
                        "resolve_computer({ tool, run_context }) with a run context first "
                        "when building payloads manually."
                    )
                converted_tool = {
                    "type": "computer_use_preview",
                    "environment": computer.environment,
                    "display_width": computer.dimensions[0],
                    "display_height": computer.dimensions[1],
                }
                includes = None
            elif isinstance(tool, HostedMCPTool):
                converted_tool = tool.tool_config
                includes = None
            elif isinstance(tool, ApplyPatchTool):
                converted_tool = cast(ToolParam, {"type": "apply_patch"})
                includes = None
            elif isinstance(tool, ShellTool):
                converted_tool = cast(ToolParam, {"type": "shell"})
                includes = None
            elif isinstance(tool, ImageGenerationTool):
                converted_tool = tool.tool_config
                includes = None
            elif isinstance(tool, CodeInterpreterTool):
                converted_tool = tool.tool_config
                includes = None
            elif isinstance(tool, LocalShellTool):
                converted_tool = {
                    "type": "local_shell",
                }
                includes = None
            else:
                raise UserError(f"Unknown tool type: {type(tool)}, tool")

            return converted_tool, includes
```

--------------------------------

### Configure Playback Tracker for Realtime Audio - Python

Source: https://openai.github.io/openai-agents-python/ko/ref/realtime/config

Defines the 'playback_tracker' attribute for realtime model sessions. This allows custom audio playback tracking, essential for managing interruptions and synchronizing with user playback speed. If not provided, a default assumes immediate playback.

```python
playback_tracker: NotRequired[RealtimePlaybackTracker]

"""
The playback tracker to use when tracking audio playback progress. If not set, the model will use a default implementation that assumes audio is played immediately, at realtime speed.
A playback tracker is useful for interruptions. The model generates audio much faster than realtime playback speed. So if there's an interruption, its useful for the model to know how much of the audio has been played by the user. In low-latency scenarios, it's fine to assume that audio is played back immediately at realtime speed. But in scenarios like phone calls or other remote interactions, you can set a playback tracker that lets the model know when audio is played to the user.
"""
```

--------------------------------

### Get Speech-to-Text Model (Python)

Source: https://openai.github.io/openai-agents-python/ja/ref/voice/model

The `get_stt_model` method retrieves a speech-to-text model based on its name. This is part of the `VoiceModelProvider` interface, allowing implementations to provide specific STT models.

```python
import abc

# Assume STTModel and VoiceModelProvider are defined
class STTModel:
    pass

class VoiceModelProvider(abc.ABC):
    @abc.abstractmethod
    def get_stt_model(self, model_name: str | None) -> STTModel:
        """Get a speech-to-text model by name.

        Args:
            model_name: The name of the model to get.

        Returns:
            The speech-to-text model.
        """
        pass
```

--------------------------------

### Get Turn Usage Statistics with Token Details - Python

Source: https://openai.github.io/openai-agents-python/ko/ref/extensions/memory/advanced_sqlite_session

Fetches detailed usage statistics for specific turns within a session and branch. It parses JSON data for token details and handles cases where a specific turn number is requested or all turns are returned. Includes error handling for JSON parsing.

```python
        if branch_id is None:
            branch_id = self._current_branch_id

        def _get_turn_usage_sync():
            """Synchronous helper to get turn usage statistics."""
            conn = self._get_connection()

            if user_turn_number is not None:
                query = """
                    SELECT requests, input_tokens, output_tokens, total_tokens,
                           input_tokens_details, output_tokens_details
                    FROM turn_usage
                    WHERE session_id = ? AND branch_id = ? AND user_turn_number = ?
                """

                with closing(conn.cursor()) as cursor:
                    cursor.execute(query, (self.session_id, branch_id, user_turn_number))
                    row = cursor.fetchone()

                    if row:
                        # Parse JSON details if present
                        input_details = None
                        output_details = None

                        if row[4]:  # input_tokens_details
                            try:
                                input_details = json.loads(row[4])
                            except json.JSONDecodeError:
                                pass

                        if row[5]:  # output_tokens_details
                            try:
                                output_details = json.loads(row[5])
                            except json.JSONDecodeError:
                                pass

                        return {
                            "requests": row[0],
                            "input_tokens": row[1],
                            "output_tokens": row[2],
                            "total_tokens": row[3],
                            "input_tokens_details": input_details,
                            "output_tokens_details": output_details,
                        }
                    return {}
            else:
                query = """
                    SELECT user_turn_number, requests, input_tokens, output_tokens,
                           total_tokens, input_tokens_details, output_tokens_details
                    FROM turn_usage
                    WHERE session_id = ? AND branch_id = ?
                    ORDER BY user_turn_number
                """

                with closing(conn.cursor()) as cursor:
                    cursor.execute(query, (self.session_id, branch_id))
```

--------------------------------

### Tracer Initialization (`__init__`)

Source: https://openai.github.io/openai-agents-python/ja/ref/tracing/processors

Initializes the tracer with API credentials, endpoint, and retry configurations. It sets up an httpx client for making requests to the trace ingestion endpoint.

```APIDOC
## POST /v1/traces/ingest (Implicit)

### Description
Initializes the tracer with API credentials, endpoint, and retry configurations. It sets up an httpx client for making requests to the trace ingestion endpoint.

### Method
POST (Implicit, used by the internal client)

### Endpoint
`https://api.openai.com/v1/traces/ingest` (default)

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
None (This is the constructor, not an endpoint call)

### Initialization Parameters
- **api_key** (`str | None`) - Required/Optional - The API key for the "Authorization" header. Defaults to `os.environ["OPENAI_API_KEY"]` if not provided.
- **organization** (`str | None`) - Required/Optional - The OpenAI organization to use. Defaults to `os.environ["OPENAI_ORG_ID"]` if not provided.
- **project** (`str | None`) - Required/Optional - The OpenAI project to use. Defaults to `os.environ["OPENAI_PROJECT_ID"]` if not provided.
- **endpoint** (`str`) - Required - The HTTP endpoint to which traces/spans are posted. Defaults to `'https://api.openai.com/v1/traces/ingest'`.
- **max_retries** (`int`) - Required - Maximum number of retries upon failures. Defaults to `3`.
- **base_delay** (`float`) - Required - Base delay (in seconds) for the first backoff. Defaults to `1.0`.
- **max_delay** (`float`) - Required - Maximum delay (in seconds) for backoff growth. Defaults to `30.0`.

### Request Example
```python
from agents.tracing.processors import Tracer

tracer = Tracer(api_key="YOUR_API_KEY", organization="YOUR_ORG_ID")
```

### Response
This is a constructor, no direct response.
```

--------------------------------

### Get Text-to-Speech Model (Python)

Source: https://openai.github.io/openai-agents-python/zh/ref/voice/model

Retrieves a text-to-speech (TTS) model by its name. This is an abstract method that concrete implementations of VoiceModelProvider must define. It takes an optional model name and returns a TTSModel object.

```python
import abc

# Assuming TTSModel is defined elsewhere

class VoiceModelProvider(abc.ABC):
    @abc.abstractmethod
    def get_tts_model(self, model_name: str | None) -> TTSModel:
        """Get a text-to-speech model by name."""
        pass
```