# Ackermann Mobile Robot: Perception-to-Action Pipeline

This repository contains a complete ROS 2 perception-to-action pipeline for an Ackermann-steered mobile robot, developed for the Greenswip Robotics Software Assignment. The system enables a robot to autonomously identify, track, and navigate toward a specific red box target while ignoring various decoy objects in a Gazebo Harmonic simulation.

## 🚀 Project Overview

The project integrates computer vision and advanced control theory to solve a "Target Retrieval" task under strict kinematic constraints.

- **Robot Kinematics**: Ackermann Steering (No in-place rotation).
- **Simulation Environment**: Gazebo Harmonic (ROS 2 Jazzy).
- **Perception**: OpenCV-based HSV color segmentation and contour analysis.
- **Control**: Proportional control mapped to Ackermann steering geometry.

## 🛠️ Technical Implementation

### Architecture & Setup
The robot is described via a URDF (`ack.urdf.xacro`) enhanced with Gazebo Sim plugins. The communication between ROS 2 and Gazebo is handled by the `ros_gz_bridge`.

### Perception (Computer Vision)
The `perception_node` processes a live camera feed. It utilizes:
- **HSV Masking**: Specifically tuned to isolate the Red Box (ignoring blue, orange, and green decoys).
- **Centroid Tracking**: Calculates the horizontal error from the image center to provide feedback for the steering controller.

### Navigation & Control
The `control_node` implements an Ackermann-specific navigation algorithm:
- **Kinematic Constraints**: The robot maintains a constant forward velocity while turning, ensuring it follows a curved path rather than pivoting, satisfying strict Ackermann constraints.
- **Closing Logic**: The robot automatically decelerates and halts once it reaches a proximity threshold determined by the target's visual area.

## 📂 Repository Structure
```text
ros2_ws/
└── src/
    └── ackermann_nav/
        ├── ackermann_nav/      # Perception and Control Nodes
        ├── launch/             # ROS 2 Launch files
        ├── urdf/               # Robot URDF with GZ plugins
        └── worlds/             # Gazebo World with shapes
```

## 📺 Video Demonstrations

Below are the demonstrations of the robot successfully reaching the target in three different shuffled object arrangements.

### Arrangement 1 (Center)
https://github.com/FireFistisDead/Shape-detection/raw/main/assests/center_box.mp4

### Arrangement 2 (Side)
https://github.com/FireFistisDead/Shape-detection/raw/main/assests/right_side_box.mp4

### Arrangement 3
<!-- REPLACE THE LINK BELOW WITH YOUR VIDEO LINK -->
[![](https://img.youtube.com/vi/YOUR_VIDEO_ID_3/0.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID_3)

## 🏁 How to Run

### 1. Build the Workspace
In your WSL2 terminal:
```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
```

### 2. Launch the Simulation
```bash
source install/setup.bash
ros2 launch ackermann_nav main.launch.py
```


