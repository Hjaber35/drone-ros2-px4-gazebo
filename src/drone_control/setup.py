from setuptools import find_packages, setup

package_name = 'drone_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jawad',
    maintainer_email='jawad@todo.todo',
    description='Drone control nodes for the ROS 2 PX4 Gazebo project',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'test_node = drone_control.test_node:main',
        'command_publisher = drone_control.command_publisher:main',
        'command_listener = drone_control.command_listener:main',
        'drone_state = drone_control.drone_state:main',
        'position_listener = drone_control.position_listener:main',
        'px4_status_listener = drone_control.px4_status_listener:main',
        'px4_odometry_listener = drone_control.px4_odometry_listener:main',
        'px4_offboard_takeoff = drone_control.px4_offboard_takeoff:main',
        ],
    },
)