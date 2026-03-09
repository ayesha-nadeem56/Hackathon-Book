# Feature Specification: UI Upgrade for Docusaurus Book Site

**Feature Branch**: `005-ui-upgrade`
**Created**: 2026-03-09
**Status**: Draft
**Input**: User description: "Upgrade UI for Docusaurus-based project (book). Target audience: Developers and readers using the book_frontend site. Focus: Modern, clean, and user-friendly UI/UX without changing core content. Success criteria: Improved visual design (layout, typography, colors), better navigation and readability, fully compatible with Docusaurus theming system, responsive design for desktop and mobile."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-Time Reader Arrives at Home Page (Priority: P1)

A developer or reader lands on the book's home page for the first time. They immediately understand the book's purpose, see a visually appealing and professional layout, and can navigate to any chapter or section without confusion.

**Why this priority**: The home page is the primary entry point. A poor first impression drives users away before they engage with content. This is the highest-impact surface for visual upgrade.

**Independent Test**: Load the home page on desktop and mobile; verify hero section, navigation bar, color palette, and call-to-action are visually coherent and functional without reading any docs pages.

**Acceptance Scenarios**:

1. **Given** a user opens the home page on a desktop browser, **When** the page loads, **Then** the hero section displays a clear title, tagline, and at least one navigation call-to-action with improved typography and color scheme.
2. **Given** a user opens the home page on a mobile device (320px–768px wide), **When** the page loads, **Then** the layout adapts responsively — no horizontal scroll, text is legible, and navigation is accessible via a hamburger menu or equivalent.
3. **Given** a user has system dark mode enabled, **When** the page loads, **Then** the site automatically applies the dark theme with readable contrast and consistent branding.

---

### User Story 2 - Reader Navigates and Reads a Book Chapter (Priority: P1)

A reader browses the sidebar, selects a chapter (e.g., Module 1: ROS 2), and reads through the content. The reading experience feels comfortable — good line spacing, readable font size, adequate contrast, and clear heading hierarchy.

**Why this priority**: Content readability is the core purpose of the book site. Typography and layout improvements here deliver immediate value to the primary user activity.

**Independent Test**: Open any existing docs page; verify typography scale, line length, heading hierarchy, and code block styling without any structural content changes.

**Acceptance Scenarios**:

1. **Given** a reader opens a docs page, **When** they read the content, **Then** body text uses a comfortable reading size (equivalent to 16–18px base), line spacing feels open, and paragraphs are not stretched full-width on large screens.
2. **Given** a reader views a page with code blocks, **When** the page loads, **Then** code blocks are visually distinct with syntax highlighting, readable monospace font, and proper contrast in both light and dark modes.
3. **Given** a reader is on any docs page, **When** they view the sidebar, **Then** the active section is clearly highlighted, hierarchy is visually apparent, and the sidebar is usable on both desktop and mobile.

---

### User Story 3 - User Switches Between Light and Dark Themes (Priority: P2)

A developer using the site at night toggles to dark mode. All UI elements — backgrounds, text, sidebar, code blocks, navbar — adapt consistently to a polished dark theme.

**Why this priority**: Dark mode is a standard expectation for developer-facing documentation. Inconsistent theming undermines perceived quality.

**Independent Test**: Toggle the theme switch; verify all key UI surfaces (navbar, sidebar, content area, code blocks, footer) render consistently in both modes.

**Acceptance Scenarios**:

1. **Given** the site is in light mode, **When** the user clicks the theme toggle, **Then** the site switches to dark mode with appropriate background, text, and accent colors without any elements becoming unreadable.
2. **Given** the site is in dark mode, **When** the user refreshes the page, **Then** the dark mode preference is preserved.
3. **Given** either theme is active, **When** the user inspects UI components (navbar, cards, buttons), **Then** no elements have hardcoded colors that clash with the active theme.

---

### User Story 4 - Reader Uses Site on a Tablet (Priority: P3)

A reader accesses the book site on a tablet (768px–1024px). Navigation, sidebar, and content layout adapt gracefully to the intermediate screen size.

