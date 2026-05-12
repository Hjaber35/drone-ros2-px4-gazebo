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
        command = msg.data

        self.get_logger().info(f"Received command: {msg.data}")

        if command == "TAKEOFF":
            self.handle_takeoff()
 
        elif command == "FORWARD":
            self.handle_forward()
        
        elif command == "LEFT":
            self.handle_left()
         
        elif command == "RIGHT":
             self.handle_right()
 
        elif command == "LAND":
             self.handle_land()
        
        else:
            self.get_logger().warn(f"Uknown command: {command}")

    def handle_takeoff(self):
        self.get_logger().info("Action: Drone should take off.")

    def handle_forward(self):
        self.get_logger().info("Action: Drone should move forward.")

    def handle_left(self):
        self.get_logger().info("Action:Drone should turn or move left.")
  
    def handle_right(self):
        self.get_logger().info("Action:Drone should turn or move right.")
    
    def handle_land(self):
        self.get_logger().info("Action:Drone should land.")

def main(args=None):
    rclpy.init(args=args)

    node = CommandListener()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()