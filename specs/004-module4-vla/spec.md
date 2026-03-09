# Feature Specification: Module 4 — Vision-Language-Action (VLA)

**Feature Branch**: `004-module4-vla`
**Created**: 2026-03-09
**Status**: Draft
**Input**: Create a Docusaurus module covering the complete Vision-Language-Action pipeline — OpenAI Whisper for voice input (Chapter 1), LLM cognitive planning with structured output and hallucination guardrail (Chapter 2), and an end-to-end capstone integrating all four modules with the "Pick up the red cube" scenario (Chapter 3).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Understand Voice Input with Whisper ASR (Priority: P1)

A robotics student reads Chapter 1 and understands how OpenAI Whisper converts spoken voice commands into text that a robot can process — including the five model size trade-offs and how the transcribed text is published on a ROS 2 topic.

**Why this priority**: Voice input is the entry point of the VLA pipeline. Students must understand how speech becomes text before they can understand how the LLM plans actions from that text (Chapter 2).

**Independent Test**: Chapter 1 can be read alone. A student should answer: "What does Whisper output?", "Name two Whisper model sizes and their trade-off", "What ROS 2 message type carries a transcribed command?"

**Acceptance Scenarios**:

1. **Given** a student reads Chapter 1, **When** asked what Whisper outputs, **Then** they say it outputs a text transcription of the spoken audio — a string that the downstream LLM planner will use as input.
2. **Given** a student reads the model sizes table, **When** asked to choose a model for a resource-constrained robot, **Then** they explain the trade-off between model size (tiny/base = fast, low accuracy; medium/large = slow, high accuracy).
3. **Given** a student reads the ROS 2 integration section, **When** asked what message type carries the transcription, **Then** they say `std_msgs/String` published on `/voice_command`.

---

### User Story 2 — Understand LLM Cognitive Planning (Priority: P2)

A robotics student reads Chapter 2 and understands how a Large Language Model acts as a cognitive planner — receiving a transcribed voice command, reasoning about it using a structured system prompt, and producing a validated JSON action plan that can be safely executed by a robot.

**Why this priority**: P2 because the LLM planner bridges the gap between natural language (from Whisper) and structured robot actions (sent to Nav2 and Isaac ROS). The hallucination guardrail is the critical safety mechanism that makes LLM-driven robots viable.

**Independent Test**: A student should explain: "Why can't raw LLM output directly drive a robot?", "What is a system prompt?", "What does structured output mean in this context?"

**Acceptance Scenarios**:

