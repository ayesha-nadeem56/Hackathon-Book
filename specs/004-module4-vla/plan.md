# Implementation Plan: Module 4 — Vision-Language-Action (VLA)

**Branch**: `004-module4-vla` | **Date**: 2026-03-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-module4-vla/spec.md`

---

## Summary

Extend the Docusaurus book with a fourth module (`book/docs/module-4-vla/`) covering the Vision-Language-Action pipeline for humanoid robots. The module comprises a module index page, a `_category_.json` sidebar descriptor, and three chapter files in MDX-compatible Markdown. Chapter 1 covers OpenAI Whisper ASR; Chapter 2 covers LLM cognitive planning with a structured system prompt, 7-action vocabulary, Python parser, and hallucination guardrail; Chapter 3 is an end-to-end capstone integrating all four modules via the "Pick up the red cube" scenario. All content is conceptual; chapters include Mermaid diagrams, Python/bash/YAML configuration examples in ASCII-only fenced blocks, prerequisite admonitions, and summary tables. The Docusaurus build must pass with zero errors and zero broken links.

---

## Technical Context

**Language/Version**: MDX v3 (Docusaurus 3.9.2)
**Primary Dependencies**: Docusaurus 3.9.2 (already scaffolded in `book/`); Mermaid plugin (already configured)
**Storage**: N/A — static file generation only
**Testing**: `npm run build` in `book/` (zero errors, zero broken links)
**Target Platform**: GitHub Pages; authoring on Windows 10 / OneDrive
**Project Type**: Documentation module (Docusaurus category)
**Constraints**:
  - ASCII-only characters in all fenced code/config blocks (Windows cp1252 safe)
  - No bare XML angle brackets in prose or table cells (MDX v3 JSX parser)
  - Relative links between chapters use `.md` extension
  - Module category `position: 4` (follows Module 3 at position 3)
  - Mermaid diagrams: maximum 8 nodes; camelCase/underscore node IDs only
  - System prompt block: use ` ```text ``` ` tag (not ` ```json ``` `) to avoid MDX curly-brace interpretation
  - Python f-strings with curly braces must not appear in prose context (MDX v3 JSX conflict)
**Scale/Scope**: 5 files — 1 `_category_.json`, 1 `index.md`, 3 chapter `.md` files

---

## Constitution Check

| Gate | Status | Evidence |
|---|---|---|
| I. Accuracy & Technical Correctness | PASS | Whisper model sizes verified; cuVSLAM/Nav2 pipeline from Module 3 research; LLM structured output pattern is standard practice |
| II. Clarity & Readability | PASS | Each chapter has 4 Learning Objectives, defined terms on first use, prerequisite admonitions, summary table |
| III. Reproducibility of Workflows | PASS | Code examples are ASCII-only; batch Whisper mode; no installation required; conceptual-only |
| IV. Modularity & Architecture | PASS | Module is a self-contained Docusaurus category at position 4; no changes to Modules 1-3 |
| V. Transparency in AI Content | PASS | Chapter 2 explicitly discusses LLM hallucination as a known risk and shows the guardrail mitigation |

No violations.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-module4-vla/
├── plan.md              # This file
├── research.md          # Phase 0 -- all unknowns resolved
├── data-model.md        # Phase 1 -- content structure schema
├── quickstart.md        # Phase 1 -- development workflow
├── tasks.md             # Phase 2 output (/sp.tasks -- NOT created here)
├── checklists/
│   └── requirements.md  # Spec quality checklist (16/16 PASS)
└── contracts/
    └── chapter-content-contract.md  # Phase 1 -- chapter structure contract
```

### Source Code (repository)

```text
book/docs/module-4-vla/
├── _category_.json            # Sidebar label, position 4, collapsible
├── index.md                   # Module landing page with chapter overview
├── chapter-1-whisper.md       # Whisper ASR + Python transcription + ROS 2 publisher
├── chapter-2-llm-planner.md   # LLM planning + system prompt + JSON + parser + guardrail
└── chapter-3-capstone.md      # End-to-end VLA capstone with 10-step trace
```

---

## Phase 0: Research

See [research.md](./research.md) for full findings. Summary:

| Unknown | Resolution |
|---|---|
| Whisper model sizes | 5 sizes: tiny (39M), base (74M), small (244M), medium (769M), large (1550M) |
| Whisper Python API | `whisper.load_model()` + `model.transcribe()` returns dict with `text` key |
| ROS 2 voice integration | VoiceNode publishes `std_msgs/String` on `/voice_command` |
| LLM system prompt structure | 4 parts: ROLE, VOCABULARY, FORMAT, SAFETY |
| 7-action vocabulary | navigate_to, pick_up, place_on, push, open_door, close_door, wait |
| JSON structured output | Array of action objects: `[{"action": "navigate_to", "target": "red_cube"}]` |
| Python action parser | `json.loads()` + `VALID_ACTIONS` set + ValueError on invalid action |
| Hallucination guardrail | Vocabulary check before any ROS 2 action is dispatched |
| Capstone scenario | "Pick up the red cube" — 10 steps across 4 modules |

---

## Phase 1: Design

### Content Architecture per Chapter

#### `_category_.json`

