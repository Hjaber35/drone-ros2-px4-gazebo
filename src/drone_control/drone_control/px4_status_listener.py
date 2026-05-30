import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import VehicleStatus


class PX4StatusListener(Node):
    def __init__(self):
        super().__init__("px4_status_listener")

        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscription = self.create_subscription(
            VehicleStatus,
            "/fmu/out/vehicle_status_v4",
            self.status_callback,
            px4_qos
        )

        self.get_logger().info("PX4 status listener started.")

    def status_callback(self, msg):
        self.get_logger().info(
            f"PX4 status -> nav_state: {msg.nav_state}, arming_state: {msg.arming_state}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = PX4StatusListener()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()