# Research: Module 2 — The Digital Twin (Gazebo & Unity)

**Date**: 2026-03-08
**Branch**: `002-module2-digital-twin`

All unknowns from the Technical Context section resolved below.

---

## Decision 1: Digital Twin Definition Scope

**Decision**: Define a digital twin as a software replica that mirrors the physical robot's geometry, dynamics, and sensor outputs in real time.

**Rationale**: This definition is the consensus in robotics literature (ROS 2 ecosystem, IEEE publications). It scopes the concept to what Gazebo and Unity actually provide without over-reaching into industrial IoT twin definitions (asset management, telemetry dashboards).

**Alternatives considered**:
- Broader IoT/industrial twin definition (includes asset lifecycle) — rejected as out of scope for a robotics simulation module.
- Narrower "URDF replica" definition — too narrow; misses sensor simulation and physics.

---

## Decision 2: Gazebo Sensor Message Types

**Decision**: Use the following standard ROS 2 message types for sensor chapters:

| Sensor | ROS 2 Topic | Message Type | Notes |
|---|---|---|---|
| LiDAR (2D planar) | `/scan` | `sensor_msgs/LaserScan` | Simpler than PointCloud2 for introductory content |
| LiDAR (3D) | `/points` | `sensor_msgs/PointCloud2` | Mention briefly; primary example uses LaserScan |
| Depth Camera (RGB) | `/camera/image_raw` | `sensor_msgs/Image` | Standard RGB frame |
| Depth Camera (Depth) | `/camera/depth/image_raw` | `sensor_msgs/Image` | 16-bit depth in mm |
| IMU | `/imu/data` | `sensor_msgs/Imu` | Linear acceleration + angular velocity + orientation quaternion |

**Rationale**: These are the canonical Gazebo classic (Gazebo 11, ROS 2 Humble) plugin output topics, aligned with ROS 2 REP-103 coordinate conventions. Using `LaserScan` for the primary LiDAR example reduces complexity for students.

**Alternatives considered**:
- Only covering PointCloud2 — too complex for introductory content; LaserScan is clearer.
- Custom topic names — rejected; canonical names match what students will see in real labs.

---

## Decision 3: Unity ROS Integration Mechanism

**Decision**: Reference Unity Robotics Hub (ROS-TCP-Connector) as the integration bridge. Describe at the conceptual data flow level; no Unity C# API details.

**Rationale**: ROS-TCP-Connector is the official Unity Technologies / Microsoft supported package for ROS 2 integration. It serializes ROS 2 messages and routes them over TCP between a ROS 2 endpoint node and the Unity runtime. This is well-documented and the de facto standard.

**Alternatives considered**:
- ROS2-For-Unity (direct native plugin) — more performant but complex; not yet mainstream in education.
- Unity ML-Agents — different purpose (reinforcement learning, not ROS 2 communication); out of scope.

**Data flow** (to be rendered as Mermaid in chapter-2):
```
Unity Scene (GameObjects)
  → Unity Robotics Hub (ROS-TCP-Connector package)
    → ROS-TCP-Endpoint node (running in ROS 2)
      → ROS 2 topic graph (/cmd_vel, /joint_states, etc.)
        → Robot controller node
          → Actuator commands
            → Unity Scene (updated robot pose)
```

---

## Decision 4: Gazebo World File Format

**Decision**: Reference SDF (Simulation Description Format) as the Gazebo world/model format. Show a minimal annotated SDF snippet for a world with one robot model and a physics plugin.

**Rationale**: SDF is Gazebo Classic's native format (URDF is converted to SDF internally by Gazebo). Students will see SDF when they open `.world` files. Showing a minimal example makes the concept concrete without requiring deep SDF authorship.

**Constraints**: SDF XML angle brackets (`<world>`, `<model>`, `<plugin>`) must be wrapped in backtick inline code when referenced in prose, and only used inside fenced code blocks in chapter text (MDX v3 rule).

---

## Decision 5: LiDAR Output Format for Chapter 3

**Decision**: Primary explanation uses `sensor_msgs/LaserScan` (2D planar scan). Mention `sensor_msgs/PointCloud2` in one sentence as the 3D variant.

**Rationale**: LaserScan is simpler (array of range values + angle metadata) and maps to the most common indoor navigation use case students will encounter. PointCloud2 is more common in research but its binary field format is confusing for first exposure.

**LaserScan message structure** (for chapter accuracy):
```
sensor_msgs/LaserScan:
  header:
    stamp: time
    frame_id: "laser_link"
  angle_min: float32        # Start angle of scan [rad]
  angle_max: float32        # End angle of scan [rad]
  angle_increment: float32  # Angular distance between samples [rad]
  time_increment: float32   # Time between measurements [s]
  range_min: float32        # Minimum valid range [m]
  range_max: float32        # Maximum valid range [m]
  ranges: float32[]         # Array of range measurements [m]
  intensities: float32[]    # Array of intensity measurements
```

---

## Decision 6: Chapter-3 Prerequisite Scope

**Decision**: Chapter 3 requires Module 1 completion (ROS 2 topics/subscribers) AND Chapter 1 of this module (Gazebo as the host simulator). Both prerequisites will be noted in a `:::note Prerequisites` admonition.

**Rationale**: Without understanding ROS 2 topics, the sensor data flow (sensor → topic → subscriber node) is meaningless. Without Gazebo context (Chapter 1), the simulation host is unknown.

---

## Windows / MDX Compatibility (Lesson-Learned Rules)

These are not decisions — they are hard constraints carried forward from Module 1:

1. **ASCII-only in fenced code blocks**: No em-dash (`—`), curly quotes (`""`), or other non-ASCII. Use plain hyphen (`-`) in comments.
2. **No bare angle brackets in prose or table cells**: `<link>`, `<joint>`, `<world>` etc. must be wrapped in backticks: `` `<link>` `` or placed only inside fenced code blocks.
3. **Relative links use `.md` extension**: In category index pages (`index.md`), links to sibling chapters must use `./chapter-1-gazebo.md` (not `./chapter-1-gazebo`) for correct Docusaurus resolution.
