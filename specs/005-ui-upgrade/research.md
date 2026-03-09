# Research: UI Upgrade — Docusaurus Book Site

**Branch**: `005-ui-upgrade` | **Date**: 2026-03-09
**Phase**: 0 — Unknowns resolved before design

---

## Decision 1: Color Palette Strategy

**Decision**: Replace the default green palette with an electric indigo/blue palette suited for an AI & robotics technical book.

**Rationale**: The current `#2e8555` green palette is the unmodified Docusaurus starter default. For a book on Humanoid Robotics and Physical AI, an indigo/deep-blue tone better conveys themes of intelligence, precision, and technology. Indigo also provides better accessibility contrast at the mid-range shades compared to green.

**Proposed values**:

| Variable | Light Mode | Dark Mode |
|---|---|---|
| `--ifm-color-primary` | `#4361ee` | `#7c8cf8` |
| `--ifm-color-primary-dark` | `#3a56d4` | `#6c7de6` |
| `--ifm-color-primary-darker` | `#3451c8` | `#6377e0` |
| `--ifm-color-primary-darkest` | `#2942a8` | `#4f63c8` |
| `--ifm-color-primary-light` | `#5370f2` | `#8c9bfa` |
| `--ifm-color-primary-lighter` | `#5e7af4` | `#96a4fb` |
| `--ifm-color-primary-lightest` | `#7490f7` | `#aab5fc` |

**Contrast check**: `#4361ee` on white (#ffffff) → contrast ratio ≈ 4.7:1 (passes WCAG AA for text ≥ 18px; borderline for body text — use darker `#3a56d4` for text-on-white). `#7c8cf8` on dark background (#1b1b1d) → contrast ratio ≈ 5.2:1 (passes WCAG AA).

**Alternatives considered**:
- Retain green: rejected (too generic, disconnected from AI/robotics domain)
- Deep teal: considered, but visually too similar to the current dark-mode teal; indigo differentiates clearly
- Purple: rejected (less technical connotation; can feel consumer-product-heavy)

---

## Decision 2: Typography — Base Size and Content Width

**Decision**: Set `--ifm-font-size-base: 16.5px`, `--ifm-line-height-base: 1.75`, and `--ifm-container-width-xl: 1200px` with a `max-width: 820px` on the doc article content.

**Rationale**: Docusaurus defaults to 16px base / 1.6 line-height. For long-form reading (book chapters covering ROS 2, digital twins, VLA models), 1.75 line-height and a capped content column width (≤ 820px) significantly reduces eye fatigue. This is consistent with reading research and patterns from high-quality documentation sites (Stripe, MDN, Rust Book).

**Alternatives considered**:
- Keep 16px base: functional but misses the readability improvement
- 18px base: too large for code-heavy content where density matters
- No width cap: on 1440px+ screens, paragraphs become uncomfortably wide (>100 characters per line)

---

## Decision 3: Heading Typography

**Decision**: Use the Infima font stack but bump heading weights to `700` for H1–H2 and `600` for H3–H4. Apply `--ifm-heading-font-weight` for H1/H2 and target `.markdown h3, h4` directly in `custom.css`.

**Rationale**: Docusaurus/Infima defaults are already reasonable, but increasing heading contrast helps readers skim technical chapters that have many sub-sections. This is a non-breaking CSS-only change.

**Alternatives considered**:
- Import a custom Google Font (e.g., Inter, JetBrains Mono): adds ~30–60KB network overhead and a CDN dependency; rejected in favour of the system font stack which is faster and already system-native
- No heading weight change: missed readability opportunity at minimal cost

---

## Decision 4: Hero Section Redesign Strategy

**Decision**: Directly edit `book/src/pages/index.js` and `index.module.css` (no component swizzling needed). Replace the `HomepageFeatures` placeholder content (Docusaurus mountains/trees SVGs) with three book-specific feature cards: "ROS 2 & Physical AI", "RAG Chatbot Integration", and "Hands-On Code Examples". Add a background gradient to the hero banner.

**Rationale**: The existing home page is the unmodified Docusaurus starter with placeholder SVGs and text about Docusaurus itself (not the book). These are custom React components already owned by the project — swizzling is not needed since `index.js` is not a theme component. Editing them directly is the smallest viable change.

**Alternatives considered**:
- Swizzle `@theme/Layout` or `@theme/Navbar`: too broad a change; would require maintaining forked Docusaurus internals across upgrades
- Leave home page as-is and only change CSS: misses FR-003 (hero section improvement) which is explicitly required
- Fully custom landing page: disproportionate scope for this feature; incremental improvement to existing page is sufficient

---

## Decision 5: Code Block Enhancement

**Decision**: Override `--ifm-code-font-size: 90%`, set `--ifm-pre-background` to a slightly elevated background (`#f6f8fa` light / `#1e2029` dark), and rely on Prism themes already bundled by Docusaurus via `prism-react-renderer`. No new Prism themes need to be installed.

**Rationale**: Docusaurus 3.x already ships with `prism-react-renderer` and the `themes.github` / `themes.dracula` pair. The `docusaurus.config.js` already imports them. Only background tweaks and font-size adjustments are needed in `custom.css`.

**Alternatives considered**:
- Install a third-party code theme: unnecessary dependency; bundled themes are sufficient
- Custom Prism theme: disproportionate effort; bundled dracula (dark) and github (light) are well-established

---

## Decision 6: Sidebar Active State Enhancement

**Decision**: Override Docusaurus sidebar CSS variables — `--ifm-menu-color-active`, `--ifm-menu-color-background-active`, and `--ifm-menu-link-sublist-icon` — in `custom.css` to use the new indigo palette. No component swizzling required.

**Rationale**: All sidebar styling in Docusaurus is driven by CSS custom properties. The active state currently uses the primary color which will automatically update once the palette is changed. Minor additional overrides will boost the visual contrast of the active indicator.

**Alternatives considered**:
- Swizzle sidebar component: unnecessary; CSS variables provide full control
- No sidebar changes: the active state improvement is minimal effort and high readability value

---

## Decision 7: Responsive Breakpoints — No New Work Needed

**Decision**: Docusaurus/Infima already handles the three required breakpoints (mobile/tablet/desktop) via built-in responsive CSS. The feature work only needs to verify no custom CSS introduces regressions and that the hero section grid reflows correctly.

**Rationale**: The `@media screen and (max-width: 996px)` breakpoint in `index.module.css` already handles the tablet/mobile hero layout. Infima handles navbar collapse and sidebar drawer at `< 996px`. No custom breakpoint work is required beyond testing.

---

## Decision 8: No Component Swizzling Required

**Decision**: All required changes can be achieved without swizzling any Docusaurus theme components. Changes are scoped to: `book/src/css/custom.css`, `book/src/pages/index.js`, `book/src/pages/index.module.css`, `book/src/components/HomepageFeatures/index.js`, `book/src/components/HomepageFeatures/styles.module.css`, and `book/docusaurus.config.js` (navbar minor tweaks only).

**Rationale**: Swizzling introduces maintenance debt (forked theme components must be manually merged on Docusaurus upgrades). The spec explicitly prefers the smallest viable change and Docusaurus-native customization (FR-009). All required visual improvements are achievable via CSS custom properties and editing owned React components.

**Alternatives considered**:
- Swizzle `@theme/DocSidebar`: considered for active state; rejected since CSS variables achieve same outcome
- Swizzle `@theme/Footer`: not required by spec; footer cleanup can be done via `docusaurus.config.js` `footer` config
