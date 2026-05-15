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

    return LaunchDescription([
        command_listener_node,
        command_publisher_node
    ])