# Autonomous Rover Simulation — ROS 2 + Gazebo

A differential-drive rover that navigates toward a target using odometry and simulated 360° LiDAR. It compares left and right detours when an obstacle blocks forward travel, checks clearance before returning toward the target, and stops near the goal.

Developed using ROS 2 Jazzy and Gazebo Harmonic on Ubuntu 24.04 through Windows WSL.

## Project Background

This project began as a ROS 2 and PX4 drone simulation. I switched active development to a rover to build a manageable autonomous navigation project and strengthen my understanding of ROS nodes, simulation, sensors, and feedback control.

The original drone/PX4 work is preserved. Active rover development is on the `rover-version` branch.

## Implemented Features

- Differential-drive rover with a blue chassis and yellow front stripe
- Autonomous navigation toward a fixed coordinate target
- Odometry-based heading correction and reduced speed near the target
- Simulated 360° LiDAR publishing distance readings on `/scan`
- Comparison of left and right 60° detour candidates
- Clearance checks that account for the rover's size
- Return toward the target when the scanned passage is clear
- Stopping when neither candidate detour has sufficient clearance
- Stopping when LiDAR data is missing, stale, or invalid in the forward sector
- Green target marker in Gazebo
- One launch command for Gazebo, the bridge, and the controller
- Selectable normal and blocked-path test worlds
- Controller timers use simulation time through `/clock`

## How It Works

1. Gazebo simulates the rover, odometry, and LiDAR.
2. `ros_gz_bridge` connects Gazebo topics to ROS 2.
3. `rover_go_to_target` reads `/odom` and `/scan`.
4. With a clear forward path, it calculates target distance and heading error.
5. When an obstacle is detected ahead, it compares left and right detours.
6. It turns toward an eligible detour and drives slowly while checking the passage toward the target.
7. When that passage has sufficient clearance, it resumes target navigation.
8. It publishes movement commands on `/cmd_vel` and stops within the target tolerance.

The controller represents the rover with a clearance circle when checking candidate paths. These checks use the current scan, not a stored map.

The green marker only displays the target area. The rover follows numerical coordinates; it does not detect the marker with a camera.

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

## Run the Normal Demo

```bash
cd ~/drone_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch drone_bringup rover_demo.launch.py
```

This loads `simple_room.sdf`. The current layout contains the central obstacle and a left-side blocker, providing a test of right-side avoidance.

The launch file starts:

- Gazebo
- The bridge for `/cmd_vel`, `/odom`, `/clock`, and `/scan`
- The `rover_go_to_target` controller

The simulation is configured to start playing automatically.

## Run the Blocked-Path Test

```bash
cd ~/drone_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch drone_bringup rover_demo.launch.py world:=blocked_paths.sdf
```

This world adds a right-side blocker. The expected result is that the rover stops when both candidate detours are rejected.

A stopped rover is the intended outcome of this test. It does not mean every possible route through the room is blocked.

Stop the current demo with Ctrl+C and wait for Gazebo to close before launching another world.

Do not run `rover_driver` alongside the autonomous controller because both publish movement commands to `/cmd_vel`.

## Current Settings

| Setting | Value |
| --- | --- |
| Target in the odometry frame | `(2.0, 2.0)` m |
| Target stopping tolerance | 0.35 m |
| Maximum target-driving speed | 0.25 m/s |
| Detour driving speed | 0.12 m/s |
| Forward obstacle threshold | 0.80 m from the LiDAR |
| Forward detection sector | ±30° |
| Candidate detour turns | ±60° |
| Clearance radius | 0.50 m |
| Minimum detour before checking for a return | 0.25 m |
| Maximum detour displacement | 1.80 m |
| LiDAR coverage | 360°, approximately 1° spacing |
| LiDAR range and update rate | 0.10–8.0 m, 10 Hz |

If both candidate paths are eligible and their clearance differs by no more than 0.05 m, the controller prefers left.

Target coordinates are defined in:

`src/rover_control/rover_control/rover_go_to_target.py`

Target markers are defined separately in both world files. With the current starting pose, they are at world coordinates `(2, 2)`. Update both markers when changing the target.

## Tests Performed

- Navigation to straight and diagonal targets
- Stopping for an obstacle ahead
- Left-side obstacle detour and return to the target
- Right-side detour with the left candidate blocked, reaching the target without touching either box
- Rejection of both detours in the blocked-path layout
- Launching the normal and blocked-path worlds using the `world` argument

These are manual simulation tests in specific layouts. Broader repeatability testing is still needed.

## Main Files

| File | Purpose |
| --- | --- |
| `src/drone_bringup/launch/rover_demo.launch.py` | Starts the demo and selects the world |
| `src/drone_bringup/worlds/simple_room.sdf` | Normal navigation test layout |
| `src/drone_bringup/worlds/blocked_paths.sdf` | Both-detours-blocked test layout |
| `src/drone_bringup/models/simple_rover/model.sdf` | Rover body, wheels, LiDAR, and drive plugin |
| `src/rover_control/rover_control/rover_go_to_target.py` | Target navigation and reactive obstacle avoidance |

## Current Limitations

- This is a reactive controller, not a global path planner.
- It considers only two detour directions: 60° left and 60° right.
- It may stop even when another route exists.
- It stops if the detour limit is reached without a clear passage to the target.
- LiDAR checks cannot reveal obstacles hidden behind other objects or outside the scan plane.
- Current scan-based clearance checks do not guarantee collision-free motion in arbitrary or changing environments.
- Wheel-based odometry can become inaccurate when wheels slip.
- The target and tuning values are currently set in code.
- SLAM, Nav2, and camera-based perception are not implemented.

## Local WSL Setup Notes

The launch file currently finds models in:

`~/drone_ws/src/drone_bringup/models`

Update that path if moving the workspace.

The current graphics configuration uses Ogre for the GUI, Ogre2 for server-side sensors, and `GALLIUM_DRIVER=d3d12` for this WSL/Intel graphics setup. Other computers may require different graphics settings.

During development, conflicting time synchronization caused large jumps in Ubuntu's system clock and jerky Gazebo display updates. Stopping Ubuntu's `systemd-timesyncd` service resolved the observed issue on this machine while Windows/WSL continued providing time synchronization.

## Original PX4 Drone Work

Earlier milestones included:

- ROS 2 Jazzy and PX4 installation
- Gazebo launch with the x500 drone
- ROS 2 workspace creation
- Initial Python ROS 2 nodes

The original drone plan included LiDAR, SLAM, and ArUco marker landing. These were planned features, not completed drone capabilities.

To launch the original PX4 simulation using the existing installation:

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

## Next Steps

- Repeat the existing tests and record results
- Test additional obstacle positions and target locations
- Improve recovery when the current detour choices are blocked
- Add screenshots and a short demonstration video
- Prepare a project report explaining the design, tests, and limitations