1. **Given** a student reads Chapter 2, **When** asked why raw LLM output cannot directly drive a robot, **Then** they explain that LLMs may generate actions outside the robot's capability set (hallucinations); the system prompt constrains output to a defined vocabulary, and the Python parser validates that every action is in the allowed list before execution.
2. **Given** a student reads the system prompt section, **When** asked what the four parts of the system prompt are, **Then** they name: ROLE (defines the robot's identity), VOCABULARY (lists the 7 allowed actions), FORMAT (requires JSON array output), SAFETY (forbids actions outside the vocabulary).
3. **Given** a student reads the hallucination guardrail section, **When** asked what happens when the LLM outputs an invalid action, **Then** they describe the parser raising a ValueError, the guardrail catching it, and the system requesting a replanned output or halting safely.

---

### User Story 3 — Understand the End-to-End VLA Capstone (Priority: P3)

A robotics student reads Chapter 3 and can trace the complete "Pick up the red cube" scenario step by step — from spoken voice command through Whisper ASR, LLM planning, Nav2 navigation, Isaac ROS perception, and arm controller execution — identifying which module handles each step.

**Why this priority**: P3 because the capstone synthesizes all four modules. It is the payoff chapter that makes the entire book coherent — showing students how every module they have learned connects into a single working system.

**Independent Test**: A student should trace: voice command → Whisper → `/voice_command` → LLM → JSON action plan → ROS 2 actions → Nav2 + Isaac ROS + arm controller → physical execution.

**Acceptance Scenarios**:

1. **Given** a student reads Chapter 3, **When** asked to identify the module responsible for pose estimation, **Then** they say Isaac ROS (cuVSLAM, Module 3, Chapter 2).
2. **Given** a student reads the 10-step trace table, **When** asked which component generates the JSON action plan, **Then** they say the LLM Planner (Module 4, Chapter 2), and they can name the input (transcribed text) and output (JSON array of actions).
3. **Given** a student completes Chapter 3, **When** asked what happens if the LLM generates "fly to cube", **Then** they describe the hallucination guardrail catching the invalid action, logging a safety rejection, and halting execution before any robot motion occurs.

---

### Edge Cases

- A student arrives at Chapter 2 without reading Chapter 1: prerequisite admonition must explain that the LLM receives its input as text from Whisper — the transcription is the LLM's only input.
- A student arrives at Chapter 3 without Module 3 (Isaac Brain): prerequisite admonition must link to Module 3 and explain that cuVSLAM provides the pose estimate the capstone depends on.
- LLM hallucination: the guardrail is not optional — Chapter 2 must make clear that no action reaches the robot hardware without passing the vocabulary validation check.
- Python code blocks: all code examples must be ASCII-only; no f-strings with curly braces in inline prose (MDX v3 JSX parsing rule).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The module MUST be structured as a Docusaurus category under `book/docs/module-4-vla/` with `_category_.json`, `index.md`, and three chapter files.
- **FR-002**: Each chapter MUST include a Learning Objectives section with exactly 4 bullet-point objectives.
- **FR-003**: Chapter 1 MUST explain Whisper ASR, include a 5-row model sizes table, a Python transcription code block, and a ROS 2 publisher snippet showing how the transcription is published on `/voice_command`.
- **FR-004**: Chapter 1 MUST include at least one Mermaid diagram showing the audio-to-text pipeline.
- **FR-005**: Chapter 2 MUST explain LLM cognitive planning, include a 7-action vocabulary table, a system prompt fenced block (text tag, ASCII-only), a structured JSON output example, and a Python action parser with vocabulary validation.
- **FR-006**: Chapter 2 MUST include a hallucination guardrail section explaining what happens when the LLM produces an invalid action, and at least two Mermaid diagrams.
- **FR-007**: Chapter 2 MUST include a Python parser that validates LLM output against the 7-action vocabulary and raises an error (or falls back) for any invalid action.
- **FR-008**: Chapter 3 MUST include a complete VLA architecture Mermaid diagram, a 10-step capstone trace table (columns: Step / Component / Module / Input / Output), and a module contribution map table.
- **FR-009**: Chapter 3 MUST include a sequence diagram showing all four modules interacting during the "Pick up the red cube" scenario.
- **FR-010**: All chapters MUST include prerequisite admonitions with links to prior chapters and modules.
- **FR-011**: All code and configuration examples MUST be ASCII-only.
- **FR-012**: No bare XML angle brackets in prose or table cells (MDX v3 rule).
- **FR-013**: The module MUST pass `npm run build` with zero errors and zero broken links.
- **FR-014**: Each chapter MUST end with a Summary table of at least 6 key concepts (Chapter 1) or 7 key concepts (Chapters 2 and 3).

### Key Entities

- **Whisper**: OpenAI's automatic speech recognition (ASR) model; converts audio to text; available in 5 sizes (tiny, base, small, medium, large).
- **VoiceNode**: The ROS 2 node that captures audio, runs Whisper transcription, and publishes the result on `/voice_command` as `std_msgs/String`.
- **LLM Planner**: A Large Language Model configured with a structured system prompt that converts natural language commands into JSON-formatted robot action plans.
- **System Prompt**: A structured instruction block passed to the LLM that defines the robot's role, allowed action vocabulary, required output format, and safety constraints.
- **Action Vocabulary**: The 7 allowed robot actions: navigate_to, pick_up, place_on, push, open_door, close_door, wait.
- **Hallucination Guardrail**: A Python validation layer that checks every LLM-generated action against the allowed vocabulary and halts execution on any invalid action.
- **VLA Capstone**: The end-to-end scenario ("Pick up the red cube") tracing a single voice command through all four modules to physical robot execution.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A student who completes all three chapters can trace the full VLA pipeline: voice command → Whisper ASR → LLM planner → validated JSON → ROS 2 actions → Nav2 + Isaac ROS → physical execution.
- **SC-002**: The Docusaurus build completes with zero errors and zero broken links when `npm run build` is run.
- **SC-003**: Each chapter contains: Learning Objectives (4), at least one Mermaid diagram, at least one fenced code block, and a Summary table (at least 6 rows).
- **SC-004**: A student reading Chapter 2 can write a basic system prompt skeleton (ROLE / VOCABULARY / FORMAT / SAFETY structure) without referring back to the text.
- **SC-005**: A student reading Chapter 3 can identify, for each of the 10 steps in the capstone trace, which module is responsible and what its input and output are.

---

## Assumptions

- Students have completed Modules 1, 2, and 3 before this module.
- Whisper is used in batch (non-streaming) mode; streaming ASR adds complexity beyond this module's scope.
- The LLM is a generic instruction-following model (GPT-4-class); no specific provider API is shown — the system prompt and JSON output pattern work with any compliant model.
- All code examples use ASCII-only characters (Windows cp1252 encoding safety).
- MDX v3 parsing rules apply: no bare XML angle brackets; no Python f-strings with curly braces in prose context.
- Relative links use `.md` extension in category index pages.

---

## Out of Scope

- Streaming ASR or real-time Whisper transcription pipelines
- LLM fine-tuning or model training for robotics
- Specific LLM provider API integration (OpenAI API calls, authentication)
- Behavior tree authoring or Nav2 behavior tree customization
- Multi-modal input (vision + language combined input to the LLM)
- Arm controller hardware programming or inverse kinematics
- Module 5 or later content