**Why this priority**: Tablets represent a significant reading device category. Responsive breakpoints must cover this range explicitly.

**Independent Test**: Load the site in a browser resized to 768px and 1024px; verify layout, sidebar behavior, and typography adapt correctly.

**Acceptance Scenarios**:

1. **Given** a user views the site at tablet width (768px–1024px), **When** browsing docs, **Then** the sidebar either collapses into an overlay or renders at a reduced width without overlapping content.
2. **Given** a user views the home page at tablet width, **When** the page loads, **Then** any feature cards or grid layouts reflow to a 2-column or single-column arrangement.

---

### Edge Cases

- What happens when a user's browser does not support CSS custom properties (very old browsers)? The site should still render with Docusaurus's bundled fallback styles.
- How does the site look when a very long chapter title appears in the sidebar? Text must truncate or wrap gracefully without breaking the sidebar layout.
- What if the user has increased system font size (accessibility setting)? The layout must not break or overflow when base font size is larger than default.
- What happens when the site is viewed offline or with CSS partially blocked? Core content must still be readable even if custom styles fail to load.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The site MUST apply a modernized color palette using Docusaurus CSS custom properties (`--ifm-*` variables), affecting primary, secondary, and accent colors in both light and dark modes.
- **FR-002**: The site MUST display body text at a comfortable reading size with appropriate line height and maximum content width (capped line length) on docs pages.
- **FR-003**: The home page MUST include an updated hero section with improved visual hierarchy — title, tagline, and at least one call-to-action button — styled beyond the default Docusaurus template.
- **FR-004**: The site MUST apply consistent heading styles (H1–H4) with clear visual hierarchy across all docs pages.
- **FR-005**: Code blocks MUST be visually distinct with a styled background, appropriate font, and syntax highlighting contrast in both light and dark modes.
- **FR-006**: The navigation bar MUST be visually refined — including logo placement, link styling, and theme-toggle button — matching the updated color palette.
- **FR-007**: The site MUST be fully responsive across three breakpoints: mobile (< 768px), tablet (768px–1024px), and desktop (> 1024px), with no horizontal overflow at any breakpoint.
- **FR-008**: The sidebar MUST clearly indicate the active page/section and provide readable hierarchy for nested sections.
- **FR-009**: All UI changes MUST be implemented using Docusaurus-supported customization mechanisms (CSS custom properties, `custom.css`, swizzled components, or `docusaurus.config.js` theme settings) without modifying core Docusaurus source.
- **FR-010**: The site MUST preserve all existing content — no docs pages, sidebar entries, or navigation links may be removed or altered in the UI upgrade.

### Assumptions

- The `book/` directory is the Docusaurus site root (`book/src/css/custom.css` is the primary style override file).
- Docusaurus classic preset with Infima CSS framework is in use — all color changes go through `--ifm-*` variables.
- No backend or RAG chatbot integration changes are in scope for this feature.
- Swizzling components (if needed) will use the `--wrap` strategy to minimize upgrade risk.
- The existing `@docusaurus/theme-mermaid` integration must continue to function after UI changes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Readers can identify the book's title, purpose, and primary navigation within 5 seconds of landing on the home page.
- **SC-002**: All docs pages render without horizontal scrolling at viewport widths of 320px, 768px, and 1440px.
- **SC-003**: Dark mode and light mode variants of every page pass a minimum contrast ratio of 4.5:1 for body text against its background (WCAG AA standard).
- **SC-004**: The complete UI upgrade passes a visual regression check where all existing docs pages remain fully readable and no content is missing.
- **SC-005**: Theme toggle correctly switches all major UI surfaces (navbar, sidebar, content, code blocks, footer) in a single interaction with no elements retaining the previous theme's colors.
- **SC-006**: All Docusaurus build checks pass (`npm run build` in `book/` completes without errors) after UI changes are applied.
- **SC-007**: The home page visually distinguishes itself from the default Docusaurus starter — updated colors, typography, and hero layout are immediately apparent without side-by-side comparison.
