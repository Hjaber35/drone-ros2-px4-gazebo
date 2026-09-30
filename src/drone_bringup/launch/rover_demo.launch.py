import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    SetEnvironmentVariable,
)
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory("drone_bringup")
    world_argument = DeclareLaunchArgument(
        "world",
        default_value="simple_room.sdf",
        description="World file inside drone_bringup/worlds",
    )

    world_path = PathJoinSubstitution([
        package_share,
        "worlds",
        LaunchConfiguration("world"),
    ])

    # Keep using the model folder from our working demo.
    models_path = os.path.expanduser("~/drone_ws/src/drone_bringup/models")
    existing_path = os.environ.get("GZ_SIM_RESOURCE_PATH", "")
    resource_path = os.pathsep.join(
        path for path in (models_path, existing_path) if path
    )

    gazebo = ExecuteProcess(
        cmd=[
            "gz", "sim", "-r", "-v", "4",
            "--render-engine-gui", "ogre",
            "--render-engine-server", "ogre2",
            world_path,
        ],
        additional_env={"GALLIUM_DRIVER": "d3d12"},
        output="screen",
    )


    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
        ],
        output="screen",
    )

    rover = Node(
        package="rover_control",
        executable="rover_go_to_target",
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    return LaunchDescription([
        world_argument,
        SetEnvironmentVariable(
            name="GZ_SIM_RESOURCE_PATH",
            value=resource_path,
        ),
        gazebo,
        bridge,
        rover,
    ])