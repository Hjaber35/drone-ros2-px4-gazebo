from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    workspace = Path.home() / "drone_ws"
    params_file = str(
        workspace / "src/drone_bringup/config/rover_nav.yaml"
    )
    map_file = str(workspace / "maps/simple_room.yaml")

    nav2_launch_dir = (
        Path(get_package_share_directory("nav2_bringup")) / "launch"
    )

    # Load the saved map and use AMCL to locate the rover on it.
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(nav2_launch_dir / "localization_launch.py")
        ),
        launch_arguments={
            "map": map_file,
            "params_file": params_file,
            "use_sim_time": "true",
            "use_composition": "False",
            "autostart": "true",
        }.items(),
    )

    # Package, executable, node name, and movement-topic remappings.
    navigation_nodes = [
        ("nav2_controller", "controller_server", "controller_server",
         [("cmd_vel", "cmd_vel_nav")]),
        ("nav2_smoother", "smoother_server", "smoother_server", []),
        ("nav2_planner", "planner_server", "planner_server", []),
        ("nav2_behaviors", "behavior_server", "behavior_server",
         [("cmd_vel", "cmd_vel_nav")]),
        ("nav2_velocity_smoother", "velocity_smoother", "velocity_smoother",
         [("cmd_vel", "cmd_vel_nav")]),
        ("nav2_collision_monitor", "collision_monitor", "collision_monitor",
         []),
        ("nav2_bt_navigator", "bt_navigator", "bt_navigator", []),
    ]

    tf_remappings = [("/tf", "tf"), ("/tf_static", "tf_static")]

    nodes = [
        Node(
            package=package,
            executable=executable,
            name=name,
            parameters=[params_file, {"use_sim_time": True}],
            remappings=tf_remappings + movement_remappings,
            output="screen",
        )
        for package, executable, name, movement_remappings
        in navigation_nodes
    ]

    manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_navigation",
        parameters=[{
            "autostart": True,
            "node_names": [entry[2] for entry in navigation_nodes],
            "use_sim_time": True,
        }],
        output="screen",
    )

    return LaunchDescription([
        localization,
        *nodes,
        TimerAction(period=10.0, actions=[manager]),
    ])
