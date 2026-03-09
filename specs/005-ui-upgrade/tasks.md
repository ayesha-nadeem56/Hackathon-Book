---
description: "Task list for UI Upgrade — Docusaurus Book Site"
---

# Tasks: UI Upgrade — Docusaurus Book Site

**Input**: Design documents from `specs/005-ui-upgrade/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, quickstart.md ✅
**Tests**: Not requested in spec — no test tasks generated (manual visual QA only)
**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on other in-progress tasks)
- **[Story]**: User story this task belongs to (US1–US4)
- All file paths are relative to repo root

---

## Phase 1: Setup

**Purpose**: Verify dev environment is working before any changes

- [x] T001 Confirm `npm start` runs cleanly from `book/` and document current visual state (screenshot or notes)

---

## Phase 2: Foundational — CSS Color Foundation

**Purpose**: Establish the new indigo color palette via CSS custom properties. All user story phases depend on this being in place first — every `--ifm-color-primary-*` usage across navbar, sidebar, buttons, and links inherits from here.

**⚠️ CRITICAL**: No user story implementation begins until T002 and T003 are complete.

- [x] T002 Replace light-mode `--ifm-color-primary` scale with indigo palette (`#4361ee` → `#2942a8` darkest, `#7490f7` lightest) in `book/src/css/custom.css`
- [x] T003 Replace dark-mode `--ifm-color-primary` scale with accessible indigo palette (`#7c8cf8` → `#4f63c8` darkest, `#aab5fc` lightest) in `book/src/css/custom.css`
- [x] T004 [P] Add `prism.additionalLanguages: ['python', 'bash', 'yaml', 'docker']` and explicitly set `prism.theme` / `prism.darkTheme` to `prismThemes.github` / `prismThemes.dracula` in `book/docusaurus.config.js`

**Checkpoint**: Run `npm run build` from `book/` — must pass before proceeding to user story phases

---

## Phase 3: User Story 1 — Home Page First Impression (Priority: P1) 🎯 MVP

**Goal**: A first-time visitor lands on the home page and immediately sees a polished, book-specific hero section with correct branding, dual CTAs, and book-relevant feature cards — not the Docusaurus starter placeholder.

**Independent Test**: Load `http://localhost:3000` after `npm start`; verify the hero gradient, both CTA buttons, and three book-specific feature cards render without placeholder Docusaurus content; resize to mobile (320px) and confirm layout holds.

- [x] T005 [P] [US1] Add hero banner gradient background (`linear-gradient` from `--ifm-color-primary-darkest` to `--ifm-color-primary`), white title/subtitle text, and increased padding in `book/src/pages/index.module.css`
- [x] T006 [US1] Add second CTA button "View All Modules →" (linking to `/docs/module-1-ros2/`) alongside the existing "Start Reading" button in `book/src/pages/index.js`
- [x] T007 [P] [US1] Replace three `FeatureList` items with book-specific entries: "ROS 2 & Physical AI", "AI-Powered RAG Chatbot", "Hands-On Code Examples" (with updated descriptions) in `book/src/components/HomepageFeatures/index.js`; remove all `undraw_docusaurus_*` SVG references and substitute inline SVG icons or Unicode symbol fallbacks
- [x] T008 [P] [US1] Update feature card styles: add hover lift effect, border-top accent in `--ifm-color-primary`, and responsive 2→1 column collapse at `max-width: 996px` in `book/src/components/HomepageFeatures/styles.module.css`
- [x] T009 [US1] Clean up footer in `book/docusaurus.config.js`: replace default Docusaurus links with project-relevant links (GitHub repo, Docs); update footer style to `dark`

**Checkpoint**: Home page renders with branded hero, dual CTAs, and book-specific cards — User Story 1 independently verifiable

---

## Phase 4: User Story 2 — Chapter Reading Experience (Priority: P1)

**Goal**: A reader opens any docs page and finds comfortable, high-quality typography — appropriate text size, generous line spacing, capped content width, clear heading hierarchy, and visually distinct code blocks.

