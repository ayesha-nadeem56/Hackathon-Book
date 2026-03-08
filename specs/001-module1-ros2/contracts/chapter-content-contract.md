# Content Contract: Chapter Structure

**Feature**: `001-module1-ros2`
**Date**: 2026-03-07
**Type**: Content Schema Contract (static documentation — no API endpoints)

This contract defines the mandatory structure every chapter file MUST conform to.
It serves as the acceptance contract for the `/sp.tasks` implementation tasks.

---

## Chapter File Contract

### Frontmatter (required fields)

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | string | Yes | Unique across all docs; format: `chapter-<N>-<slug>` |
| `title` | string | Yes | Format: `"Chapter N — <Title>"` |
| `sidebar_position` | integer | Yes | Unique within module directory; 1-based |
| `description` | string | Yes | 1 sentence; used in SEO and sidebar tooltip |
| `tags` | string[] | Yes | MUST include `ros2` and `module-1` |

### Body Sections (ordered, all required)

| Order | Section Heading | Required Content |
|---|---|---|
| 1 | `## Learning Objectives` | Bulleted list of 3–5 measurable learning outcomes |
| 2–N | Content sections | Prose + at least one diagram (Mermaid) and one code block where applicable |
| Last | `## Summary` | Table with 2 columns: Concept \| Key Takeaway (min 3 rows) |

### Code Block Contract

| Attribute | Rule |
|---|---|
| Language tag | `python` for rclpy; `xml` for URDF; `bash` for shell |
| `title` | Required on all blocks; filename or descriptive label |
| `showLineNumbers` | Required on blocks with >5 lines |
| Inline comments | MUST explain each logical step (not just describe what the line does) |
| ROS 2 version note | MUST appear as comment in first line of all rclpy examples |
| Validation | Python: `py_compile`; XML/URDF: `xmllint --noout` |

### Diagram Contract

| Attribute | Rule |
|---|---|
| Type | Mermaid code block (```mermaid) |
| Frequency | At least 1 per chapter |
| Accuracy | MUST represent concept described in surrounding prose |
| Validation | Must render without errors via `docusaurus build` |

---

## Module 1 Chapter Contracts

### Contract: Chapter 1 — Introduction to ROS 2

**File**: `book/docs/module-1-ros2/chapter-1-intro.md`

Required sections (in order):

| Section | Content Requirement |
|---|---|
| Learning Objectives | 3–5 bullets covering middleware, ROS 2 rationale, architecture, nodes/topics |
| What is Middleware? | Defines middleware; explains role in robotics |
| Why ROS 2? | Compares ROS 2 to alternatives; lists key advantages |
| ROS 2 Architecture Overview | Mermaid architecture diagram REQUIRED; describes DDS layer |
| Nodes, Topics, and Message Passing | Defines node, topic, message; explains pub/sub pattern |
| Real-World Example | Concrete humanoid robot scenario (e.g., walking command flow) |
| Summary | Table with ≥5 concepts defined |

### Contract: Chapter 2 — ROS 2 Communication Model

**File**: `book/docs/module-1-ros2/chapter-2-communication.md`

Required sections (in order):

| Section | Content Requirement |
|---|---|
| Learning Objectives | 3–5 bullets covering nodes, pub/sub, services, rclpy, AI-ROS |
| Understanding Nodes | Deep dive on node lifecycle, naming, namespaces |
| Topics: Publishers and Subscribers | Mermaid sequence diagram REQUIRED; pub/sub pattern |
| Services: Request-Response | Explains synchronous service calls vs async topics |
| Python Examples with rclpy | Min 2 code blocks: publisher node + subscriber node (ROS 2 Humble) |
| AI Agent and ROS Controller Interaction | Explains how AI decisions become ROS messages |
| Summary | Table with ≥5 concepts defined |

**Python example acceptance criteria**:
- Publisher node: defines a Node subclass, creates publisher, publishes on timer
- Subscriber node: defines a Node subclass, creates subscription, prints received message
- Both examples: pass `python -m py_compile` without errors
- Both examples: include ROS 2 Humble compatibility comment

### Contract: Chapter 3 — Robot Structure and URDF

**File**: `book/docs/module-1-ros2/chapter-3-urdf.md`

Required sections (in order):

| Section | Content Requirement |
|---|---|
| Learning Objectives | 3–5 bullets covering URDF purpose, links/joints, humanoid model, ROS 2 integration |
| What is URDF? | Defines URDF; explains XML format and purpose |
| Links and Joints | Defines `<link>` and `<joint>`; covers joint types (fixed, revolute, continuous, prismatic) |
| Humanoid Robot Representation | Explains how a humanoid body maps to URDF links/joints |
| Sample URDF: Simplified Humanoid | Complete XML code block (see URDF contract below); Mermaid hierarchy diagram REQUIRED |
| Integration with ROS 2 | Explains `robot_state_publisher`, `joint_state_publisher`, TF2 |
| Summary | Table with ≥5 concepts defined |

**URDF sample acceptance criteria**:
- Valid XML (passes `xmllint --noout`)
- Contains `<robot name="...">` root element
- Contains at least 7 named `<link>` elements: `base_link`, `torso`, `head`, `left_arm`, `right_arm`, `left_leg`, `right_leg`
- Contains at least 6 `<joint>` elements connecting the links with appropriate types
- Each joint specifies `parent`, `child`, and `origin`
- Code block uses `title="humanoid_robot.urdf"` attribute

---

## Validation Checklist (per chapter, before merge)

- [ ] Frontmatter: all 5 required fields present and valid
- [ ] `## Learning Objectives` section is first body section
- [ ] `## Summary` section is last body section with concept table
- [ ] At least 1 Mermaid diagram present and renders cleanly
- [ ] All Python code: `python -m py_compile <file>` passes
- [ ] All XML/URDF code: `xmllint --noout` passes
- [ ] All code blocks have `title` attribute
- [ ] No placeholder text (`TODO`, `[placeholder]`, `...`) in final version
- [ ] All technical terms defined on first use
- [ ] Prerequisite callouts link to prior chapters where concepts are assumed
- [ ] `sidebar_position` is unique within module directory
- [ ] `docusaurus build` completes without errors after adding this chapter
