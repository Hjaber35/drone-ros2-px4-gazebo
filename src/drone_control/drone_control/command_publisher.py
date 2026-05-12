import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class CommandPublisher(Node):
    def __init__(self):
        super().__init__("command_publisher")

        self.publisher = self.create_publisher(
            String,
            "drone_command",
            10
        )

        self.commands = [
            "TAKEOFF",
            "FORWARD",
            "LEFT",
            "RIGHT",
            "LAND"
        ]
        self.command_index = 0
        self.timer = self.create_timer(2.0, self.send_command)

        self.get_logger().info("Command publisher started.")

    def send_command(self):
        msg = String()

        msg.data = self.commands[self.command_index]

        self.publisher.publish(msg)

        self.get_logger().info(f"Published command: {msg.data}")

        self.command_index += 1

        if self.command_index >= len(self.commands):
            self.command_index = 0


def main(args=None):
    rclpy.init(args=args)

    node = CommandPublisher()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()