from launch import LaunchDescription
from launch.actions import ExecuteProcess
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

    return LaunchDescription([
        gazebo_process
    ])