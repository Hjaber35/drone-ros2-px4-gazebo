import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory("drone_bringup")
    world_path = os.path.join(package_share, "worlds", "simple_room.sdf")

    # Keep using the model folder from our working demo.
    models_path = os.path.expanduser("~/drone_ws/src/drone_bringup/models")
    existing_path = os.environ.get("GZ_SIM_RESOURCE_PATH", "")
    resource_path = os.pathsep.join(
        path for path in (models_path, existing_path) if path
    )

    gazebo = ExecuteProcess(
        cmd=["gz", "sim", "-r", world_path],
        output="screen",
    )


    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
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
        SetEnvironmentVariable(
            name="GZ_SIM_RESOURCE_PATH",
            value=resource_path,
        ),
        gazebo,
        bridge,
        rover,
    ])