**Independent Test**: Open `http://localhost:3000/docs/module-1-ros2/` (or any docs page); verify text size feels readable (≥16px effective), paragraphs do not stretch full-width on a 1440px monitor, H1–H4 have distinct weights, and code blocks have a styled background with visible syntax highlighting in both themes.

- [x] T010 [US2] Set `--ifm-font-size-base: 16.5px` and `--ifm-line-height-base: 1.75` in the `:root` block of `book/src/css/custom.css`
- [x] T011 [US2] Add `max-width: 820px` constraint on the docs article content column in `book/src/css/custom.css` (target `.theme-doc-markdown` or `article.margin-bottom--xl` as appropriate for Docusaurus 3.x class names)
- [x] T012 [US2] Set `--ifm-heading-font-weight: 700` in `:root` and add `.markdown h3, .markdown h4 { font-weight: 600; }` in `book/src/css/custom.css`
- [x] T013 [US2] Override `--ifm-pre-background: #f6f8fa` (light) and `--ifm-pre-background: #1e2029` (dark, inside `[data-theme='dark']`) in `book/src/css/custom.css`; set `--ifm-code-font-size: 90%`
- [x] T014 [US2] Strengthen sidebar active-link indicator: override `--ifm-menu-color-active` to use `--ifm-color-primary` and add a left border accent on `.menu__link--active` in `book/src/css/custom.css`

**Checkpoint**: Any docs page renders with improved readability — User Story 2 independently verifiable alongside US1

---

## Phase 5: User Story 3 — Light/Dark Theme Toggle (Priority: P2)

**Goal**: The theme toggle switches all UI surfaces (navbar, sidebar, hero, feature cards, code blocks, footer) consistently in one click with no elements retaining the previous theme's colours.

**Independent Test**: Start in light mode → toggle to dark → verify all major surfaces update; refresh → dark mode persists; toggle back to light → all surfaces update cleanly.

- [x] T015 [US3] Audit `book/src/pages/index.module.css` for any hardcoded colour values (`#rrggbb`, `rgb()`, named colours) that bypass CSS variables; replace with `var(--ifm-*)` tokens or theme-aware values
- [x] T016 [US3] Audit `book/src/components/HomepageFeatures/styles.module.css` for hardcoded colours; replace with CSS variable references; confirm feature card borders and hover states work in both themes
- [x] T017 [US3] Verify `[data-theme='dark']` block in `book/src/css/custom.css` covers `--ifm-pre-background`, `--docusaurus-highlighted-code-line-bg`, and sidebar accent variables; add any missing overrides

**Checkpoint**: Theme toggle cycles cleanly with no visual artifacts — User Story 3 independently verifiable

---

## Phase 6: User Story 4 — Tablet Responsive Layout (Priority: P3)

**Goal**: The site renders correctly at 768px–1024px — sidebar behaviour, feature card grid, and hero section all adapt gracefully without overflow or overlapping elements.

**Independent Test**: Resize browser to 768px and 1024px; verify sidebar collapses or reduces width on docs pages, home page feature cards reflow to 2-col or 1-col, and hero text/buttons remain readable.

- [x] T018 [US4] Verify docs page layout at 768px and 1024px in `book/src/css/custom.css`; add a targeted media query if the 820px content-width cap causes layout issues at tablet breakpoints (e.g., sidebar + content overflow)
- [x] T019 [US4] Verify feature card grid reflow in `book/src/components/HomepageFeatures/styles.module.css`: confirm `@media (max-width: 996px)` collapses cards to single column; add `768px` intermediate breakpoint if 2-column layout is preferred at tablet width

**Checkpoint**: Site is responsive across all three breakpoints — User Story 4 independently verifiable

---

## Final Phase: Polish & Cross-Cutting Verification

**Purpose**: Build gate, Mermaid compatibility, and final success-criteria sign-off

