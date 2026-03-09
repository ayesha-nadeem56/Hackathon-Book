# Quickstart: UI Upgrade Development

**Branch**: `005-ui-upgrade`

## Prerequisites

- Node.js 18+ installed
- `npm` available

## Local Development

```bash
# From repo root
cd book
npm install
npm start
```

Docusaurus dev server starts at `http://localhost:3000`. Changes to `src/css/custom.css`, `src/pages/`, and `src/components/` hot-reload instantly.

## Building for Production

```bash
cd book
npm run build
```

Build output is placed in `book/build/`. Verify no errors before committing.

## Visual Testing Checklist

After each implementation task, manually verify in the browser:

1. **Viewport widths** — resize to 320px, 768px, 1024px, 1440px; confirm no horizontal scroll
2. **Light/Dark mode** — toggle theme; verify all surfaces update correctly
3. **Home page** — hero section, feature cards, navbar visible and styled
4. **Docs page** — open `docs/module-1-ros2/` or any chapter; verify typography, code blocks, sidebar
5. **Accessibility** — use browser DevTools colour-contrast checker on primary text

## Key Files

| File | Purpose |
|---|---|
| `book/src/css/custom.css` | All CSS variable overrides, global typography |
| `book/src/pages/index.js` | Home page React component |
| `book/src/pages/index.module.css` | Home page scoped CSS |
| `book/src/components/HomepageFeatures/index.js` | Feature cards component |
| `book/src/components/HomepageFeatures/styles.module.css` | Feature cards CSS |
| `book/docusaurus.config.js` | Site config, navbar, footer, theme settings |
