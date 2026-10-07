# Autonomous Rover Simulation

A differential-drive rover project built with ROS 2 Jazzy and Gazebo Harmonic. The rover uses a simulated LiDAR to sense the room. I used SLAM Toolbox to create a map, then saved it so the rover can localize with AMCL and drive to a goal selected in RViz using Nav2.

The project runs in Ubuntu 24.04 through WSL on Windows.

## Why this project changed

This repository started as a PX4 drone project. I switched my active work to a rover so I could focus on a reliable autonomous navigation demo. The earlier drone work is still in the repository; rover development is on the `rover-version` branch.

## What works

- A differential-drive rover drives in a Gazebo room with walls and obstacles.
- A simulated 360° LiDAR publishes scans on `/scan`.
- SLAM Toolbox was used to make and save a map of the room.
- AMCL estimates the rover's position on the saved map.
- Nav2 plans a path to a goal chosen in RViz and uses LiDAR data to avoid obstacles.
- An earlier Python controller can drive to a fixed target and choose a left or right detour using the LiDAR scan.

The Nav2 route and the earlier Python controller are separate ways of driving the rover. Run only one at a time because both can publish movement commands.

## How navigation works

Gazebo simulates the rover, its wheel odometry, and its LiDAR. `ros_gz_bridge` passes the simulation topics into ROS 2. SLAM Toolbox combined the LiDAR scans with the rover's movement to build the saved map. During a navigation run, AMCL estimates where the rover is on that map, and Nav2 plans and follows a route to the goal selected in RViz.

The green circle in Gazebo marks the earlier controller's fixed target. Nav2 follows the goal selected in RViz; it does not read the green circle.

## Setup and build

These commands assume ROS 2 Jazzy, Gazebo Harmonic, `ros_gz_bridge`, Nav2, and the workspace are already installed at `~/drone_ws`.

```bash
cd ~/drone_ws
git switch rover-version
source /opt/ros/jazzy/setup.bash
colcon build --packages-select drone_bringup rover_control --symlink-install
source install/setup.bash
```

## Run navigation on the saved map

Open three Ubuntu terminals. Keep each launch command running while you use the next terminal.

**Terminal 1 — Gazebo and the bridge**

```bash
cd ~/drone_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch drone_bringup rover_demo.launch.py
```

Make sure Gazebo is playing. This launch starts the room and bridges `/cmd_vel`, `/odom`, `/clock`, and `/scan`. It does not start the earlier Python controller.

**Terminal 2 — saved map, AMCL, and Nav2**

```bash
cd ~/drone_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch drone_bringup rover_navigation.launch.py
```

Give the navigation nodes a little time to become active.

**Terminal 3 — RViz**

```bash
cd ~/drone_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
GALLIUM_DRIVER=d3d12 rviz2 --ros-args -p use_sim_time:=true
```

In RViz, set **Fixed Frame** to `map`. If the map is missing, add a **Map** display, choose `/map`, and set its **Durability Policy** to **Transient Local**. Use **2D Pose Estimate** to show AMCL where the rover starts. Then use **2D Goal Pose** to select where Nav2 should drive. Check that the pose arrow points in the rover's actual direction.

Stop a launch with Ctrl+C in its terminal. Let Gazebo close before starting another world.

## Earlier controller and blocked-path test

`rover_go_to_target` is the earlier controller in `rover_control`. It uses `/odom` to steer to `(2, 2)` and `/scan` to check possible left and right detours. It slows near the target and stops within 0.35 m. If neither detour has enough clearance, it stops. This is a simple reactive approach, not the Nav2 planner.

To test the case where both detours are blocked, stop the Nav2 launch and any other controller. Start the blocked world in **Terminal 1**:

```bash
cd ~/drone_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch drone_bringup rover_demo.launch.py world:=blocked_paths.sdf
```

Then start the earlier controller in a **second Ubuntu terminal**:

```bash
cd ~/drone_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run rover_control rover_go_to_target --ros-args -p use_sim_time:=true
```

The expected result in this test is a stopped rover when both candidate detours are rejected. This does not mean that every possible route through the room is blocked.

Do not run `rover_driver` at the same time as either navigation method; it also publishes to `/cmd_vel`.

## Main files

| File | Purpose |
| --- | --- |
| `src/drone_bringup/launch/rover_demo.launch.py` | Starts Gazebo and the ROS/Gazebo bridge |
| `src/drone_bringup/launch/rover_navigation.launch.py` | Starts the saved map, AMCL, and Nav2 |
| `src/drone_bringup/config/rover_nav.yaml` | Nav2 settings, including driving speed |
| `src/drone_bringup/config/rover_mapping.yaml` | SLAM Toolbox settings used while mapping |
| `src/drone_bringup/worlds/simple_room.sdf` | Main room and target marker |
| `src/drone_bringup/worlds/blocked_paths.sdf` | Optional blocked-detour test |
| `src/drone_bringup/models/simple_rover/model.sdf` | Rover, wheels, LiDAR, and drive plugin |
| `src/rover_control/rover_control/rover_go_to_target.py` | Earlier fixed-target controller |
| `maps/simple_room.pgm` and `maps/simple_room.yaml` | Saved room map |

## What has been tested

- Mapped the room with LiDAR and SLAM Toolbox, then saved the map.
- Localized the rover on the saved map with AMCL.
- Selected a goal in RViz and drove there with Nav2 while avoiding obstacles in the simulation room.
- Launched Nav2 automatically using `rover_navigation.launch.py` with the configured 0.40 m/s forward speed limit.
- Ran the earlier controller through left and right detours and checked that it stops when both detours are rejected.

These are manual tests in this simulated room. The project has not been tested against every obstacle layout.

## Current limits and next steps

- Nav2 uses a saved map; the initial pose is currently set manually in RViz.
- Wheel odometry can drift, especially if the wheels slip.
- The earlier controller checks two 60° detours and may stop even when another route exists.
- The LiDAR only measures obstacles visible in its scan plane.
- Camera-based perception is not part of this demo.

Next I plan to repeat the navigation tests, capture screenshots and a short video, and write up the design, results, and limitations.

## WSL notes

The Gazebo launch currently looks for rover models at `~/drone_ws/src/drone_bringup/models`. Update that path if the workspace moves. The `GALLIUM_DRIVER=d3d12` RViz command and Gazebo rendering settings were chosen for this WSL computer with Intel graphics and may need changing on another machine.

## Earlier PX4 work

The initial drone milestones included installing ROS 2 and PX4, launching an x500 drone in Gazebo, and running basic Python ROS 2 nodes. Drone LiDAR, SLAM, and marker landing were ideas for later work, not completed drone features.

The earlier PX4 installation can still be launched separately:

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```
