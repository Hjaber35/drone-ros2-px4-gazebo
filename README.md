# Autonomous Rover Simulation — ROS 2 + Gazebo

A differential-drive rover that uses odometry feedback to drive toward a target, adjust its heading, slow down as it approaches, and stop within a defined tolerance.

Developed using ROS 2 Jazzy and Gazebo Harmonic on Ubuntu 24.04 through Windows WSL.

## Project Background

This project began as a ROS 2 and PX4 drone simulation. I switched the active development focus to a rover to build a manageable autonomous navigation project and strengthen my understanding of ROS nodes, simulation, and feedback control.

The original drone/PX4 work is preserved. Active rover development is on the `rover-version` branch.

## Implemented Features

- Differential-drive rover in a room with walls and an obstacle
- Autonomous movement toward a fixed target
- Heading correction using odometry feedback
- Reduced speed near the target
- Automatic stopping within the target tolerance
- Green target marker in Gazebo
- Blue chassis with a yellow stripe identifying the front
- One launch command for Gazebo, the ROS/Gazebo bridge, and the controller
- Controller timing synchronized with Gazebo through `/clock`
- Diagonal target navigation verified in two consecutive runs

## How It Works

1. Gazebo simulates the rover and publishes wheel-based odometry.
2. `ros_gz_bridge` connects Gazebo topics to ROS 2.
3. The `rover_go_to_target` node reads `/odom`.
4. It calculates the distance and heading error to the target.
5. It publishes forward speed and turning commands on `/cmd_vel`.
6. It continues updating these commands until the rover reaches the stopping tolerance.

The green marker displays the target area. The rover follows numerical coordinates; it does not detect the marker with a camera.

## Environment

- Windows with WSL Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- `ros_gz_bridge`
- Python
- colcon

The commands below assume these dependencies are installed and the workspace is located at `~/drone_ws`.

## Build

```bash
cd ~/drone_ws
git switch rover-version
source /opt/ros/jazzy/setup.bash
colcon build --packages-select drone_bringup rover_control --symlink-install
source install/setup.bash
```

## Run the Rover Demo

```bash
cd ~/drone_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch drone_bringup rover_demo.launch.py
```

Click Play in Gazebo if the simulation starts paused.

The launch file starts:

- Gazebo with `simple_room.sdf`
- The bridge for `/cmd_vel` and `/odom`
- The `rover_go_to_target` controller

The launcher currently finds rover models in `~/drone_ws/src/drone_bringup/models`. If the workspace is moved, update that path in the launch file.

Do not run `rover_driver` alongside the autonomous controller because both publish movement commands to `/cmd_vel`.

Press Ctrl+C in the launch terminal to stop the demo.

## Current Target

- Target: `x = 2.0 m`, `y = -2.0 m` in the odometry frame
- Stopping tolerance: `0.35 m`

Target coordinates are defined in:

`src/rover_control/rover_control/rover_go_to_target.py`

The target marker is defined separately in:

`src/drone_bringup/worlds/simple_room.sdf`

For the current starting pose, the marker is placed at world coordinates `(2, -2)`. If changing the target, update the marker to match.

## Main Files

| File | Purpose |
| --- | --- |
| `src/drone_bringup/launch/rover_demo.launch.py` | Starts the complete rover demo |
| `src/drone_bringup/worlds/simple_room.sdf` | Room, obstacle, target marker, and rover placement |
| `src/drone_bringup/models/simple_rover/model.sdf` | Rover body, wheels, joints, and drive plugin |
| `src/rover_control/rover_control/rover_go_to_target.py` | Autonomous target controller |

## Current Limitations

- The route to the target must be clear; obstacle avoidance is not implemented.
- Wheel-based odometry can drift or report inaccurate movement if wheels slip.
- The target is currently set in code.
- Straight-line navigation to `(2, 0)` and diagonal navigation to `(2, -2)` have been demonstrated. The diagonal test succeeded in two consecutive runs; broader testing is still needed.
- Rover navigation does not currently use LiDAR, SLAM, or camera-based perception.

## Original PX4 Drone Work

Earlier milestones included:

- ROS 2 Jazzy and PX4 installation
- Gazebo launch with the x500 drone
- ROS 2 workspace creation
- Initial Python ROS 2 nodes

The original drone plan included LiDAR, SLAM, and ArUco marker landing. These were planned features, not completed capabilities.

To launch the original PX4 simulation, using the existing PX4 installation:

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

## Next Steps

- Validate navigation to targets that require turning
- Check repeatability over multiple runs
- Add screenshots and a short demonstration video
- Document test results and lessons learned