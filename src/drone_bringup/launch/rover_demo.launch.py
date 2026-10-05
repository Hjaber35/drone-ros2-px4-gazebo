import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory("drone_bringup")

    # Use one room for mapping and navigation.
    world_path = os.path.join(
        package_share, "worlds", "simple_room.sdf"
    )

    models_path = os.path.expanduser(
        "~/drone_ws/src/drone_bringup/models"
    )
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
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/model/simple_rover/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
        ],
        remappings=[
            ("/model/simple_rover/tf", "/tf"),
        ],
        output="screen",
    )

    # Fixed mounting position of the LiDAR relative to the chassis.
    lidar_transform = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "--x", "0",
            "--y", "0",
            "--z", "0.20",
            "--roll", "0",
            "--pitch", "0",
            "--yaw", "0",
            "--frame-id", "base_link",
            "--child-frame-id", "simple_rover/base_link/rover_lidar",
        ],
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
        lidar_transform,
    ])