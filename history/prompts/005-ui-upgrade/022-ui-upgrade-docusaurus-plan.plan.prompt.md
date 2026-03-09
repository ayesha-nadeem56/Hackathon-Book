---
id: 022
title: ui-upgrade-docusaurus-plan
stage: plan
date: 2026-03-09
surface: agent
model: claude-sonnet-4-6
feature: 005-ui-upgrade
branch: 005-ui-upgrade
user: hp
command: /sp.plan
labels: ["ui","docusaurus","plan","color-palette","typography","responsive"]
links:
  spec: specs/005-ui-upgrade/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-ui-upgrade/plan.md
  - specs/005-ui-upgrade/research.md
  - specs/005-ui-upgrade/quickstart.md
tests:
  - npm run build (book/) — build gate
---

## Prompt

(empty — /sp.plan invoked on current branch 005-ui-upgrade)

## Response snapshot

Generated full implementation plan for the Docusaurus UI upgrade feature.

**Phase 0 (research.md)**: Resolved 8 decisions — electric indigo color palette (`#4361ee`/`#7c8cf8`), typography (16.5px base, 1.75 line-height, 820px content width), heading weights, hero redesign strategy (direct edit, no swizzle), code block approach (bundled Prism themes + background override), sidebar active state (CSS variables only), responsive breakpoints (Infima handles them; regression test only), no swizzling required.

**Phase 1 (plan.md)**: Technical context confirmed — Docusaurus 3.9.2, React 19, Infima CSS. Constitution check: all 5 principles pass. 6 files in scope: `custom.css`, `index.js`, `index.module.css`, `HomepageFeatures/index.js`, `HomepageFeatures/styles.module.css`, `docusaurus.config.js`. No new npm dependencies. No data model or API contracts (pure UI). 7 task groups identified for `/sp.tasks`. ADR suggestion raised for color palette decision.

**quickstart.md**: Dev setup documented (`cd book && npm start`).

## Outcome

- ✅ Impact: Complete implementation plan ready for /sp.tasks; all technical decisions resolved with rationale documented.
- 🧪 Tests: Build gate (`npm run build`); manual visual QA against 7 SCs.
- 📁 Files: specs/005-ui-upgrade/plan.md, research.md, quickstart.md
- 🔁 Next prompts: `/sp.tasks` to generate task list; optionally `/sp.adr ui-color-palette-indigo`
- 🧠 Reflection: No swizzling approach keeps upgrade risk minimal and Docusaurus upgradeable without merge conflicts.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): constitution check — all 5 PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Run /sp.tasks then /sp.implement
