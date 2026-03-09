# Implementation Plan: UI Upgrade for Docusaurus Book Site

**Branch**: `005-ui-upgrade` | **Date**: 2026-03-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/005-ui-upgrade/spec.md`

## Summary

Upgrade the visual design, typography, and home page of the `book/` Docusaurus 3.9.2 site without modifying any book content. All changes are scoped to CSS custom properties, owned React page/component files, and `docusaurus.config.js`. No component swizzling, no new npm packages, and no backend changes are required.

## Technical Context

**Language/Version**: JavaScript/JSX (ES2022+), CSS3 — React 19, Node.js 18+
**Primary Dependencies**: Docusaurus 3.9.2 (classic preset), Infima CSS framework (bundled), `prism-react-renderer` (bundled), `@docusaurus/theme-mermaid`
**Storage**: N/A — static site, no data storage
**Testing**: Manual visual regression (browser DevTools, viewport resize), `npm run build` (Docusaurus build gate)
**Target Platform**: Browser (static site, GitHub Pages)
**Performance Goals**: No measurable performance regression; CSS bundle size increase < 5KB
**Constraints**: No component swizzling; no external CSS frameworks; all changes via Docusaurus-native customization (FR-009); Mermaid integration must remain functional
**Scale/Scope**: 6 files modified; 0 new npm dependencies; UI only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Notes |
|---|---|---|
| I. Accuracy & Technical Correctness | ✅ PASS | No book content modified; UI only |
| II. Clarity & Readability | ✅ PASS | This feature directly improves readability (FR-002, FR-004, FR-008) |
| III. Reproducibility of Workflows | ✅ PASS | `npm run build` and `npm start` are standard; no environment-specific tooling added |
| IV. Modularity & Maintainable Architecture | ✅ PASS | Changes isolated to `book/src/` and `book/docusaurus.config.js`; no new dependencies; smallest viable diff |
| V. Transparency in AI Content | ✅ PASS | No AI-generated content changes; UI only |

**Post-design re-check**: All gates pass. No component swizzling avoids maintenance debt (Principle IV). No new dependencies added.

## Project Structure

### Documentation (this feature)

```text
specs/005-ui-upgrade/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output — all decisions resolved
├── quickstart.md        # Phase 1 output — dev setup
├── spec.md              # Feature specification
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
book/
├── src/
│   ├── css/
│   │   └── custom.css              # MODIFY — color palette, typography, code blocks, sidebar
│   ├── pages/
│   │   ├── index.js                # MODIFY — hero section redesign
│   │   └── index.module.css        # MODIFY — hero CSS
│   └── components/
│       └── HomepageFeatures/
│           ├── index.js            # MODIFY — replace placeholder content with book-specific cards
│           └── styles.module.css   # MODIFY — feature card styling
└── docusaurus.config.js            # MODIFY — footer cleanup, prism theme config
```

**Structure Decision**: Web application — single Docusaurus static site in `book/`. No backend changes in scope. All modifications are to owned source files in `book/src/` and the top-level config.

## Phase 0: Research

**Status**: ✅ Complete — see [research.md](./research.md)

All eight unknowns resolved:

| # | Decision | Outcome |
|---|---|---|
| 1 | Color palette | Electric indigo `#4361ee` light / `#7c8cf8` dark — WCAG AA compliant |
| 2 | Typography base | `16.5px` base, `1.75` line-height, `820px` content max-width |
| 3 | Heading weights | `700` H1–H2, `600` H3–H4 via CSS custom properties |
| 4 | Hero redesign | Edit `index.js` directly (no swizzle); replace HomepageFeatures placeholder content |
| 5 | Code blocks | Prism bundled themes (github/dracula); override `--ifm-pre-background` in `custom.css` |
| 6 | Sidebar active state | CSS variable overrides only; no swizzling |
| 7 | Responsive breakpoints | No new work — Infima breakpoints already handle requirements; regression test only |
| 8 | Swizzling | Not required — all changes achievable via CSS + owned component edits |

## Phase 1: Design

### 1.1 Color System Design

**File**: `book/src/css/custom.css`

Complete CSS variable override plan:

