# Research: Module 3 — The AI-Robot Brain (NVIDIA Isaac)

**Branch**: `003-module3-isaac-brain` | **Date**: 2026-03-09
**Phase**: 0 — Research & Unknowns Resolution

All unknowns from Technical Context resolved below.

---

## Decision 1: Isaac Sim Architecture Components

**Decision**: Present Isaac Sim as built on four technology pillars: Omniverse (collaborative simulation platform), USD (Universal Scene Description — the scene file format), RTX (NVIDIA's real-time ray tracing renderer), and PhysX (GPU-accelerated physics engine).

**Rationale**: These four pillars explain why Isaac Sim produces photorealistic images (RTX), physically accurate behavior (PhysX), interoperable scenes (USD), and multi-user workflows (Omniverse). They also explain the key differentiators vs. Gazebo.

**Alternatives considered**: Describe only the user-facing tools (Replicator, Robot Engine Bridge). Rejected — students need to understand WHY Isaac Sim looks and behaves differently from Gazebo; the four-pillar framing answers this clearly.

---

## Decision 2: Isaac Sim vs Gazebo Comparison Dimensions

**Decision**: Six-row comparison table covering: rendering quality, physics engine, scene format, AI training workflow, ROS 2 integration, and hardware requirements.

**Rationale**: These six dimensions capture the meaningful differences without going into product marketing. Rendering quality and AI training workflow are where Isaac Sim clearly wins; ROS 2 integration is where Gazebo wins (native vs. bridge). Balance is important for educational credibility.

**Alternatives considered**: Five rows (drop hardware requirements). Kept hardware requirements because GPU requirement is a real constraint students will encounter.

**Resolved values**:

| Dimension | Isaac Sim | Gazebo |
|---|---|---|
| Rendering | RTX ray tracing, PBR materials, photorealistic | Rasterization, basic materials, functional |
| Physics engine | PhysX (GPU-accelerated) | ODE / Bullet / DART (CPU) |
| Scene format | USD (Universal Scene Description) | SDF (Simulation Description Format) |
| AI training | Replicator synthetic data pipeline built-in | No built-in synthetic data tooling |
| ROS 2 integration | Via Isaac ROS bridge (ROS2 control bridge) | Native (gz-ros2-control, sensor plugins) |
| Hardware requirement | NVIDIA GPU required (RTX 3080 or better recommended) | CPU-based; GPU optional |

---

## Decision 3: Replicator Domain Randomization Content

**Decision**: Explain Replicator as a Python-scriptable domain randomization tool that varies four categories: lighting (intensity, color, position), materials (textures, reflectivity), object poses (position, rotation), and camera parameters (position, angle, focal length). Show an annotated Python-based YAML-style config snippet illustrating randomization parameters.

**Rationale**: Domain randomization is the key concept that makes synthetic data useful — models trained on randomized data generalize to real-world conditions. The four categories cover the major sources of real-world variation.

**Alternatives considered**: Show full Python Replicator API calls. Rejected — Python f-strings with curly braces cause MDX JSX parsing errors; a YAML-style config block is safer and more readable for students.

**Resolved Replicator label types**:
- Bounding Box 2D / 3D
- Semantic Segmentation (pixel-level labels)
- Instance Segmentation
- Depth (per-pixel distance)
- Surface Normals

---

## Decision 4: Isaac ROS GEM Overview Table

**Decision**: Four-row GEM overview table covering: `isaac_ros_visual_slam` (cuVSLAM), `isaac_ros_object_detection`, `isaac_ros_image_segmentation`, and `isaac_ros_depth_segmentation`.

**Rationale**: These four GEMs represent the core perception capabilities needed for a humanoid robot: know where you are (VSLAM), see what objects are nearby (detection), understand the scene at pixel level (segmentation), and measure depth (depth segmentation). Together they constitute a minimal autonomous perception stack.

**Alternatives considered**: Include more GEMs (stereo disparity, DNN stereo disparity). Kept to four for pedagogical clarity — more would overwhelm students without adding conceptual value.

**GPU fps context** (for CPU vs GPU comparison):
- Object detection on CPU: ~5 fps
- Object detection on GPU with Isaac ROS GEM: ~60 fps
- This 12x speedup motivates the entire GEM/NITROS architecture.

---

## Decision 5: cuVSLAM Pipeline — Five Steps

**Decision**: Decompose cuVSLAM into five sequential steps with one sentence each.

**Resolved five steps**:
1. **Feature Extraction**: Detect distinctive keypoints in each camera frame using GPU-accelerated ORB or similar descriptors.
2. **Feature Matching**: Match keypoints between consecutive frames to compute relative camera motion.
3. **Visual Odometry**: Accumulate frame-to-frame motion estimates to compute the robot's pose trajectory.
4. **Map Update**: Insert new keypoints and pose estimates into the sparse 3D feature map.
5. **Loop Closure**: Detect when the robot revisits a previously mapped area and correct accumulated drift.

**Rationale**: This decomposition maps directly to the standard SLAM literature (estimation, mapping, loop closure) while being accessible to students without a computer vision background.

**ROS 2 interface**:
- Input: `/camera/image_raw` (`sensor_msgs/Image`) + `/camera/camera_info`
- Output: `/visual_slam/tracking/odometry` (`nav_msgs/Odometry`) → consumed by Nav2 as `/odom`

---

## Decision 6: NITROS Zero-Copy Transport

**Decision**: Explain NITROS as a zero-copy transport layer that allows GPU-resident tensor data to pass between Isaac ROS nodes without CPU-GPU memory copies. Use a before/after comparison: without NITROS, each node reads from CPU RAM (slow); with NITROS, nodes share a GPU memory tensor handle (fast).

**Rationale**: NITROS is the key architectural innovation that makes Isaac ROS GEMs practical for real-time robotics. Students need to understand the performance reason for its existence.

**Resolved fps numbers for chapter text**:
- Traditional CPU pipeline (object detection): ~5 fps
- Isaac ROS GEM with NITROS: ~60 fps
- Improvement: 12x at typical 640x480 resolution

---

## Decision 7: Nav2 Architecture Components

**Decision**: Cover five Nav2 components: global costmap, local costmap, inflation radius, global planner (NavFn), and local planner/controller (DWB Controller).

**Resolved definitions**:
- **Global Costmap**: A full map of the environment; cells marked free, occupied, or unknown; used by global planner to find a complete path.
- **Local Costmap**: A small rolling window around the robot; updated in real time from sensor data (`/scan`); used by local controller for immediate obstacle avoidance.
- **Inflation Radius**: Buffer zone added around obstacles in the costmap; prevents the robot from planning paths that would require grazing obstacles.
- **NavFn Global Planner**: Dijkstra's algorithm on the costmap; computes the globally optimal path from start to goal.
- **DWB Controller (local planner)**: Dynamic Window Approach B; samples candidate velocity commands, simulates trajectories, scores each by distance to goal and clearance from obstacles, executes the best one.

**Nav2 topic interface** (for chapter table):

| Topic | Direction | Message Type | Purpose |
|---|---|---|---|
| `/map` | Subscribe | `nav_msgs/OccupancyGrid` | Static map from SLAM |
| `/odom` | Subscribe | `nav_msgs/Odometry` | Robot pose from cuVSLAM |
| `/scan` | Subscribe | `sensor_msgs/LaserScan` | LiDAR for local costmap |
| `/goal_pose` | Subscribe | `geometry_msgs/PoseStamped` | Navigation goal from planner |
| `/cmd_vel` | Publish | `geometry_msgs/Twist` | Velocity commands to robot base |

---

## Decision 8: Recovery Behaviors

**Decision**: Name three recovery behaviors: Spin (rotate in place to clear sensor artifacts), Back Up (drive backward to escape stuck state), and Clear Costmap (reset the local costmap to remove transient obstacle detections).

**Rationale**: These three cover the most common stuck scenarios and are the default Nav2 recovery behavior tree nodes.

---

## MDX / Windows Constraints (carried forward from Module 2)

- ASCII-only in all fenced code blocks (no em-dashes, curly quotes, unicode)
- No bare XML angle brackets in prose or table cells
- Relative links use `.md` extension in category index
- Mermaid node IDs: camelCase or underscores, maximum 8 nodes per diagram
- YAML blocks for config examples (safer than Python f-strings in MDX)
- System prompt / JSON examples in chapter 2: use `text` fence, not `json`, if content has curly braces in prose context

---

## Chapter Narrative Arc

- **Chapter 1 (Isaac Sim)**: The training ground — before the robot can see the real world, it trains its eyes on a simulated one.
- **Chapter 2 (Isaac ROS)**: The perception engine — GPU-accelerated vision that knows where the robot is and what is around it.
- **Chapter 3 (Nav2)**: The navigation system — the robot consumes pose from Chapter 2 and moves autonomously through the world.

Chapters cross-reference each other: Chapter 2 references Isaac Sim training data (Ch 1); Chapter 3 references cuVSLAM pose output (Ch 2).
