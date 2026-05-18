from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    command_listener_node = Node(
        package="drone_control",
        executable="command_listener",
        name="command_listener"
    )

    command_publisher_node = Node(
        package="drone_control",
        executable="command_publisher",
        name="command_publisher"
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

    return LaunchDescription([
        command_listener_node,
        drone_state_node,
        position_listener_node,
        command_publisher_node
    ])