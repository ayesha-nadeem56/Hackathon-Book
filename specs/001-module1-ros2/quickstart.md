# Quickstart: Module 1 — The Robotic Nervous System (ROS 2)

**Branch**: `001-module1-ros2` | **Date**: 2026-03-07

This guide documents how to set up the Docusaurus book locally, run the development
server, add new content, validate content, and deploy to GitHub Pages.

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Node.js | 18 LTS | https://nodejs.org (or `nvm install 18`) |
| npm | 9+ (bundled with Node 18) | — |
| Git | Any recent | — |
| Python | 3.10+ | For code example validation only |
| xmllint | Any | `sudo apt install libxml2-utils` (Linux) or `brew install libxml2` (macOS) |

---

## 1. Clone and Install

```bash title="Terminal"
# Clone the repository
git clone https://github.com/<org>/Hackathon-Book.git
cd Hackathon-Book

# Switch to the feature branch
git checkout 001-module1-ros2

# Install Docusaurus dependencies
cd book
npm install
```

---

## 2. Run the Development Server

```bash title="Terminal"
# From the book/ directory
npm start
```

Opens http://localhost:3000 in your browser with hot-reload enabled.
Module 1 will appear in the sidebar under "Module 1: The Robotic Nervous System".

---

## 3. Build for Production

```bash title="Terminal"
# From the book/ directory
npm run build
```

Output is in `book/build/`. Verify no warnings or errors in the build log.
Broken links cause the build to fail — this is intentional as a quality gate.

---

## 4. Add a New Chapter

1. Create `book/docs/module-1-ros2/chapter-N-slug.md`
2. Add required frontmatter (see `contracts/chapter-content-contract.md`)
3. Set `sidebar_position: N` (unique within directory)
4. Run `npm start` to preview
5. Validate content (see Section 6 below)

---

## 5. Validate Module 1 Content

### Python code examples

```bash title="Terminal"
# Save code block content to a .py file and validate syntax
python -m py_compile path/to/example.py
echo $?   # 0 = pass, non-zero = syntax error
```

### URDF XML samples

```bash title="Terminal"
# Save URDF code block to a .urdf file and validate XML
xmllint --noout path/to/humanoid_robot.urdf
echo $?   # 0 = valid, non-zero = malformed XML
```

### Broken links

```bash title="Terminal"
# Build first (broken links fail the build)
npm run build
```

### Mermaid diagrams

Mermaid diagrams are validated at build time by `@docusaurus/theme-mermaid`.
A syntax error in a Mermaid block will cause `npm run build` to fail.

---

## 6. Deployment to GitHub Pages

Deployment is automated via GitHub Actions on every push to `main`.

**Workflow file** (to be created): `.github/workflows/deploy.yml`

High-level steps:
1. Trigger: `push` to `main` branch
2. Steps:
   - `actions/checkout@v4`
   - `actions/setup-node@v4` with `node-version: 18`
   - `cd book && npm ci && npm run build`
   - Deploy `book/build/` to GitHub Pages using `actions/deploy-pages@v4`

**Manual deploy** (alternative):

```bash title="Terminal"
# From the book/ directory
GIT_USER=<your-github-username> npm run deploy
```

This pushes the `build/` output to the `gh-pages` branch automatically.

---

## 7. Docusaurus Configuration

Key settings in `book/docusaurus.config.js`:

| Setting | Value | Purpose |
|---|---|---|
| `title` | `"AI-Driven Interactive Book"` | Site title |
| `url` | `https://<org>.github.io` | GitHub Pages base URL |
| `baseUrl` | `"/Hackathon-Book/"` | Repo name as base path |
| `organizationName` | `<github-org>` | GitHub org/username |
| `projectName` | `"Hackathon-Book"` | GitHub repo name |
| `themeConfig.mermaid` | enabled | Mermaid diagram rendering |

---

## 8. File Naming Conventions

| Item | Pattern | Example |
|---|---|---|
| Module directory | `module-<N>-<slug>/` | `module-1-ros2/` |
| Chapter file | `chapter-<N>-<slug>.md` | `chapter-1-intro.md` |
| Static images | `static/img/module-1/<name>.png` | `static/img/module-1/ros2-architecture.png` |
| URDF samples | Embedded in chapter as code block; no separate file | — |
