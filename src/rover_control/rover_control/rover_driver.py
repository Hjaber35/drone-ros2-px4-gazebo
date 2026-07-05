import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class RoverDriver(Node):
    def __init__(self):
        super().__init__('rover_driver')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.timer = self.create_timer(0.1, self.drive_forward)

        self.get_logger().info('Rover driver started. Publishing to /cmd_vel')

    def drive_forward(self):
        msg = Twist()

        # Forward speed
        msg.linear.x = 0.2
        # No turning for now
        msg.angular.z = 0.0

        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = RoverDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()