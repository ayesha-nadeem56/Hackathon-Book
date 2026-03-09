# Research: Module 4 — Vision-Language-Action (VLA)

**Branch**: `004-module4-vla` | **Date**: 2026-03-09
**Phase**: 0 — Research & Unknowns Resolution

All unknowns from Technical Context resolved below.

---

## Decision 1: Whisper Model Architecture and Sizes

**Decision**: Present Whisper as a transformer-based encoder-decoder ASR model available in five sizes: tiny (39M parameters), base (74M), small (244M), medium (769M), and large (1550M).

**Rationale**: The five-size progression from tiny to large provides a clear trade-off story that is directly applicable to robotics — small robots with limited compute use tiny/base; cloud-connected systems use large. This is the most pedagogically useful framing for students choosing a model for their own project.

**Alternatives considered**: Show only two sizes (tiny and large). Rejected — the five-size table matches the actual Whisper API options and gives students a complete reference they can act on.

**Resolved model sizes table**:

| Size | Parameters | Relative Speed | Recommended Use Case |
|---|---|---|---|
| tiny | 39M | Fastest | Edge devices, low-power robots, development testing |
| base | 74M | Fast | Embedded systems, resource-constrained robots |
| small | 244M | Moderate | General robotics; good accuracy/speed balance |
| medium | 769M | Slow | High-accuracy scenarios; cloud or workstation |
| large | 1550M | Slowest | Maximum accuracy; offline or cloud inference |

---

## Decision 2: Whisper Python API Pattern

**Decision**: Show Whisper transcription using `whisper.load_model()` to load the model and `model.transcribe()` to process a WAV file. Use `sounddevice` for audio capture in the VoiceNode example.

**Rationale**: This is the standard `openai-whisper` package API. The batch (non-streaming) pattern is simpler and appropriate for a student audience. Streaming Whisper adds real-time chunking complexity that is out of scope.

**Resolved code pattern**:
```python
import whisper
import sounddevice as sd
import numpy as np

model = whisper.load_model("base")
audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype="float32")
sd.wait()
result = model.transcribe(audio.flatten())
text = result["text"].strip()
```

---

## Decision 3: ROS 2 Voice Integration Pattern

**Decision**: VoiceNode is a ROS 2 node that publishes the Whisper transcription as `std_msgs/String` on the `/voice_command` topic. The LLM planner subscribes to this topic.

**Rationale**: `std_msgs/String` is the simplest message type for text; it requires no custom message definition and is universally available in all ROS 2 distributions. Using a topic (not a service) allows multiple nodes to consume the voice command simultaneously.

**Resolved ROS 2 interface**:
- Publisher topic: `/voice_command` (`std_msgs/String`)
- Message field: `data` (the transcribed text string)

---

## Decision 4: LLM System Prompt Structure

**Decision**: Use a 4-part system prompt structure: ROLE, VOCABULARY, FORMAT, SAFETY.

**Rationale**: This structure separates concerns cleanly — ROLE defines who the model is pretending to be (constraining hallucination of non-robot behaviors), VOCABULARY gives the explicit action list, FORMAT enforces structured JSON output, SAFETY adds the explicit prohibition on inventing new actions. Students can use this template for any new robot task by changing the vocabulary.

**Resolved system prompt template**:
```text
ROLE: You are a robot action planner. Convert the user's natural language command
into a sequence of robot actions. Only use actions from the vocabulary below.

VOCABULARY:
- navigate_to(target)
- pick_up(object)
- place_on(surface)
- push(object)
- open_door(door)
- close_door(door)
- wait(seconds)

FORMAT: Respond with a JSON array only. No explanation. No markdown. Example:
[{"action": "navigate_to", "target": "red_cube"},
 {"action": "pick_up", "object": "red_cube"}]

SAFETY: Do not invent actions. If the command cannot be completed with the
vocabulary above, respond with: [{"action": "wait", "seconds": 0}]
```

---

## Decision 5: 7-Action Vocabulary

