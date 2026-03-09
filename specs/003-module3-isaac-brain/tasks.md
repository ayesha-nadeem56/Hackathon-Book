# Tasks: Module 3 — The AI-Robot Brain (NVIDIA Isaac)

**Input**: Design documents from `specs/003-module3-isaac-brain/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-content-contract.md

**Organization**: Tasks are grouped by user story to enable independent authoring and testing of each chapter.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Module Directory Structure)

**Purpose**: Create module directory and sidebar descriptor so Docusaurus recognizes the module.

- [ ] T001 Create module directory `book/docs/module-3-isaac-brain/`
- [ ] T002 Create `book/docs/module-3-isaac-brain/_category_.json` with position 3, label "Module 3: The AI-Robot Brain", collapsible true, collapsed false

**Checkpoint**: Module directory and `_category_.json` exist; `npm run start` shows Module 3 in sidebar at position 3.

---

## Phase 2: Foundational (Module Landing Page)

**Purpose**: Create `index.md` module landing page — required before chapters can cross-link correctly.

**CRITICAL**: Chapter files link back to the index; index.md must exist before build validation.

- [ ] T003 Create `book/docs/module-3-isaac-brain/index.md` with frontmatter (`id: module-3-overview`, `sidebar_position: 0`), three-layer brain narrative, prerequisites admonition (Modules 1 and 2), 3-row chapter overview table, 5 module learning outcomes, and CTA link to `./chapter-1-isaac-sim.md`

**Checkpoint**: Foundation ready — `npm run start` renders Module 3 landing page with working prerequisites and chapter table.

---

## Phase 3: User Story 1 — Isaac Sim and Synthetic Data (Priority: P1) MVP

**Goal**: Chapter 1 teaches students Isaac Sim architecture, synthetic data rationale, and Replicator domain randomization.

**Independent Test**: A student who reads only Chapter 1 can answer: "What is synthetic data?", "What does Replicator do?", "When would you choose Isaac Sim over Gazebo?"

### Implementation for User Story 1

- [ ] T004 [US1] Create `book/docs/module-3-isaac-brain/chapter-1-isaac-sim.md` with frontmatter (`id: chapter-1-isaac-sim`, `sidebar_position: 1`) and all required sections in order:
  - Exactly 4 Learning Objectives bullet points
  - Prerequisites admonition linking to Module 1 and Module 2
  - "What is NVIDIA Isaac Sim?" section: four pillars (Omniverse, USD, RTX, PhysX) each defined
  - "Isaac Sim vs Gazebo" 6-row comparison table: Rendering, Physics engine, Scene format, AI training, ROS 2 integration, Hardware requirement
  - "Why Synthetic Data?" section: data problem (expensive/slow/dangerous) + synthetic data as solution
  - "Replicator: Domain Randomization" section: 4 randomization categories, label types table (5+ rows), annotated YAML config block (yaml tag, ASCII-only, first-line comment)
  - "Where Isaac Sim Fits in the Pipeline" section linking to Chapter 2
  - Mermaid diagram 1: Replicator pipeline (`graph LR`: IsaacSim --> Replicator --> DomainRandomization --> SyntheticDataset --> AIModelTraining, max 8 nodes)
  - Mermaid diagram 2: Chapter arc (`graph LR`: IsaacSim --> SyntheticData --> IsaacROS --> RealWorldPerception --> Nav2 --> AutonomousNavigation, max 8 nodes)
  - Summary table: minimum 7 rows (Isaac Sim, Omniverse, USD, RTX, Replicator, Synthetic Data, Domain Randomization)

**Checkpoint**: Chapter 1 complete — `npm run start` renders chapter; all 3 acceptance scenarios from spec.md are answerable from the text; no MDX parse errors.

---

## Phase 4: User Story 2 — Isaac ROS GPU-Accelerated Perception (Priority: P2)

**Goal**: Chapter 2 teaches students GEMs, NITROS zero-copy transport, and the 5-step cuVSLAM pipeline.

**Independent Test**: A student who reads only Chapter 2 can name the 5 cuVSLAM steps, explain what a GEM is, and explain why NITROS improves fps.

### Implementation for User Story 2

- [ ] T005 [US2] Create `book/docs/module-3-isaac-brain/chapter-2-isaac-ros.md` with frontmatter (`id: chapter-2-isaac-ros`, `sidebar_position: 2`) and all required sections in order:
  - Exactly 4 Learning Objectives bullet points
  - Prerequisites admonition linking to Chapter 1 (Isaac Sim synthetic data)
  - "What is Isaac ROS?" section: ROS 2 GPU-accelerated packages; 5 fps (CPU) vs 60 fps (GPU) fps comparison stated explicitly; "GEM" defined as "GPU-Enabled Module"
  - "NITROS: Zero-Copy Transport" section: "NVIDIA Isaac Transport for ROS" defined; before/after memory copy explanation; 12x speedup rationale
  - "Isaac ROS GEMs" 4-row table: columns Package / Capability / Key Output Topic; rows: isaac_ros_visual_slam, isaac_ros_object_detection, isaac_ros_image_segmentation, isaac_ros_depth_segmentation
  - "cuVSLAM: Visual SLAM on GPU" section: exactly 5-step pipeline prose (Feature Extraction, Feature Matching, Visual Odometry, Map Update, Loop Closure), one paragraph per step; ROS 2 input/output topics in backticks
  - "Launching Isaac ROS cuVSLAM" annotated bash block: `ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam.launch.py` with comment above (bash tag, ASCII-only)
  - Mermaid diagram 1: cuVSLAM pipeline (`graph LR`: FeatureExtraction --> FeatureMatching --> VisualOdometry --> MapUpdate --> LoopClosure --> /odom --> Nav2, max 8 nodes)
  - Mermaid diagram 2: Isaac ROS perception pipeline (`graph LR` with /camera, NITROS, cuVSLAM, ObjectDetection, /odom nodes, max 8 nodes)
  - Summary table: minimum 7 rows (Isaac ROS, GEM, NITROS, cuVSLAM, Feature Extraction, Loop Closure, Visual Odometry)

**Checkpoint**: Chapter 2 complete — `npm run start` renders chapter; 3 acceptance scenarios from spec.md answerable from text; cuVSLAM 5 steps nameable from the chapter.

---

## Phase 5: User Story 3 — Nav2 Autonomous Navigation (Priority: P3)

**Goal**: Chapter 3 teaches students Nav2 architecture, costmaps, planners, topic interface, and recovery behaviors.

**Independent Test**: A student who reads only Chapter 3 (with Module 1 knowledge) can explain the difference between global and local costmap, describe NavFn vs DWB, and list 3 recovery behaviors.

### Implementation for User Story 3

- [ ] T006 [US3] Create `book/docs/module-3-isaac-brain/chapter-3-nav2.md` with frontmatter (`id: chapter-3-nav2`, `sidebar_position: 3`) and all required sections in order:
  - Exactly 4 Learning Objectives bullet points
  - Prerequisites admonition linking to Chapter 2 (cuVSLAM /odom output) and Module 1 (ROS 2 topics)
  - "What is Nav2?" section: ROS 2 navigation stack; successor to move_base; receives `/odom` from cuVSLAM; outputs `/cmd_vel`
  - "Costmaps" section: global costmap (full map, cells free/occupied/unknown); local costmap (rolling window from sensor data); inflation radius defined
  - "Planners and Controllers" section: NavFn global planner (Dijkstra's algorithm on global costmap); DWB Controller (sample velocities, simulate trajectories, score by goal distance + clearance, execute best)
  - "Nav2 Topics" 5-row table: columns Topic / Direction / Message Type / Purpose; rows: /map, /odom, /scan, /goal_pose, /cmd_vel
  - "Obstacle Avoidance and Recovery" section: local replanning on obstacle detection; three recovery behaviors (Spin, Back Up, Clear Costmap) each defined
  - Mermaid diagram 1: Nav2 architecture (`graph LR`: GlobalCostmap + LocalCostmap --> NavFn --> DWBController --> /cmd_vel, max 8 nodes)
  - Mermaid diagram 2: Navigation sequence diagram (4 participants: Goal, Nav2, LocalPlanner, Robot; obstacle detection + recovery steps)
  - Annotated YAML costmap config block: yaml tag, first-line comment, inline comments on inflation_radius/resolution/update_frequency, ASCII-only
  - Summary table: minimum 7 rows (Nav2, Global Costmap, Local Costmap, Inflation Radius, NavFn, DWB Controller, Recovery Behavior)

**Checkpoint**: Chapter 3 complete — `npm run start` renders chapter; 3 acceptance scenarios from spec.md answerable from text; student can sketch Nav2 architecture from memory.

---

## Phase 6: Polish & Build Validation

**Purpose**: Cross-cutting content validation and full Docusaurus build check.

- [ ] T007 [P] Validate all chapter files against contracts/chapter-content-contract.md checklist (11 items): sidebar_position uniqueness, 4 Learning Objectives each, prerequisite admonitions, Summary tables min 7 rows, no bare XML angle brackets, all fenced blocks ASCII-only
- [ ] T008 [P] Run `npm run build` from `book/` directory and confirm zero errors and zero broken links; fix any issues found

**Checkpoint**: All 5 module files authored and validated; `npm run build` passes with zero errors and zero broken links. Module 3 ready for merge to main.

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
- **US2 (P2)**: Can start after Phase 2 — references US1 via prerequisite admonition (text only, not a code dependency)
- **US3 (P3)**: Can start after Phase 2 — references US2 via prerequisite admonition (text only, not a code dependency)

### Parallel Opportunities

- T001, T002 (Phase 1) — parallel
- T004, T005, T006 (Phases 3–5) — all parallel once T003 complete (each is a separate file)
- T007, T008 (Phase 6) — run after all chapters complete; T007 before T008

---

## Parallel Example: User Stories 1–3

```text
After T003 (index.md) is complete:

  Parallel execution:
    Task T004: chapter-1-isaac-sim.md  (Isaac Sim + Replicator)
    Task T005: chapter-2-isaac-ros.md  (GEMs + cuVSLAM + NITROS)
    Task T006: chapter-3-nav2.md       (Costmaps + NavFn + DWB)

  Then sequentially:
    Task T007: Content validation against contracts checklist
    Task T008: npm run build -- must pass zero errors, zero broken links
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003 — index.md)
3. Complete Phase 3: User Story 1 (T004 — chapter-1-isaac-sim.md)
4. **STOP and VALIDATE**: `npm run start`; confirm Chapter 1 renders correctly with all contract elements
5. Extend to US2 and US3 once US1 validated

### Incremental Delivery

1. T001–T003 → Module 3 shell visible in sidebar
2. T004 → Chapter 1 live (Isaac Sim) — independently readable
3. T005 → Chapter 2 live (Isaac ROS) — independently readable
4. T006 → Chapter 3 live (Nav2) — independently readable
5. T007–T008 → Full build validation, ready for merge

---

## Notes

- [P] tasks operate on different files — no merge conflicts possible
- Each chapter task (T004, T005, T006) is a complete chapter file — test by reading the rendered page
- All YAML and bash code blocks must be ASCII-only (no em-dashes, curly quotes, Unicode)
- No bare XML angle brackets in prose or tables (MDX v3 JSX parser rule)
- Mermaid node IDs: camelCase or underscores only; maximum 8 nodes per diagram
- Relative links in index.md must use `.md` extension (e.g., `./chapter-1-isaac-sim.md`)
