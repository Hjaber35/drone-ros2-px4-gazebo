import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from px4_msgs.msg import OffboardControlMode
from px4_msgs.msg import TrajectorySetpoint
from px4_msgs.msg import VehicleCommand


class PX4OffboardTakeoff(Node):
    def __init__(self):
        super().__init__("px4_offboard_takeoff")

        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.offboard_control_mode_publisher = self.create_publisher(
            OffboardControlMode,
            "/fmu/in/offboard_control_mode",
            px4_qos
        )

        self.trajectory_setpoint_publisher = self.create_publisher(
            TrajectorySetpoint,
            "/fmu/in/trajectory_setpoint",
            px4_qos
        )

        self.vehicle_command_publisher = self.create_publisher(
            VehicleCommand,
            "/fmu/in/vehicle_command",
            px4_qos
        )

        self.timer = self.create_timer(0.1, self.timer_callback)

        self.setpoint_counter = 0

        self.get_logger().info("PX4 offboard takeoff node started.")

    def timer_callback(self):
        self.publish_offboard_control_mode()
        self.publish_trajectory_setpoint()

        if self.setpoint_counter == 10:
            self.engage_offboard_mode()
            self.arm()

        if self.setpoint_counter < 11:
            self.setpoint_counter += 1

    def publish_offboard_control_mode(self):
        msg = OffboardControlMode()

        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)

        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False

        self.offboard_control_mode_publisher.publish(msg)

    def publish_trajectory_setpoint(self):
        msg = TrajectorySetpoint()

        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)

        msg.position = [0.0, 0.0, -2.0]
        msg.yaw = 0.0

        self.trajectory_setpoint_publisher.publish(msg)

        self.get_logger().info("Sending takeoff setpoint: x=0.0, y=0.0, z=-2.0")

    def engage_offboard_mode(self):
        self.publish_vehicle_command(
            VehicleCommand.VEHICLE_CMD_DO_SET_MODE,
            param1=1.0,
            param2=6.0
        )

        self.get_logger().info("Switching to Offboard mode.")

    def arm(self):
        self.publish_vehicle_command(
            VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM,
            param1=1.0
        )

        self.get_logger().info("Arm command sent.")

    def publish_vehicle_command(self, command, param1=0.0, param2=0.0):
        msg = VehicleCommand()

        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)

        msg.param1 = param1
        msg.param2 = param2
        msg.command = command

        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1

        msg.from_external = True

        self.vehicle_command_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = PX4OffboardTakeoff()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()