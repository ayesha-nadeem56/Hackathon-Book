# Data Model: Module 2 — The Digital Twin (Gazebo & Unity)

**Branch**: `002-module2-digital-twin` | **Date**: 2026-03-09
**Phase**: 1 — Design & Contracts

This document describes the content structure model for Module 2 of the Docusaurus book.
There is no relational or vector database in this phase — the "data model" is
the schema of static content files.

---

## Entity 1: Module (Directory)

A Module is a Docusaurus docs directory representing one book module.

**Location**: `book/docs/module-2-digital-twin/`

**Files**:
- `_category_.json` — Docusaurus sidebar category metadata
- `index.md` — Module landing page

**`_category_.json` schema**:
```json
{
  "label": "Module 2: The Digital Twin",
  "position": 2,
  "collapsible": true,
  "collapsed": false,
  "description": "Simulate humanoid robots in Gazebo and Unity before deploying to real hardware"
}
```

**`index.md` frontmatter**:
```yaml
---
id: module-2-overview
sidebar_position: 0
---
```

**Validation rules**:
- `position` MUST be 2 (unique integer; follows Module 1 at position 1).
- `label` MUST be "Module 2: The Digital Twin".
- `index.md` MUST exist and contain a CTA link to `./chapter-1-gazebo.md`.
- `index.md` MUST include a Prerequisites admonition referencing Module 1.

---

## Entity 2: Chapter (MDX File)

A Chapter is a Docusaurus MDX page representing one topic area within the module.

**Location**: `book/docs/module-2-digital-twin/chapter-<N>-<slug>.md`

**Frontmatter schema**:
```yaml
---
id: chapter-<N>-<slug>     # Unique ID across all docs; format: chapter-N-slug
sidebar_position: <N>      # Integer; 1-based; unique within module directory
---
```

**Body structure** (ordered, all sections MUST be present):

| Order | Section | Required Content |
|---|---|---|
| 1 | `## Learning Objectives` | Bulleted list of 4 measurable learning outcomes |
| 2 | `:::info Prerequisites` | Admonition linking to prior chapters or Module 1 |
| 3-N | Content sections | Prose + at least one Mermaid diagram and one code/config block |
| Last | `## Summary` | Table with 2 columns: Term / Definition (min 6 rows) |

**Validation rules**:
- `sidebar_position` MUST be unique within `module-2-digital-twin/`.
- `id` MUST be unique across all docs in the book.
- Body MUST begin with `## Learning Objectives` (exactly 4 items).
- Body MUST end with `## Summary` table (minimum 6 rows).
- All SDF/XML tag names in prose MUST be backtick-wrapped (never bare `<tag>`).
- All fenced code blocks MUST be ASCII-only (no em-dashes, curly quotes, unicode).
- At least one Mermaid diagram per chapter.

---

## Entity 3: SDF Configuration Block

SDF (Simulation Description Format) is the XML-based file format for Gazebo worlds.

**Format**:
```xml
<!-- Annotated SDF snippet -- angle brackets allowed in fenced blocks -->
<sensor name="lidar" type="gpu_lidar">
  <topic>/scan</topic>
  <update_rate>10</update_rate>
</sensor>
```

**Validation rules**:
- SDF blocks MUST use the `xml` language tag.
- XML tag names in prose MUST be backtick-wrapped: e.g., `sensor`, `model`, `world`.
- All XML MUST be well-formed (no unclosed tags).
- ASCII-only content; no Unicode characters.
- Each block MUST have inline comments explaining key fields.

---

## Entity 4: YAML Message Structure Block

YAML is used to show ROS 2 message field structures (not executable code).

**Format**:
```yaml
# sensor_msgs/LaserScan -- key fields explained
header:
  stamp:    # ROS 2 timestamp of this scan
  frame_id: laser_link    # TF frame of the sensor
ranges:     # array of distance measurements in meters
  - 1.23
  - inf    # inf = no return at this angle
```

**Validation rules**:
- YAML blocks MUST use the `yaml` language tag.
- First line MUST be a comment identifying the message type.
- ASCII-only content.
- Key fields MUST be annotated with inline comments.

---

## Entity 5: Diagram (Mermaid Block)

**Supported diagram types for Module 2**:

| Type | Use Case | Example |
|---|---|---|
| `graph LR` | Data flow, feedback loops, pipelines | Digital twin feedback loop, sensor data flow |
| `graph TD` | Processing loops, decision trees | Gazebo simulation loop |
| `sequenceDiagram` | Step-by-step publish/subscribe sequences | LiDAR scan sequence |

**Validation rules**:
- Every chapter MUST include at least one Mermaid diagram.
- Mermaid node IDs MUST use camelCase or underscores (no spaces, no special chars).
- Maximum 8 nodes per diagram for readability.
- Diagrams MUST accurately represent the concept described in surrounding prose.
- Mermaid syntax validated at `npm run build` time.

---

## Module 2 Content Map

| File | `sidebar_position` | Title | Key Entities |
|---|---|---|---|
| `_category_.json` | — | — | Module entity (position 2, label, collapsible) |
| `index.md` | 0 | Module 2 Overview | Chapter table, prerequisites, 5 outcomes, CTA |
| `chapter-1-gazebo.md` | 1 | Physics Simulation with Gazebo | Digital twin, 4 physics properties, SDF snippet, Gazebo plugin table, 2 Mermaid diagrams, Summary (7 rows) |
| `chapter-2-unity.md` | 2 | High-Fidelity Environments with Unity | Gazebo vs Unity table, scene hierarchy text block, ROS-TCP-Connector, 1 Mermaid diagram, Summary (6 rows) |
| `chapter-3-sensors.md` | 3 | Simulating Robot Sensors | LiDAR/RGBD/IMU, 3 code blocks (YAML), 2 Mermaid diagrams, Summary (7 rows) |

---

## State Transitions

```
Draft --> Review --> Published
```

- **Draft**: MDX file created; may have incomplete sections.
- **Review**: All sections complete; Mermaid renders; code blocks pass validation; `npm run build` passes.
- **Published**: Merged to `main`; deployed to GitHub Pages.

**Draft to Review gate**:
- `npm run build` passes with zero errors and zero broken links
- All 4 Learning Objectives present per chapter
- Prerequisites admonition present with correct links
- Summary table has minimum required rows
- No bare XML angle brackets in prose
- All fenced code blocks are ASCII-only