```json
{
  "label": "Module 4: Vision-Language-Action",
  "position": 4,
  "collapsible": true,
  "collapsed": false,
  "description": "Voice commands, LLM planning, and autonomous action for humanoid robots"
}
```

#### `index.md` — Module Landing Page

Front-matter: `id: module-4-overview`, `sidebar_position: 0`

Sections:
1. Opening narrative — the VLA concept: a robot that listens, understands, and acts
2. Prerequisites admonition — Modules 1, 2, and 3
3. Chapter overview table (3 rows: chapter / tool / role)
4. Module Learning Outcomes (5 items)
5. CTA link: `[Chapter 1 — Voice Input with Whisper →](./chapter-1-whisper.md)`

#### `chapter-1-whisper.md` — Voice Input with Whisper

Front-matter: `id: chapter-1-whisper`, `sidebar_position: 1`

Sections:
1. **What is ASR?** — audio-to-text conversion; why robots need voice input
2. **OpenAI Whisper** — transformer-based; multilingual; 5 model sizes
3. **Model Sizes Table** — 5 rows (tiny/base/small/medium/large): parameters, speed, use case
4. **Python Transcription** — `whisper.load_model()` + `sd.rec()` + `model.transcribe()` code block (ASCII-only)
5. **ROS 2 Integration** — VoiceNode publishes `std_msgs/String` on `/voice_command`; snippet
6. **Mermaid pipeline** — microphone → AudioCapture → Whisper → VoiceNode → /voice_command → LLMPlanner (7 nodes)
7. **Summary table** — 6 rows (ASR, Whisper, Transcription, Model Size, VoiceNode, /voice_command)

#### `chapter-2-llm-planner.md` — LLM Cognitive Planning

Front-matter: `id: chapter-2-llm-planner`, `sidebar_position: 2`

Sections:
1. **The Planning Problem** — why natural language cannot directly drive motors
2. **LLMs as Planners** — instruction-following models; system prompt as constraint
3. **Action Vocabulary Table** — 7 rows (navigate_to, pick_up, place_on, push, open_door, close_door, wait)
4. **System Prompt Block** — 4-part template in ```text``` block (ROLE / VOCABULARY / FORMAT / SAFETY)
5. **JSON Structured Output** — example response array; why JSON enables validation
6. **Python Action Parser** — `json.loads()` + `VALID_ACTIONS` set + ValueError on invalid
7. **Hallucination Guardrail** — what happens when LLM outputs invalid action
8. **ROS 2 Action Translation** — mapping JSON action objects to ROS 2 action calls
9. **Mermaid diagram 1** — LLM planning pipeline (VoiceCommand → LLM → JSONOutput → Parser → ROS2Actions)
10. **Mermaid diagram 2** — guardrail flow (Parser → valid/invalid branch → execute/halt)
11. **Summary table** — 7 rows (LLM Planner, System Prompt, Action Vocabulary, Structured Output, Action Parser, Hallucination, Guardrail)

#### `chapter-3-capstone.md` — End-to-End VLA Capstone

Front-matter: `id: chapter-3-capstone`, `sidebar_position: 3`

Sections:
1. **The Complete VLA System** — all 4 modules working together
2. **Mermaid diagram 1** — full VLA architecture with subgraph grouping
3. **10-Step Capstone Trace Table** — columns: Step / Component / Module / Input / Output
4. **Mermaid diagram 2** — sequence diagram (7 participants: User, Whisper, LLM, Guardrail, Nav2, IsaacROS, ArmController)
5. **Module Contribution Map** — table: module / role / key output
6. **Guardrail in Action** — "fly to cube" rejection scenario
7. **Summary table** — 7 rows (VLA, Whisper, LLM Planner, Guardrail, Nav2, Isaac ROS, Action Executor)

### Acceptance Checks

- [ ] `_category_.json` has `"position": 4`
- [ ] `index.md` has `sidebar_position: 0` and links to `./chapter-1-whisper.md`
- [ ] Each chapter has exactly 4 Learning Objectives
- [ ] Chapter 1 has Whisper model sizes table (5 rows), Python code block, Mermaid diagram
- [ ] Chapter 2 has 7-row action vocabulary table, system prompt ```text``` block, JSON example, Python parser, 2 Mermaid diagrams, Summary table (7 rows)
- [ ] Chapter 3 has 10-step trace table, 2 Mermaid diagrams, module contribution table, Summary table (7 rows)
- [ ] All prerequisite admonitions present (ch1: Modules 1-3; ch2: ch1; ch3: Modules 1-3 + ch1 + ch2)
- [ ] All Summary tables have minimum 6 rows (Ch1) or 7 rows (Ch2, Ch3)
- [ ] No bare XML angle brackets in prose or table cells
- [ ] All fenced blocks ASCII-only
- [ ] `npm run build` passes with zero errors and zero broken links

---

## Follow-ups and Risks

- **Risk 1**: System prompt curly braces in MDX — resolved by using ` ```text ``` ` language tag instead of ` ```json ``` ` for the system prompt block.
- **Risk 2**: Chapter 3 sequence diagram complexity — 7 participants is at the limit for readability; keep each step to one line.
- **Risk 3**: Python parser code in MDX — f-strings with `{action}` in prose will cause MDX JSX parse errors; show only the parser function body in fenced blocks.
