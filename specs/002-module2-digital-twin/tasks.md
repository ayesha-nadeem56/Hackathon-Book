# Tasks: Module 2 — The Digital Twin (Gazebo & Unity)

**Input**: Design documents from `specs/002-module2-digital-twin/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-content-contract.md
**Tests**: Not requested — documentation module; build gate (`npm run build`) is the acceptance test.
**Organization**: Tasks grouped by user story to enable independent authoring and testing of each chapter.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Module Directory Structure)

**Purpose**: Create module directory and sidebar descriptor so Docusaurus recognizes the module.

- [x] T001 Create module directory `book/docs/module-2-digital-twin/`
- [x] T002 Create `book/docs/module-2-digital-twin/_category_.json` with position 2, label "Module 2: The Digital Twin", collapsible true, collapsed false, description "Gazebo physics simulation, Unity environments, and simulated sensors for robotics"

**Checkpoint**: Module directory and `_category_.json` exist; `npm run start` shows Module 2 in sidebar at position 2.

---

## Phase 2: Foundational (Module Landing Page)

**Purpose**: Create `index.md` module landing page — required before chapters can cross-link correctly.

**CRITICAL**: Chapter files link back to the index; index.md must exist before build validation.

- [x] T003 Create `book/docs/module-2-digital-twin/index.md` with frontmatter (`id: module-2-overview`, `sidebar_position: 0`), digital twin concept narrative, prerequisites admonition (Module 1), 3-row chapter overview table (Chapter / Tool / Role), 5 module learning outcomes, and CTA link to `./chapter-1-gazebo.md`

**Checkpoint**: Foundation ready — `npm run start` renders Module 2 landing page with working prerequisites and chapter table.

---

## Phase 3: User Story 1 — Digital Twins and Gazebo Physics (Priority: P1) MVP

**Goal**: Chapter 1 teaches students what a digital twin is, why physics simulation matters before real-world deployment, and how Gazebo simulates robot dynamics.

**Independent Test**: A student who reads only Chapter 1 can answer: "What is a digital twin?", "What four physical phenomena does Gazebo simulate?", "What is an SDF world file?"

### Implementation for User Story 1

- [x] T004 [US1] Create `book/docs/module-2-digital-twin/chapter-1-gazebo.md` with frontmatter (`id: chapter-1-gazebo`, `sidebar_position: 1`) and all required sections in order:
  - Exactly 4 Learning Objectives bullet points
  - Prerequisites admonition linking to Module 1 (ROS 2 topics and publisher/subscriber)
  - "What is a Digital Twin?" section: definition; software replica mirroring geometry, dynamics, sensors; why simulate before deploying on real hardware
  - "Gazebo: A Physics Simulator" section: Gazebo overview; ROS 2 native integration; 4 physics properties defined (gravity, collisions, inertia, friction)
  - "The Gazebo World File (SDF)" section: annotated XML snippet (xml tag) showing world, model, physics, include elements with inline comments
  - Gazebo Plugins table: minimum 4 rows; columns: Plugin / Purpose / ROS 2 Output Topic
  - Mermaid diagram 1: Digital twin feedback loop (graph LR; PhysicalRobot and DigitalTwin both connecting to ROS2Network, max 8 nodes)
  - Mermaid diagram 2: Gazebo simulation loop (graph TD; PhysicsStep → Sensors → ROS2Bridge → Planner → Commands → back to PhysicsStep, max 8 nodes)
  - Summary table: minimum 7 rows (Digital Twin, Gazebo, SDF, Gravity, Inertia, Friction, Gazebo Plugin)

**Checkpoint**: Chapter 1 complete — `npm run start` renders chapter; all 3 acceptance scenarios from spec.md answerable from text; SDF snippet renders without MDX parse errors.

---

## Phase 4: User Story 2 — High-Fidelity Environments with Unity (Priority: P2)

**Goal**: Chapter 2 teaches students why Unity is used for high-fidelity HRI environments and how it connects to the ROS 2 ecosystem via ROS-TCP-Connector.

**Independent Test**: A student who reads only Chapter 2 can name 2 differences between Gazebo and Unity, explain what ROS-TCP-Connector does, and describe a Unity scene hierarchy.

### Implementation for User Story 2

- [x] T005 [US2] Create `book/docs/module-2-digital-twin/chapter-2-unity.md` with frontmatter (`id: chapter-2-unity`, `sidebar_position: 2`) and all required sections in order:
  - Exactly 4 Learning Objectives bullet points
  - Prerequisites admonition linking to Chapter 1 (this module) and Module 1 (ROS 2 topics)
  - "Why Unity for Robotics?" section: high-fidelity rendering rationale; HRI research needs; where Gazebo falls short (visual fidelity, photorealism)
  - "Gazebo vs Unity: Choosing Your Simulator" comparison table: exactly 5 rows covering physics accuracy, visual fidelity, ROS 2 integration, HRI research, sensor simulation
  - "The Unity Scene Hierarchy" section: fenced text block (text tag) showing scene tree (Environment / Robot / ROSConnection / Lighting nodes); NOT bare XML
  - "ROS-TCP-Connector Bridge" section: how TCP socket connects Unity to ROS 2; bidirectional topic communication explained
  - Mermaid diagram: Unity-ROS 2 data flow (graph LR; UnityScene → ROSTCPEndpoint → ROS2Network with return path, max 8 nodes)
  - "An HRI Scenario" section: concrete example of photorealistic human-robot interaction study
  - Summary table: minimum 6 rows (Unity, HRI, GameObject, Component, ArticulationBody, ROS-TCP-Connector)

**Checkpoint**: Chapter 2 complete — `npm run start` renders chapter; comparison table has exactly 5 rows; "when to use Gazebo vs Unity" guidance present; no MDX parse errors.

---

## Phase 5: User Story 3 — Simulated Sensors and Perception (Priority: P3)

**Goal**: Chapter 3 teaches students how LiDAR, RGBD camera, and IMU sensors are simulated in Gazebo and how simulated sensor data flows into the ROS 2 topic graph.

**Independent Test**: A student who reads only Chapter 3 (with Module 1 knowledge) can name the ROS 2 topic and message type for each of the three sensor types and trace the data flow from simulator to ROS 2 consumer.

### Implementation for User Story 3

- [x] T006 [US3] Create `book/docs/module-2-digital-twin/chapter-3-sensors.md` with frontmatter (`id: chapter-3-sensors`, `sidebar_position: 3`) and all required sections in order:
  - Exactly 4 Learning Objectives bullet points
  - Prerequisites admonition linking to Module 1 (sensor_msgs) and Chapter 1 (Gazebo and SDF format)
  - "Why Simulate Sensors?" section: cost, repeatability, edge case coverage, same ROS 2 message format as real sensors
  - "LiDAR: sensor_msgs/LaserScan" section: YAML block (yaml tag) showing LaserScan message fields with inline comments; XML SDF config snippet (xml tag); topic `/scan` named explicitly
  - "RGBD Camera: sensor_msgs/Image" section: 3-row table (columns: Stream / Topic / Message Type; rows: color, depth, camera_info); XML SDF config snippet
  - "IMU: sensor_msgs/Imu" section: YAML block showing Imu message fields with inline comments; topic `/imu/data`; note on gravity in `linear_acceleration.z`
  - Mermaid diagram 1: Sensor data flow (graph LR; GazeboPhysics → SensorPlugin → ROSBridge → ROS2Topic → consumer nodes, max 8 nodes)
  - Mermaid diagram 2: LiDAR scan sequence diagram (sequenceDiagram; Gazebo → SensorPlugin → ROSBridge → NavStack, max 8 nodes)
  - Summary table: minimum 7 rows (LiDAR, RGBD Camera, IMU, sensor_msgs/LaserScan, sensor_msgs/Image, Gazebo Sensor Plugin, TF Frame)

**Checkpoint**: Chapter 3 complete — `npm run start` renders chapter; all three ROS 2 topics named (/scan, /camera/depth/image_raw, /imu/data); both Mermaid diagrams render; no MDX parse errors.

---

## Phase 6: Polish & Build Validation

**Purpose**: Cross-cutting content validation and full Docusaurus build check.

- [x] T007 [P] Validate all chapter files against contracts/chapter-content-contract.md checklist (10 items): sidebar_position uniqueness, 4 Learning Objectives each, prerequisite admonitions, Summary tables min 6 rows, no bare XML angle brackets, all fenced blocks ASCII-only, all Mermaid diagrams max 8 nodes
- [x] T008 [P] Run `npm run build` from `book/` directory and confirm zero errors and zero broken links; fix any issues found

**Checkpoint**: All 5 module files authored and validated; `npm run build` passes with zero errors and zero broken links. Module 2 ready for merge to main.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately (T001, T002)
- **Foundational (Phase 2)**: Depends on Phase 1 completion — T003 after T001/T002
- **User Stories (Phases 3–5)**: All depend on Foundational (T003) completion
  - T004, T005, T006 can proceed in parallel once T003 is complete (different files)
- **Polish (Phase 6)**: Depends on T004, T005, T006 all complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependencies on US2 or US3
- **US2 (P2)**: Can start after Phase 2 — references US1 via prerequisite admonition (text only)
- **US3 (P3)**: Can start after Phase 2 — references US1 via prerequisite admonition (text only)

### Parallel Opportunities

- T001, T002 (Phase 1) — parallel
- T004, T005, T006 (Phases 3–5) — all parallel once T003 complete (each is a separate file)
- T007, T008 (Phase 6) — T007 before T008

---

## Parallel Example: User Stories 1–3

```text
After T003 (index.md) is complete:

  Parallel execution:
    Task T004: chapter-1-gazebo.md    (Digital Twin + SDF + 2 Mermaid)
    Task T005: chapter-2-unity.md     (Unity + comparison table + Mermaid)
    Task T006: chapter-3-sensors.md   (LiDAR + RGBD + IMU + 2 Mermaid)

  Then sequentially:
    Task T007: Content validation against contracts checklist
    Task T008: npm run build -- must pass zero errors, zero broken links
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003 — index.md)
3. Complete Phase 3: User Story 1 (T004 — chapter-1-gazebo.md)
4. **STOP and VALIDATE**: `npm run start`; confirm Chapter 1 renders correctly with all contract elements
5. Extend to US2 and US3 once US1 validated

### Incremental Delivery

1. T001–T003 → Module 2 shell visible in sidebar
2. T004 → Chapter 1 live (Gazebo + Digital Twin) — independently readable
3. T005 → Chapter 2 live (Unity + HRI) — independently readable
4. T006 → Chapter 3 live (Sensors) — independently readable
5. T007–T008 → Full build validation, ready for merge

---

## Notes

- [P] tasks operate on different files — no merge conflicts possible
- Each chapter task (T004, T005, T006) is a complete chapter file — test by reading the rendered page
- All YAML and XML code blocks must be ASCII-only (no em-dashes, curly quotes, Unicode)
- No bare XML angle brackets in prose or tables (MDX v3 JSX parser rule) — use backtick inline code for XML tag names
- Mermaid node IDs: camelCase or underscores only; maximum 8 nodes per diagram
- Unity scene hierarchy block: use `text` fence tag, NOT XML or bare angle brackets
- Relative links in index.md must use `.md` extension (e.g., `./chapter-1-gazebo.md`)
