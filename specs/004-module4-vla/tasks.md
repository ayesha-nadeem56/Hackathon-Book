# Tasks: Module 4 — Vision-Language-Action (VLA)

**Input**: Design documents from `/specs/004-module4-vla/`
**Prerequisites**: plan.md, spec.md, research.md
**Tests**: Not requested — documentation module; build gate (`npm run build`) is the acceptance test.
**Organization**: Tasks grouped by user story; each story maps to one chapter file.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Module Directory and Sidebar)

**Purpose**: Create the Docusaurus category directory and sidebar descriptor — must exist before any chapter file can be written.

- [x] T001 Create `book/docs/module-4-vla/` directory (mkdir)
- [x] T002 Create `book/docs/module-4-vla/_category_.json` with `label: "Module 4: Vision-Language-Action"`, `position: 4`, `collapsible: true`, `collapsed: false`, and `description: "Voice commands, LLM planning, and autonomous action for humanoid robots"`

---

## Phase 2: Foundational (Module Landing Page)

**Purpose**: The index page links to all three chapters and establishes the module narrative. Must exist before chapters reference it.

**WARNING**: Chapter CTAs in index.md use `.md` relative links -- must match final chapter filenames exactly.

- [x] T003 Create `book/docs/module-4-vla/index.md` with front-matter `id: module-4-overview`, `sidebar_position: 0`; sections: (1) opening narrative -- the VLA concept: a robot that listens, understands, and acts; (2) prerequisites admonition -- Modules 1, 2, and 3; (3) chapter overview table (3 rows: Chapter / Tool / Role); (4) Module Learning Outcomes (5 bullet points); (5) CTA link to `./chapter-1-whisper.md`

**Checkpoint**: Directory, sidebar, and index in place -- chapter implementation can begin.

---

## Phase 3: User Story 1 — Voice-to-Action with Whisper (Priority: P1)

**Goal**: Deliver Chapter 1 covering OpenAI Whisper ASR, the audio-to-text pipeline, and ROS 2 voice integration.

**Independent Test**: A student can answer: "What does Whisper output?", "Name two Whisper model sizes and their trade-off", "What ROS 2 message type carries a transcribed command?"

- [x] T004 [US1] Create `book/docs/module-4-vla/chapter-1-whisper.md` with: Learning Objectives (4), Prerequisites admonition, ASR intro, Whisper architecture, 5-row model sizes table, Python transcription code block (ASCII-only), ROS 2 publisher snippet, Mermaid pipeline diagram (<=8 nodes), Summary table (6 rows)

**Checkpoint**: Chapter 1 complete -- Whisper pipeline explained with code, table, and diagram.

---

## Phase 4: User Story 2 — LLM Cognitive Planning (Priority: P2)

**Goal**: Deliver Chapter 2 covering LLM cognitive planning, prompt engineering, structured JSON output, and ROS 2 action translation -- including the hallucination guardrail.

**Independent Test**: A student can explain: "Why can't raw LLM output directly drive a robot?", "What is a system prompt?", "What does structured output mean in this context?"

- [x] T005 [US2] Create `book/docs/module-4-vla/chapter-2-llm-planner.md` with: Learning Objectives (4), Prerequisites admonition, planning problem section, LLMs as planners, 7-action vocabulary table, system prompt fenced block (```text, ASCII-only), JSON example, Python parser block (json.loads + vocabulary validation), hallucination guardrail section, ROS 2 action translation, Mermaid diagram 1 (planning pipeline), Mermaid diagram 2 (guardrail flow), Summary table (7 rows)

**Checkpoint**: Chapter 2 complete -- LLM planning pipeline explained with system prompt, JSON, parser, and guardrail.

---

## Phase 5: User Story 3 — End-to-End Capstone (Priority: P3)

**Goal**: Deliver Chapter 3 -- the complete VLA capstone integrating all four modules with the "Pick up the red cube" scenario traced step by step.

**Independent Test**: A student can trace the full data flow from spoken command through Whisper, LLM, Nav2, Isaac ROS, and arm controller, naming the module responsible for each step.

- [x] T006 [US3] Create `book/docs/module-4-vla/chapter-3-capstone.md` with: Learning Objectives (4), Prerequisites admonition (Modules 1-3 + ch1 + ch2), VLA capstone intro, system architecture, Mermaid diagram 1 (full VLA architecture with subgraph), 10-step capstone trace table (Step/Component/Module/Input/Output), Mermaid diagram 2 (sequence diagram 7 participants), module contribution map table, guardrail in action section, Summary table (7 rows)

**Checkpoint**: Chapter 3 complete -- full capstone with 10-step trace, two Mermaid diagrams, and module contribution map.

---

## Phase 6: Polish and Build Validation

- [x] T007 Run `npm run build` in `book/` directory and confirm zero build errors, zero broken links, module-4-vla appears in sidebar at position 4

---

## Dependencies and Execution Order

- **Setup (Phase 1)**: No dependencies -- start immediately; T001 before T002
- **Foundational (Phase 2)**: T003 depends on T001 + T002
- **User Story Phases (3-5)**: All depend on Phase 2; T004, T005, T006 can run in parallel (different files)
- **Polish (Phase 6)**: T007 depends on T001-T006 all complete

### Parallel Opportunities

```text
After T003 completes:
  [Parallel] T004 -- chapter-1-whisper.md     (US1)
  [Parallel] T005 -- chapter-2-llm-planner.md (US2)
  [Parallel] T006 -- chapter-3-capstone.md    (US3)
After T004 + T005 + T006 complete:
  [Sequential] T007 -- npm run build
```

---

## Acceptance Checks (from plan.md)

- [ ] `_category_.json` has `"position": 4`
- [ ] `index.md` links to `./chapter-1-whisper.md`; `sidebar_position: 0`
- [ ] Each chapter has exactly 4 Learning Objectives
- [ ] Chapter 1 has Whisper model sizes table (5 rows), Python code block, Mermaid diagram
- [ ] Chapter 2 has action vocabulary table (7 rows), system prompt block, JSON block, Python parser block, 2 Mermaid diagrams, Summary table (7 rows)
- [ ] Chapter 3 has 10-step capstone trace table, 2 Mermaid diagrams, module contribution table, Summary table (7 rows)
- [ ] All prerequisite admonitions present (ch1: Modules 1-3; ch2: ch1; ch3: Modules 1-3 + ch1 + ch2)
- [ ] No bare XML angle brackets in prose or table cells
- [ ] All fenced blocks ASCII-only
- [ ] `npm run build` passes with zero errors and zero broken links

---

## Notes

- MDX v3: no bare `<tag>` in prose or table cells; use backtick inline code instead
- All fenced code blocks: ASCII-only (no em-dashes, curly quotes, non-ASCII)
- System prompt example in Ch2: use ```text``` not ```json``` to avoid MDX curly-brace interpretation
- Mermaid node IDs: no spaces; use camelCase or underscores
- Relative links in index.md: must use `.md` extension
- Chapter 3 is the most complex content in the book -- use table for trace, keep each step to one sentence