```css
/* LIGHT MODE — Electric Indigo palette */
:root {
  /* Primary scale */
  --ifm-color-primary: #4361ee;
  --ifm-color-primary-dark: #3a56d4;
  --ifm-color-primary-darker: #3451c8;
  --ifm-color-primary-darkest: #2942a8;
  --ifm-color-primary-light: #5370f2;
  --ifm-color-primary-lighter: #5e7af4;
  --ifm-color-primary-lightest: #7490f7;

  /* Typography */
  --ifm-font-size-base: 16.5px;
  --ifm-line-height-base: 1.75;
  --ifm-heading-font-weight: 700;

  /* Content width */
  --ifm-container-width-xl: 1200px;

  /* Code */
  --ifm-code-font-size: 90%;
  --ifm-pre-background: #f6f8fa;
  --docusaurus-highlighted-code-line-bg: rgba(67, 97, 238, 0.1);
}

/* DARK MODE */
[data-theme='dark'] {
  --ifm-color-primary: #7c8cf8;
  --ifm-color-primary-dark: #6c7de6;
  --ifm-color-primary-darker: #6377e0;
  --ifm-color-primary-darkest: #4f63c8;
  --ifm-color-primary-light: #8c9bfa;
  --ifm-color-primary-lighter: #96a4fb;
  --ifm-color-primary-lightest: #aab5fc;

  --ifm-pre-background: #1e2029;
  --docusaurus-highlighted-code-line-bg: rgba(124, 140, 248, 0.15);
}

/* READING WIDTH — prevent over-wide paragraphs on large screens */
.container.padding-vert--xl .col.col--8,
article.margin-bottom--xl {
  max-width: 820px;
}

/* HEADING HIERARCHY */
.markdown h3 { font-weight: 600; }
.markdown h4 { font-weight: 600; }
```

### 1.2 Hero Section Design

**Files**: `book/src/pages/index.js`, `book/src/pages/index.module.css`

Redesigned hero:
- Background: gradient from primary dark to primary colour
- Title: site title from `siteConfig`
- Subtitle: tagline
- CTA button: "Start Reading — Module 1 →"
- Added second link: "View All Modules" → `/docs/`
- No external SVG dependencies; no new npm packages

```css
/* index.module.css additions */
.heroBanner {
  padding: 5rem 0;
  background: linear-gradient(135deg, var(--ifm-color-primary-darkest) 0%, var(--ifm-color-primary) 100%);
  color: white;
}

.heroBanner h1, .heroBanner p { color: white; }

.buttons { gap: 1rem; }

.buttonSecondary {
  background: transparent;
  border: 2px solid white;
  color: white;
}
.buttonSecondary:hover {
  background: rgba(255,255,255,0.15);
  color: white;
}
```

### 1.3 HomepageFeatures — Book-Specific Cards

**File**: `book/src/components/HomepageFeatures/index.js`

Replace the three Docusaurus placeholder items with book-specific content:

| Card | Title | Description |
|---|---|---|
| 1 | ROS 2 & Physical AI | From ROS 2 fundamentals to deploying robots with real-world physical AI pipelines |
| 2 | AI-Powered RAG Chatbot | Ask questions about the book — an embedded RAG chatbot answers from the full content corpus |
| 3 | Hands-On Code Examples | Every concept backed by reproducible Python code, tested on modern hardware and cloud environments |

Remove references to Docusaurus placeholder SVGs (`undraw_docusaurus_*`). Use inline SVG icons or Unicode emoji fallbacks; no new SVG library added.

### 1.4 Docusaurus Config — Prism Themes & Footer

**File**: `book/docusaurus.config.js`

Changes:
1. Explicitly set `prism.theme` to `prismThemes.github` and `prism.darkTheme` to `prismThemes.dracula` (already partially done; make explicit).
2. Add `prism.additionalLanguages: ['python', 'bash', 'yaml', 'docker']` to ensure robotics code samples render correctly.
3. Clean up footer — replace generic Docusaurus footer links with project-relevant links.

### 1.5 Data Model

Not applicable. This is a pure CSS/JSX UI feature with no data entities or persistence.

### 1.6 API Contracts

Not applicable. Static site — no API calls are added by this feature.

## Phase 2 Summary (Tasks)

The following task groups will be generated by `/sp.tasks`:

| Group | Tasks | Files |
|---|---|---|
| T1: Color palette | Update `--ifm-*` color variables in light + dark mode | `custom.css` |
| T2: Typography | Set base font size, line-height, content width, heading weights | `custom.css` |
| T3: Code blocks | Override `--ifm-pre-background`, verify Prism themes | `custom.css`, `docusaurus.config.js` |
| T4: Hero section | Redesign banner gradient, dual CTA buttons | `index.js`, `index.module.css` |
| T5: Feature cards | Replace Docusaurus placeholder content with book-specific cards | `HomepageFeatures/index.js`, `styles.module.css` |
| T6: Build verification | Run `npm run build`; verify no errors | CI check |
| T7: Visual QA | Verify all 7 success criteria across viewports and themes | Manual |

## Risks & Follow-ups

1. **Prism highlighting regression**: Adding `additionalLanguages` for Python/bash could affect build if language packs are missing — validate with `npm run build` immediately after config change.
2. **Mermaid theme conflict**: The `@docusaurus/theme-mermaid` uses its own theme variables. After color palette change, verify mermaid diagrams still render visibly in both light and dark modes.
3. **GitHub Pages cache**: After deploy, old CSS may be cached. Not a code issue, but worth noting for QA sign-off.

📋 Architectural decision detected: Indigo color palette replacing default Docusaurus green — affects brand identity going forward and creates a consistent visual language. Document reasoning and tradeoffs? Run `/sp.adr ui-color-palette-indigo`
