import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import VehicleOdometry


class PX4OdometryListener(Node):
    def __init__(self):
        super().__init__("px4_odometry_listener")

        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscription = self.create_subscription(
            VehicleOdometry,
            "/fmu/out/vehicle_odometry",
            self.odometry_callback,
            px4_qos
        )

        self.get_logger().info("PX4 odometry listener started.")

    def odometry_callback(self, msg):
        x = msg.position[0]
        y = msg.position[1]
        z = msg.position[2]

        self.get_logger().info(
            f"PX4 odometry -> x: {x}, y: {y}, z: {z}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = PX4OdometryListener()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()