- [x] T020 [P] Run `npm run build` from `book/` and resolve any build errors or broken-link warnings introduced by changes
- [x] T021 [P] Open `docs/` pages containing Mermaid diagrams; verify diagrams render in both light and dark themes with the updated palette
- [x] T022 Remove or replace any remaining unreferenced Docusaurus placeholder SVG files from `book/static/img/` (`undraw_docusaurus_mountain.svg`, `undraw_docusaurus_tree.svg`, `undraw_docusaurus_react.svg`) if no longer used after T007
- [ ] T023 Manual visual QA — validate all 7 success criteria across viewports (320px, 768px, 1440px) in both light and dark themes:
  - SC-001: Title/purpose identifiable within 5s on home page
  - SC-002: No horizontal scroll at 320/768/1440px
  - SC-003: Body text contrast ≥ 4.5:1 (check with DevTools)
  - SC-004: All existing docs pages readable, no content missing
  - SC-005: Theme toggle switches all surfaces in one click
  - SC-006: `npm run build` passes without errors
  - SC-007: Home page visually distinct from default Docusaurus starter

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **BLOCKS all user story phases**
- **US1 (Phase 3)**: Depends on Phase 2 completion
- **US2 (Phase 4)**: Depends on Phase 2 completion — can run in parallel with US1 (different files)
- **US3 (Phase 5)**: Depends on Phase 3 + 4 completion (reviews outputs of both)
- **US4 (Phase 6)**: Depends on Phase 3 + 4 completion — can run in parallel with US3
- **Polish (Final Phase)**: Depends on all user story phases

### User Story Dependencies

- **US1 (P1)**: After Foundational — no story dependencies; files: `index.js`, `index.module.css`, `HomepageFeatures/*`, `docusaurus.config.js`
- **US2 (P1)**: After Foundational — no story dependencies; files: `custom.css` only
- **US3 (P2)**: After US1 + US2 — reviews and hardens their outputs
- **US4 (P3)**: After US1 + US2 — verifies responsive behaviour of their outputs

### Within Each User Story

- Within US1: T005 and T007/T008 are parallel (different files); T006 comes after T005
- Within US2: T010–T014 are sequential edits to `custom.css`
- Within US3: T015–T017 are sequential audits
- Within US4: T018–T019 are parallel (different files)

### Parallel Opportunities

- T002 + T004: Different files (`custom.css` vs `docusaurus.config.js`)
- T003 + T004: Different files
- T005 + T007 + T008: All different files (Phase 3)
- US1 tasks (Phase 3) + US2 tasks (Phase 4): Completely different files — can run in parallel
- T015 + T016: Different files (Phase 5)
- T018 + T019: Different files (Phase 6)
- T020 + T021: Independent verification tasks (Final Phase)

---

## Parallel Example: US1 + US2 (can run simultaneously after Foundational)

```text
# Developer A — US1 (home page)
Task T005: book/src/pages/index.module.css
Task T006: book/src/pages/index.js
Task T007: book/src/components/HomepageFeatures/index.js
Task T008: book/src/components/HomepageFeatures/styles.module.css
Task T009: book/docusaurus.config.js

# Developer B — US2 (chapter reading)
Task T010: book/src/css/custom.css (typography)
Task T011: book/src/css/custom.css (content width)
Task T012: book/src/css/custom.css (headings)
Task T013: book/src/css/custom.css (code blocks)
Task T014: book/src/css/custom.css (sidebar)
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational — install indigo palette + Prism config
3. Complete Phase 3 (US1) — home page redesign
4. Complete Phase 4 (US2) — reading experience
5. **STOP and VALIDATE**: Run `npm run build`; manually check home page + one docs page
6. Ship as MVP — visible improvement with no risk to content

### Incremental Delivery

1. Phase 1 + 2 → Color foundation ready
2. Phase 3 (US1) → Home page branded ✅ Demo-able
3. Phase 4 (US2) → Reading experience upgraded ✅ Demo-able
4. Phase 5 (US3) → Theme toggle polished ✅
5. Phase 6 (US4) → Tablet verified ✅
6. Final Phase → Build gate + full QA sign-off

---

## Notes

- No new npm packages are added — all changes are CSS + JSX edits to owned files
- `custom.css` is edited sequentially (T002, T003, T010–T014, T017) — avoid parallel edits to this file
- After T007 removes SVG imports, run `npm run build` to confirm no missing-module errors
- Mermaid integration (`@docusaurus/theme-mermaid`) is read-only in this feature — verify but do not modify
- Commit after each task group (end of each phase) to keep git history clean
