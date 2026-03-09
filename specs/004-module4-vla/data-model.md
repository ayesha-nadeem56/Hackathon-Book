# Data Model: Module 4 — Vision-Language-Action (VLA)

**Branch**: `004-module4-vla` | **Date**: 2026-03-09
**Phase**: 1 — Design & Contracts

This document describes the content structure model for Module 4 of the Docusaurus book.
There is no relational or vector database in this phase — the "data model" is the schema of static content files.

---

## Entity 1: Module (Directory)

**Location**: `book/docs/module-4-vla/`

**`_category_.json` schema**:
```json
{
  "label": "Module 4: Vision-Language-Action",
  "position": 4,
  "collapsible": true,
  "collapsed": false,
  "description": "Voice commands, LLM planning, and autonomous action for humanoid robots"
}
```

**`index.md` frontmatter**:
```yaml
---
id: module-4-overview
sidebar_position: 0
---
```

**Validation rules**:
- `position` MUST be 4 (unique; follows Module 3 at position 3).
- `index.md` MUST link to `./chapter-1-whisper.md`.
- `index.md` MUST include a Prerequisites admonition referencing Modules 1, 2, and 3.

---

## Entity 2: Chapter (MDX File)

**Location**: `book/docs/module-4-vla/chapter-<N>-<slug>.md`

**Frontmatter schema**:
```yaml
---
id: chapter-<N>-<slug>
sidebar_position: <N>
---
```

**Body structure** (ordered, all MUST be present):

| Order | Section | Required Content |
|---|---|---|
| 1 | `## Learning Objectives` | Exactly 4 bullet points |
| 2 | `:::info Prerequisites` | Links to prior chapters or modules |
| 3-N | Content sections | Prose + Mermaid diagrams + code blocks |
| Last | `## Summary` | Term / Definition table (minimum 6 rows Ch1; minimum 7 rows Ch2/Ch3) |

**Validation rules**:
- `sidebar_position` unique within `module-4-vla/`.
- Body MUST begin with exactly 4 Learning Objectives.
- Body MUST end with Summary table.
- ASCII-only in all fenced code blocks.
- No bare XML angle brackets in prose or table cells.
- At least one Mermaid diagram per chapter; maximum 8 nodes per diagram.

---

## Entity 3: Python Code Block

Python is the primary implementation language shown in Chapters 1 and 2.

**Format**:
```python
# Whisper transcription -- load model and transcribe audio buffer
model = whisper.load_model("base")
result = model.transcribe(audio_array)
text = result["text"].strip()
```

**Validation rules**:
- Python blocks MUST use the `python` language tag.
- First line MUST be a comment identifying the code context.
- All content ASCII-only; no f-string curly braces in prose context (MDX v3 JSX conflict).
- Variables in code blocks are fine; only prose-inline `{var}` is prohibited.

---

## Entity 4: Text Block (System Prompt)

The LLM system prompt must use the `text` language tag to prevent MDX from parsing curly braces as JSX.

**Format**:
```text
ROLE: You are a robot action planner. Convert the user's natural language command
into a sequence of robot actions.
```

**Validation rules**:
- System prompt blocks MUST use the `text` language tag (NOT `json` or `python`).
- Content ASCII-only.
- Must include all four sections: ROLE, VOCABULARY, FORMAT, SAFETY.

---

## Entity 5: Diagram (Mermaid Block)

**Supported types for Module 4**:

| Type | Use Case |
|---|---|
| `graph LR` | Pipelines (ASR pipeline, LLM planning pipeline, VLA architecture) |
| `graph TD` | Decision flows (guardrail valid/invalid branch) |
| `sequenceDiagram` | End-to-end capstone interaction sequence |

**Validation rules**:
- Maximum 8 nodes per diagram.
- Node IDs: camelCase or underscores (no spaces, no special characters).
- Must accurately represent the concept described in surrounding prose.
- Validated at `npm run build` time.

---

## Module 4 Content Map

| File | `sidebar_position` | Title | Key Content Elements |
|---|---|---|---|
| `_category_.json` | — | — | position 4, label, collapsible |
| `index.md` | 0 | Module 4 Overview | Narrative, prerequisites (Modules 1-3), chapter table, 5 outcomes, CTA |
| `chapter-1-whisper.md` | 1 | Voice Input with Whisper | ASR intro, 5-row model sizes table, Python transcription block, ROS 2 publisher snippet, Mermaid pipeline, Summary (6 rows) |
| `chapter-2-llm-planner.md` | 2 | LLM Cognitive Planning | Planning problem, 7-row vocabulary table, system prompt text block, JSON example, Python parser, hallucination guardrail, 2 Mermaid diagrams, Summary (7 rows) |
| `chapter-3-capstone.md` | 3 | End-to-End VLA Capstone | VLA architecture Mermaid, 10-step trace table, sequence diagram (7 participants), module contribution map, guardrail scenario, Summary (7 rows) |

---

## State Transitions

```
Draft --> Review --> Published
```

- **Draft**: MDX file created; may have incomplete sections.
- **Review**: All sections complete; `npm run build` passes; no bare angle brackets; ASCII-only code.
- **Published**: Merged to `main`; deployed to GitHub Pages.
