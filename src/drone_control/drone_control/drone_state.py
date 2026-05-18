import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Point


class DroneState(Node):
    def __init__(self):
        super().__init__("drone_state")

        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.subscription = self.create_subscription(
            String,
            "drone_command",
            self.command_callback,
            10
        )

        self.position_publisher = self.create_publisher(
            Point,
            "drone_position",
            10
        )

        self.get_logger().info("Drone state node started.")
        self.print_state()
        self.publish_position()

    def command_callback(self, msg):
        command = msg.data

        self.get_logger().info(f"State node received command: {command}")

        if command == "TAKEOFF":
            self.z = 1.0

        elif command == "FORWARD":
            self.x += 1.0

        elif command == "LEFT":
            self.y += 1.0

        elif command == "RIGHT":
            self.y -= 1.0

        elif command == "LAND":
            self.z = 0.0

        else:
            self.get_logger().warn(f"Unknown command: {command}")

        self.print_state()
        self.publish_position()

    def publish_position(self):
        position_msg = Point()

        position_msg.x = self.x
        position_msg.y = self.y
        position_msg.z = self.z

        self.position_publisher.publish(position_msg)

        self.get_logger().info(
            f"Published position -> x: {position_msg.x}, y: {position_msg.y}, z: {position_msg.z}"
        )

    def print_state(self):
        self.get_logger().info(
            f"Drone position -> x: {self.x}, y: {self.y}, z: {self.z}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = DroneState()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()