**Decision**: The robot's allowed action vocabulary is exactly 7 actions: navigate_to, pick_up, place_on, push, open_door, close_door, wait.

**Rationale**: 7 actions covers the most common mobile manipulation tasks (locomotion, manipulation, interaction, fallback) without overwhelming students. The `wait` action serves as the safe fallback for commands the robot cannot execute. This small vocabulary also makes the Python validation code clean and teachable.

**Resolved vocabulary table**:

| Action | Parameters | Purpose |
|---|---|---|
| navigate_to | target (location name) | Move the robot base to a named location |
| pick_up | object (object name) | Grasp and lift a named object |
| place_on | object, surface | Place a held object on a named surface |
| push | object | Push an object with the robot's arm |
| open_door | door | Open a named door |
| close_door | door | Close a named door |
| wait | seconds | Pause execution for a duration |

---

## Decision 6: Python Action Parser and Guardrail

**Decision**: Use `json.loads()` to parse LLM output, then validate each action against a `VALID_ACTIONS` set. Raise `ValueError` on any invalid action; log and halt before any ROS 2 call is made.

**Rationale**: The guardrail must be at the parser level — before any ROS 2 action is dispatched — to ensure that no invalid action reaches the hardware. Using a Python set for `VALID_ACTIONS` is O(1) lookup and requires no additional dependencies.

**Resolved parser pattern**:
```python
import json

VALID_ACTIONS = {
    "navigate_to", "pick_up", "place_on",
    "push", "open_door", "close_door", "wait"
}

def parse_action_plan(llm_response):
    actions = json.loads(llm_response)
    for step in actions:
        action = step.get("action", "")
        if action not in VALID_ACTIONS:
            raise ValueError("Invalid action: " + action)
    return actions
```

---

## Decision 7: Capstone Scenario and 10-Step Trace

**Decision**: Use "Pick up the red cube" as the end-to-end capstone scenario. Trace it in a 10-step table (Step / Component / Module / Input / Output).

**Rationale**: "Pick up the red cube" is the canonical VLA demo scenario — it requires locomotion (Nav2), perception (Isaac ROS cuVSLAM + object detection), and manipulation (arm controller). It exercises all four modules and is concrete enough to trace step by step.

**Resolved 10-step trace**:

| Step | Component | Module | Input | Output |
|---|---|---|---|---|
| 1 | Microphone | Hardware | Spoken: "Pick up the red cube" | Raw audio PCM |
| 2 | Whisper ASR | Module 4 Ch1 | Raw audio PCM | Text: "Pick up the red cube" |
| 3 | VoiceNode | Module 4 Ch1 | Text string | /voice_command (std_msgs/String) |
| 4 | LLM Planner | Module 4 Ch2 | /voice_command text | JSON action plan |
| 5 | Guardrail Parser | Module 4 Ch2 | JSON action plan | Validated action list |
| 6 | Nav2 | Module 3 Ch3 | navigate_to(red_cube_area) | /cmd_vel velocity commands |
| 7 | Isaac ROS cuVSLAM | Module 3 Ch2 | /camera/image_raw | /odom pose estimate |
| 8 | Isaac ROS ObjectDetection | Module 3 Ch2 | /camera/image_raw | /detections (cube location) |
| 9 | Arm Controller | Module 1 | pick_up(red_cube) + /detections | Joint trajectory commands |
| 10 | Robot Hardware | Module 1 | Joint trajectory | Physical cube pickup |

---

## MDX / Windows Constraints (applied to this module)

- ASCII-only in all fenced code blocks (no em-dashes, curly quotes, unicode)
- No bare XML angle brackets in prose or table cells
- System prompt block: use ` ```text ``` ` (not ` ```json ``` `) to prevent MDX from parsing curly braces as JSX
- Python f-strings: only show in fenced blocks; never put `{variable}` in inline prose
- Relative links use `.md` extension
- Mermaid node IDs: camelCase or underscores, maximum 8 nodes per diagram
