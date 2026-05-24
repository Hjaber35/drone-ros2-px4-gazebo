from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    world_path = os.path.join(
        get_package_share_directory("drone_bringup"),
        "worlds",
        "simple_room.sdf"
    )

    gazebo_process = ExecuteProcess(
        cmd=["gz", "sim", world_path],
        output="screen"
    )

    command_listener_node = Node(
        package="drone_control",
        executable="command_listener",
        name="command_listener"
    )

    drone_state_node = Node(
        package="drone_control",
        executable="drone_state",
        name="drone_state"
    )

    position_listener_node = Node(
        package="drone_control",
        executable="position_listener",
        name="position_listener"
    )

    command_publisher_node = Node(
        package="drone_control",
        executable="command_publisher",
        name="command_publisher"
    )

    return LaunchDescription([
        gazebo_process,
        command_listener_node,
        drone_state_node,
        position_listener_node,
        command_publisher_node
    ])