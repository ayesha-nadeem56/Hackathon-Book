# Chapter Content Contract: Module 4 — Vision-Language-Action (VLA)

**Branch**: `004-module4-vla` | **Date**: 2026-03-09
**Phase**: 1 — Design & Contracts

This document defines the required structure and content elements for each file in Module 4.
All chapter files MUST conform to this contract before the `npm run build` acceptance check.

---

## Frontmatter Schema (All Files)

```yaml
---
id: <file-slug>          # matches filename without .md extension
sidebar_position: <N>    # integer, unique within module-4-vla/
---
```

---

## Body Section Order (All Chapters)

| Order | Section | Required |
|---|---|---|
| 1 | `## Learning Objectives` (exactly 4 bullet points) | MUST |
| 2 | `:::info Prerequisites` admonition | MUST |
| 3-N | Content sections (prose + diagrams + code blocks) | MUST |
| Last | `## Summary` table | MUST |

---

## Contract: `_category_.json`

| Field | Required Value |
|---|---|
| `label` | `"Module 4: Vision-Language-Action"` |
| `position` | `4` |
| `collapsible` | `true` |
| `collapsed` | `false` |
| `description` | `"Voice commands, LLM planning, and autonomous action for humanoid robots"` |

---

## Contract: `index.md`

**Frontmatter**: `id: module-4-overview`, `sidebar_position: 0`

**Required sections** (in order):

| Section | Required Content |
|---|---|
| Opening narrative | VLA concept: a robot that listens, understands, and acts |
| Prerequisites admonition | Links to Modules 1, 2, and 3 |
| Chapter overview table | 3 rows: chapter title / tool / role |
| Module Learning Outcomes | Exactly 5 bullet points |
| CTA link | `[Chapter 1 — Voice Input with Whisper →](./chapter-1-whisper.md)` |

---

## Contract: `chapter-1-whisper.md`

**Frontmatter**: `id: chapter-1-whisper`, `sidebar_position: 1`

**Prerequisites admonition**: Links to Modules 1, 2, and 3.

**Required content elements**:

| Element | Specification |
|---|---|
| Learning Objectives | Exactly 4 bullet points |
| ASR introduction | Audio-to-text concept; why robots need voice input |
| Whisper description | Transformer-based; multilingual; 5 model sizes |
| Model sizes table | Exactly 5 rows: tiny, base, small, medium, large; columns: Size / Parameters / Speed / Use Case |
| Python transcription block | `whisper.load_model()` + `sd.rec()` + `model.transcribe()`; python tag; ASCII-only; first-line comment |
| ROS 2 publisher snippet | VoiceNode publishes `std_msgs/String` on `/voice_command`; python tag; ASCII-only |
| Mermaid pipeline | 7 nodes: microphone → AudioCapture → Whisper → VoiceNode → /voice_command → LLMPlanner (max 8 nodes) |
| Summary table | Minimum 6 rows: ASR, Whisper, Transcription, Model Size, VoiceNode, /voice_command |

**Validation rules**:
- Python blocks use `python` language tag with first-line comment
- All code ASCII-only; no Unicode characters in code
- No bare angle brackets in prose

---

## Contract: `chapter-2-llm-planner.md`

**Frontmatter**: `id: chapter-2-llm-planner`, `sidebar_position: 2`

**Prerequisites admonition**: Link to Chapter 1 (VoiceNode `/voice_command` output).

**Required content elements**:

| Element | Specification |
|---|---|
| Learning Objectives | Exactly 4 bullet points |
| Planning problem section | Why natural language cannot directly drive motors |
| LLMs as planners section | Instruction-following models; system prompt as constraint |
| Action vocabulary table | Exactly 7 rows: navigate_to, pick_up, place_on, push, open_door, close_door, wait; columns: Action / Parameters / Purpose |
| System prompt block | 4-part template (ROLE / VOCABULARY / FORMAT / SAFETY); MUST use `text` language tag (NOT `json`); ASCII-only |
| JSON structured output block | Example response array; `json` tag acceptable here (no curly braces in prose context) |
| Python parser block | `json.loads()` + `VALID_ACTIONS` set + `ValueError` on invalid action; python tag; ASCII-only |
| Hallucination guardrail section | What happens when LLM outputs invalid action; safe halt described |
| Mermaid diagram 1 | LLM planning pipeline (VoiceCommand → LLM → JSONOutput → Parser → ROS2Actions, max 8 nodes) |
| Mermaid diagram 2 | Guardrail flow: Parser → valid/invalid branch → execute/halt (graph TD, max 8 nodes) |
| Summary table | Minimum 7 rows: LLM Planner, System Prompt, Action Vocabulary, Structured Output, Action Parser, Hallucination, Guardrail |

**Validation rules**:
- System prompt MUST use ` ```text ``` ` tag — this is a hard requirement
- Python parser block uses `python` tag
- VALID_ACTIONS set must list all 7 actions
- No bare angle brackets in prose or table cells

---

## Contract: `chapter-3-capstone.md`

**Frontmatter**: `id: chapter-3-capstone`, `sidebar_position: 3`

**Prerequisites admonition**: Links to Modules 1, 2, 3 and Chapter 1 and Chapter 2.

**Required content elements**:

| Element | Specification |
|---|---|
| Learning Objectives | Exactly 4 bullet points |
| VLA system intro | All 4 modules working together; connects Module 1 hardware to Module 4 language |
| Mermaid diagram 1 | Full VLA architecture; subgraph grouping by module layer (max 8 nodes) |
| 10-step trace table | Exactly 10 rows; columns: Step / Component / Module / Input / Output |
| Mermaid diagram 2 | Sequence diagram with 7 participants: User, Whisper, LLM, Guardrail, Nav2, IsaacROS, ArmController |
| Module contribution map | Table: Module / Role / Key Output (4 rows for Modules 1-4) |
| Guardrail in action section | "fly to cube" rejection scenario; shows safety halt |
| Summary table | Minimum 7 rows: VLA, Whisper, LLM Planner, Guardrail, Nav2, Isaac ROS, Action Executor |

**Validation rules**:
- Sequence diagram participants limited to 7
- 10-step trace table must have all 5 columns
- Module contribution map must cover all 4 modules
- No bare angle brackets in any section

---

## Cross-Chapter Validation Checklist

- [ ] `_category_.json` position is `4`
- [ ] `index.md` `sidebar_position` is `0`; links to `./chapter-1-whisper.md`
- [ ] Each chapter has exactly 4 Learning Objectives
- [ ] Chapter 1 has 5-row model sizes table, Python transcription block, Mermaid pipeline
- [ ] Chapter 2 has 7-row vocabulary table, `text`-tagged system prompt, JSON example, Python parser, 2 Mermaid diagrams
- [ ] Chapter 3 has 10-step trace table, 2 Mermaid diagrams, module contribution map
- [ ] All prerequisite admonitions present (ch1: Modules 1-3; ch2: ch1; ch3: Modules 1-3 + ch1 + ch2)
- [ ] Chapter 1 Summary table minimum 6 rows; Chapters 2 and 3 minimum 7 rows
- [ ] No bare XML angle brackets in prose or table cells
- [ ] All fenced blocks ASCII-only
- [ ] `npm run build` passes with zero errors and zero broken links
