import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class RoverGoToTarget(Node):
    def __init__(self):
        super().__init__('rover_go_to_target')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.target_x = 2.0
        self.target_y = 0.0

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        self.has_odom = False
        self.target_reached = False

        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Autonomous rover target node started.')
        self.get_logger().info(f'Target: x={self.target_x}, y={self.target_y}')

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

        self.has_odom = True

    def control_loop(self):
        if not self.has_odom:
            self.get_logger().info('Waiting for odometry...')
            return

        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y

        distance = math.sqrt(dx * dx + dy * dy)
        target_angle = math.atan2(dy, dx)

        angle_error = target_angle - self.current_yaw
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

        cmd = Twist()

        if distance < 0.35:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.cmd_pub.publish(cmd)

            if not self.target_reached:
                self.get_logger().info('Target reached. Rover stopped.')
                self.target_reached = True

            return

        if abs(angle_error) > 0.25:
            cmd.linear.x = 0.0
            cmd.angular.z = max(min(0.5 * angle_error, 0.6), -0.6)
        else:
            cmd.linear.x = min(0.12, 0.25 * distance)
            cmd.angular.z = max(min(0.5 * angle_error, 0.4), -0.4)

        self.cmd_pub.publish(cmd)

        self.get_logger().info(
            f'x={self.current_x:.2f}, y={self.current_y:.2f}, '
            f'distance={distance:.2f}, angle_error={angle_error:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = RoverGoToTarget()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()