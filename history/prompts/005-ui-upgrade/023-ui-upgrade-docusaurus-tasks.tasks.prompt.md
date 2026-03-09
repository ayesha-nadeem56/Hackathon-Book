---
id: 023
title: ui-upgrade-docusaurus-tasks
stage: tasks
date: 2026-03-09
surface: agent
model: claude-sonnet-4-6
feature: 005-ui-upgrade
branch: 005-ui-upgrade
user: hp
command: /sp.tasks
labels: ["ui","docusaurus","tasks","typography","color-palette","responsive"]
links:
  spec: specs/005-ui-upgrade/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-ui-upgrade/tasks.md
tests:
  - null
---

## Prompt

(empty — /sp.tasks invoked on current branch 005-ui-upgrade)

## Response snapshot

Generated `specs/005-ui-upgrade/tasks.md` with 23 tasks across 7 phases for the Docusaurus UI upgrade feature.

**Phases**: Setup (1 task) → Foundational color palette (3 tasks) → US1 Home Page MVP (5 tasks) → US2 Reading Experience (5 tasks) → US3 Dark Mode (3 tasks) → US4 Tablet Responsive (2 tasks) → Polish & QA (4 tasks).

**Key decisions**: US1 and US2 can run in parallel after Foundational (completely different files). `custom.css` edits are sequential to avoid conflicts. No new npm packages. No test tasks (not requested in spec). MVP = Phase 1 + 2 + 3 + 4.

## Outcome

- ✅ Impact: 23 immediately executable tasks covering all 4 user stories and 7 success criteria; ready for /sp.implement.
- 🧪 Tests: Manual visual QA (T023) validates SC-001 through SC-007; build gate (T020).
- 📁 Files: specs/005-ui-upgrade/tasks.md
- 🔁 Next prompts: `/sp.implement` to execute tasks
- 🧠 Reflection: Parallel opportunity between US1 (JSX/module-css) and US2 (custom.css) is clean — completely disjoint file sets allow simultaneous implementation.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): format validation — all 23 tasks follow [ID] [P?] [Story] pattern ✅
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): /sp.implement starting from T001
