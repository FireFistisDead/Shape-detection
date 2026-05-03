# Mandatory Technical Report: The Debug & Prompt Log

**Candidate Evaluation: Robotics Software Assignment**
**Focus Area: Perception-to-Action Pipeline for Ackermann Mobile Robots**

---

## 1. Initial AI Prompts Used
The project was initiated using a high-level architectural prompt designed to establish the ROS 2 Jazzy workspace and Gazebo Harmonic environment:

> *"Objective: Design and implement a complete ROS 2 perception-to-action pipeline. You must reconstruct a partially stripped simulation architecture using `ack.urdf.xacro` and `shapes.sdf`. Integrate correct Gazebo control and camera plugins for ROS 2 Jazzy. Develop a vision node using OpenCV to detect a red target box and a control node that respects Ackermann turning constraints (no in-place rotation)."*

---

## 2. Technical Discrepancies and AI Hallucinations

### A. Gazebo Simulation Plugin API (Harmonic Transition)
**The Hallucination:** The AI initially generated URDF and SDF plugins using the `gz-gazebo-*` prefix (e.g., `libgz-gazebo-ackermann-steering-system.so`).
**The Reality:** In ROS 2 Jazzy, which utilizes Gazebo Harmonic, the plugin libraries have been renamed to follow the **Gazebo Sim** naming convention (`gz-sim-*`). Specifically, namespaces transitioned from `gz::gazebo` to `gz::sim`.
**Impact:** Launching the simulation resulted in `Shared library not found` errors. I had to manually audit the Gazebo Harmonic documentation to correct the plugin filenames to `gz-sim-physics-system`, `gz-sim-sensors-system`, and `gz-sim-ackermann-steering-system`.

### B. Ogre2 Render Engine & Material Properties
**The Hallucination:** The AI assumed that the provided `<ambient>` color in the SDF file would be sufficient for the OpenCV node to detect the red box.
**The Reality:** Modern Gazebo (using the Ogre2 render engine) calculates illumination primarily through the `<diffuse>` and `<specular>` components. Without these, the target box rendered as a silhouette or a very dark red under directional light.
**Impact:** The OpenCV HSV filter (looking for `H: 0-10, S: 100-255, V: 50-255`) failed to detect the object. I resolved this by injecting `<diffuse>` tags into the `shapes.sdf` for all objects, ensuring high-contrast color data.

### C. URDF Global Topic Namespacing
**The Hallucination:** The AI suggested a relative topic name for the camera sensor: `camera/image_raw`.
**The Reality:** Relative topic names in Gazebo Harmonic are scoped to the model link (e.g., `/ackerman_simple/camera_link/camera/image_raw`).
**Impact:** The `ros_gz_bridge` was configured for the global topic `/camera/image_raw`. This led to a "Silent Failure" where the bridge was running but passing zero data. I corrected this by adding the leading slash `/` in the URDF, forcing the sensor to publish to the global namespace.

---

## 3. Systematic Debugging and Architecture Functionalization

### Phase 1: Communication Bridge Validation
To isolate why the robot was "blind," I utilized `ros2 node info` on the perception node and audited the `parameter_bridge`. I discovered that while the `Twist` bridge was active, the `Image` bridge was not receiving messages. By monitoring `gz topic -l`, I identified the namespacing error in the URDF and corrected it to align the Gazebo and ROS 2 namespaces.

### Phase 2: Visual Perception Robustness
After fixing the bridge, I used `rqt_image_view` to inspect the raw feed. The target box was appearing dark, causing the HSV mask to fail. I systematically:
1.  **Updated SDF**: Injected diffuse lighting properties.
2.  **Calibrated HSV**: Widened the Value (V) and Saturation (S) bounds to account for shadow gradients.
3.  **Contour Filtering**: Implemented an area threshold (>500 pixels) to filter out background noise and focus only on the target box.

### Phase 3: Kinematic Constraint Enforcement
Initial control outputs caused the robot to "jerk" and spin its wheels, violating Ackermann constraints. I debugged the control architecture by:
1.  **Implementing EMA**: Added an **Exponential Moving Average** to the steering output to smooth the wheel transition.
2.  **State Persistence**: Added a "last-seen" memory buffer. If the target is lost for <1 second, the robot continues its last known steering trajectory instead of entering a "search-circle" immediately.
3.  **Velocity Control**: Locked `linear.x` to a constant positive value during tracking to ensure the robot always drives in an arc, never stopping to pivot.
