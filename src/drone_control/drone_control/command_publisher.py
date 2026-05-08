import rclpy
from rclpy.node import Node 
from std_msgs.msg import String 


class CommandPublisher(Node): 
    def __init__(self):
        super().__init__("command_publisher")
        self.publisher = self.create_publisher(
            String,
            "drone_command",
            10 //ROS can keep a small buffer of messages if needed
        )

        self.timer = self.create_timer(1.0, self.send_command)

        self.get_logger().info("Command publisher started.")
    def send_command(self): 
        msg = String() 
        msg.data = "TAKEOFF" 
        self.publisher.publish(msg) 

        self.get_logger().info(f"Published command: {msg.data}")


def main(args=None):
    rclpy.init(args=args)

    node = CommandPublisher()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()