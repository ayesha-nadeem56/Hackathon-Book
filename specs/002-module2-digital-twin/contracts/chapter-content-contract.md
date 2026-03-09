# Content Contract: Chapter Structure

**Feature**: `002-module2-digital-twin`
**Date**: 2026-03-09
**Type**: Content Schema Contract (static documentation — no API endpoints)

This contract defines the mandatory structure every chapter file in Module 2 MUST conform to.
It serves as the acceptance contract for the `/sp.tasks` implementation tasks.

---

## Chapter File Contract

### Frontmatter (required fields)

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | string | Yes | Unique across all docs; format: `chapter-<N>-<slug>` |
| `sidebar_position` | integer | Yes | Unique within `module-2-digital-twin/`; 1-based |

### Body Sections (ordered, all required)

| Order | Section Heading | Required Content |
|---|---|---|
| 1 | `## Learning Objectives` | Bulleted list of exactly 4 measurable learning outcomes |
| 2 | `:::info Prerequisites` | Admonition block; links to prior chapters or Module 1 |
| 3-N | Content sections | Prose + at least 1 Mermaid diagram; configuration/code blocks as needed |
| Last | `## Summary` | Table with 2 columns: Term / Definition (minimum 6 rows) |

### Code/Config Block Contract

| Attribute | Rule |
|---|---|
| Language tag | `xml` for SDF/Gazebo; `yaml` for ROS 2 message structures; `json` for category files |
| Inline comments | Key fields MUST have inline comments explaining their purpose |
| XML in prose | XML tag names in prose/tables MUST be backtick-wrapped (never bare `<tag>`) |
| ASCII-only | ALL fenced code blocks MUST contain only ASCII characters (no em-dashes, curly quotes, unicode) |

### Diagram Contract

| Attribute | Rule |
|---|---|
| Type | Mermaid code block (` ```mermaid `) |
| Frequency | At least 1 per chapter |
| Node count | Maximum 8 nodes per diagram |
| Node IDs | camelCase or underscores only (no spaces, no special characters) |
| Accuracy | MUST represent the concept described in surrounding prose |
| Validation | Must render without errors via `npm run build` |

---

## Module 2 Chapter Contracts

### Contract: Chapter 1 — Physics Simulation with Gazebo

**File**: `book/docs/module-2-digital-twin/chapter-1-gazebo.md`
**Frontmatter**: `id: chapter-1-gazebo`, `sidebar_position: 1`

Required sections (in order):

| Section | Content Requirement |
|---|---|
| Learning Objectives | 4 bullets: define digital twin; describe 4 physics properties; read SDF; explain feedback loop |
| Prerequisites | Module 1 (ROS 2 topics and publisher/subscriber) |
| What is a Digital Twin? | Definition; software replica mirroring geometry, dynamics, sensors; why simulate |
| Gazebo: A Physics Simulator | Gazebo overview; ROS 2 native integration; 4 physics properties (gravity, collisions, inertia, friction) |
| The Gazebo World File (SDF) | Annotated XML snippet (` ```xml `) showing world, model, physics plugin, include elements |
| Mermaid diagram 1 | Digital twin feedback loop (graph LR; physical robot + digital twin both connecting to ROS 2) |
| Mermaid diagram 2 | Gazebo simulation loop (graph TD; physics step -> sensors -> ROS 2 -> planner -> commands) |
| Gazebo Plugins | Table: plugin name / purpose / ROS 2 output (minimum 4 rows) |
| Summary | 7-row table (Digital Twin, Gazebo, SDF, Gravity, Inertia, Friction, Gazebo Plugin) |

**Acceptance criteria**:
- All 4 physics properties (gravity, collisions, inertia, friction) defined with explanation
- SDF snippet is valid XML with inline comments on key elements
- Both Mermaid diagrams have <= 8 nodes
- No bare XML angle brackets in prose or table cells

---

### Contract: Chapter 2 — High-Fidelity Environments with Unity

**File**: `book/docs/module-2-digital-twin/chapter-2-unity.md`
**Frontmatter**: `id: chapter-2-unity`, `sidebar_position: 2`

Required sections (in order):

