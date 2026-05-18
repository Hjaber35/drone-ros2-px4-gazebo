import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point


class PositionListener(Node):
    def __init__(self):
        super().__init__("position_listener")

        self.subscription = self.create_subscription(
            Point,
            "drone_position",
            self.position_callback,
            10
        )

        self.get_logger().info("Position listener started.")

    def position_callback(self, msg):
        self.get_logger().info(
            f"Current drone position -> x: {msg.x}, y: {msg.y}, z: {msg.z}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = PositionListener()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()