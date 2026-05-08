import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class CommandListener(Node):
    def __init__(self):
        super().__init__("command_listener") 

        self.subscription = self.create_subscription(
            String,
            "drone_command",
            self.command_callback,
            10
        ) 
        self.get_logger().info("Command listener started.") 

    def command_callback(self, msg):
        self.get_logger().info(f"Received command: {msg.data}")


def main(args=None):
    rclpy.init(args=args)

    node = CommandListener()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()