| Section | Content Requirement |
|---|---|
| Learning Objectives | 4 bullets: explain why Unity for HRI; compare Gazebo vs Unity; describe scene hierarchy; explain ROS-TCP-Connector |
| Prerequisites | Chapter 1 (this module) + Module 1 (ROS 2 topics) |
| Why Unity for Robotics? | High-fidelity rendering; HRI research needs; where Gazebo falls short |
| Gazebo vs Unity: Choosing Your Simulator | Comparison table: 5 rows (physics accuracy, visual fidelity, ROS 2 integration, HRI research, sensor simulation) |
| The Unity Scene Hierarchy | Fenced text block (` ```text `) showing scene tree: Environment, Robot, ROSConnection, Lighting |
| ROS-TCP-Connector Bridge | How TCP socket connects Unity to ROS 2; bidirectional topic communication |
| Mermaid diagram | Unity-ROS 2 data flow (graph LR; UnityScene -> ROSTCPEndpoint -> ROS2Network -> back) |
| An HRI Scenario | Concrete example of photorealistic HRI study scenario |
| Summary | 6-row table (Unity, HRI, GameObject, Component, ArticulationBody, ROS-TCP-Connector) |

**Acceptance criteria**:
- Comparison table has exactly 5 rows and covers all 5 dimensions
- Scene hierarchy shown as fenced text block (not bare XML)
- Mermaid diagram shows bidirectional connection (<= 8 nodes)
- "When to use Gazebo vs Unity" guidance present

---

### Contract: Chapter 3 — Simulating Robot Sensors

**File**: `book/docs/module-2-digital-twin/chapter-3-sensors.md`
**Frontmatter**: `id: chapter-3-sensors`, `sidebar_position: 3`

Required sections (in order):

| Section | Content Requirement |
|---|---|
| Learning Objectives | 4 bullets: explain why simulate; name ROS 2 message types; read SDF sensor config; trace sensor data flow |
| Prerequisites | Module 1 (sensor_msgs) + Chapter 1 (Gazebo and SDF format) |
| Why Simulate Sensors? | Cost, repeatability, edge case coverage, same ROS 2 message format as real sensors |
| LiDAR: sensor_msgs/LaserScan | YAML block showing LaserScan message fields; XML block showing SDF lidar sensor config; topic `/scan` |
| RGBD Camera: sensor_msgs/Image | Table: stream / topic / message type (3 rows: color, depth, camera_info); XML SDF config snippet |
| IMU: sensor_msgs/Imu | YAML block showing Imu message fields; topic `/imu/data`; note on gravity in linear_acceleration.z |
| Mermaid diagram 1 | Sensor data flow (graph LR; GazeboPhysics -> SensorPlugin -> ROSBridge -> ROS2Topic -> 3 consumer nodes) |
| Mermaid diagram 2 | LiDAR scan sequence (sequenceDiagram; Gazebo -> SensorPlugin -> ROSBridge -> NavStack) |
| Summary | 7-row table (LiDAR, RGBD Camera, IMU, sensor_msgs/LaserScan, sensor_msgs/Image, Gazebo Sensor Plugin, TF Frame) |

**Acceptance criteria**:
- All three sensor types covered: LiDAR (LaserScan), RGBD (Image), IMU (Imu)
- All three ROS 2 topics named: `/scan`, `/camera/depth/image_raw`, `/imu/data`
- YAML message structure blocks have inline comments on each key field
- Both Mermaid diagrams render correctly (<= 8 nodes each)

---

## Validation Checklist (per chapter, before merge)

- [ ] Frontmatter: `id` and `sidebar_position` present and valid
- [ ] `## Learning Objectives` is first body section (exactly 4 bullets)
- [ ] `:::info Prerequisites` admonition present with correct links
- [ ] `## Summary` is last body section (minimum 6 rows)
- [ ] At least 1 Mermaid diagram present and renders via `npm run build`
- [ ] All code/config blocks ASCII-only (no non-ASCII characters)
- [ ] No bare XML angle brackets in prose or table cells
- [ ] All technical terms defined on first use
- [ ] `sidebar_position` is unique within `module-2-digital-twin/`
- [ ] `npm run build` completes without errors after adding this chapter
