import math
import time
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException


class RoverGoToTarget(Node):
    def __init__(self):
        super().__init__('rover_go_to_target')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.target_x = 2.0
        self.target_y = 2.0

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        self.has_odom = False
        self.target_reached = False
        self.front_distance = None
        self.last_scan_time = None
        self.obstacle_stop_distance = 0.8
        # Remember which part of the detour we are performing.
        self.mode = 'GO_TO_TARGET'
        self.detour_yaw = 0.0
        self.detour_start_x = 0.0
        self.detour_start_y = 0.0
        self.detour_distance = 1.8
        self.latest_scan = None
        self.clearance_radius = 0.50
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile_sensor_data,
        )
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('Autonomous rover target node started.')
        self.get_logger().info(f'Target: x={self.target_x}, y={self.target_y}')

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        # Convert the odometry quaternion into yaw (heading in radians).
        q = msg.pose.pose.orientation

        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

        self.has_odom = True
    def scan_callback(self, msg):
        self.latest_scan = msg
        front_ranges = []

        for index, distance in enumerate(msg.ranges):
            angle = msg.angle_min + index * msg.angle_increment

            # Examine only the 30 degrees on either side of forward.
            if abs(angle) <= math.radians(30):
                if distance == math.inf:
                    # Gazebo reports +inf when nothing is within range.
                    front_ranges.append(msg.range_max)
                elif math.isfinite(distance) and (
                    msg.range_min <= distance <= msg.range_max
                ):
                    front_ranges.append(distance)
                else:
                    # Invalid forward readings: wait for a usable scan.
                    self.front_distance = None
                    self.last_scan_time = time.monotonic()
                    return

        self.front_distance = min(front_ranges) if front_ranges else None
        self.last_scan_time = time.monotonic()
    def path_clearance(self, direction, path_length):
        """Estimate clearance around a straight path using the current scan."""
        scan = self.latest_scan

        if scan is None or not scan.ranges:
            return 0.0

        if (
            scan.angle_increment <= 0.0
            or scan.angle_max - scan.angle_min
            < 2 * math.pi - 2 * scan.angle_increment
        ):
            return 0.0

        if path_length + self.clearance_radius > scan.range_max:
            return 0.0

        closest = scan.range_max

        for index, distance in enumerate(scan.ranges):
            if distance == math.inf:
                continue

            if (
                not math.isfinite(distance)
                or distance < scan.range_min
                or distance > scan.range_max
            ):
                return 0.0

            angle = scan.angle_min + index * scan.angle_increment
            relative_angle = angle - direction

            along = distance * math.cos(relative_angle)
            sideways = distance * math.sin(relative_angle)
            nearest_along = max(0.0, min(path_length, along))

            distance_to_path = math.hypot(
                along - nearest_along,
                sideways,
            )
            closest = min(closest, distance_to_path)

        return closest

    def target_path_clear(self):
        if not self.has_odom:
            return False

        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        path_length = math.hypot(dx, dy)
        direction = math.atan2(dy, dx) - self.current_yaw

        return (
            self.path_clearance(direction, path_length)
            > self.clearance_radius
        )
    def control_loop(self):
        scan_missing = (
            self.last_scan_time is None
            or time.monotonic() - self.last_scan_time > 1.0
            or self.front_distance is None
        )

        if scan_missing:
            self.cmd_pub.publish(Twist())
            self.get_logger().info(
                'Waiting for fresh, valid LiDAR data...',
                throttle_duration_sec=2.0,
            )
            return

        if not self.has_odom:
            self.cmd_pub.publish(Twist())
            self.get_logger().info(
                'Waiting for odometry...',
                throttle_duration_sec=2.0,
            )
            return
        # Compare left and right detours when forward travel is blocked.
        if (
            self.mode == 'GO_TO_TARGET'
            and self.front_distance < self.obstacle_stop_distance
        ):
            left_angle = math.radians(60)
            right_angle = math.radians(-60)

            left_clearance = self.path_clearance(
                left_angle, self.detour_distance
            )
            right_clearance = self.path_clearance(
                right_angle, self.detour_distance
            )

            left_clear = left_clearance > self.clearance_radius
            right_clear = right_clearance > self.clearance_radius

            # Stop before making a turn decision.
            self.cmd_pub.publish(Twist())

            if not left_clear and not right_clear:
                self.get_logger().info(
                    'Neither detour has enough clearance. Stopped. '
                    f'Left={left_clearance:.2f} m, '
                    f'right={right_clearance:.2f} m',
                    throttle_duration_sec=2.0,
                )
                return

            # Prefer left when the two clearances are almost equal.
            if left_clear and (
                not right_clear
                or left_clearance >= right_clearance - 0.05
            ):
                chosen_angle = left_angle
                side = 'left'
            else:
                chosen_angle = right_angle
                side = 'right'

            self.detour_yaw = self.current_yaw + chosen_angle
            self.detour_yaw = math.atan2(
                math.sin(self.detour_yaw),
                math.cos(self.detour_yaw),
            )
            self.mode = 'TURN_DETOUR'

            self.get_logger().info(
                f'Obstacle detected. Turning {side}. '
                f'Left clearance={left_clearance:.2f} m, '
                f'right clearance={right_clearance:.2f} m'
            )
            return

        if self.mode == 'TURN_DETOUR':
            turn_error = self.detour_yaw - self.current_yaw
            turn_error = math.atan2(
                math.sin(turn_error), math.cos(turn_error)
            )

            cmd = Twist()

            # Stop the turn once we are within about 5 degrees.
            if abs(turn_error) < 0.08:
                self.detour_start_x = self.current_x
                self.detour_start_y = self.current_y
                self.mode = 'PASS_OBSTACLE'
                self.get_logger().info(
                    'Turn complete. Driving along the detour.'
                )
            else:
                cmd.angular.z = max(min(0.8 * turn_error, 0.5), -0.5)

            self.cmd_pub.publish(cmd)
            return

        if self.mode == 'PASS_OBSTACLE':
            travelled = math.hypot(
                self.current_x - self.detour_start_x,
                self.current_y - self.detour_start_y,
            )

            cmd = Twist()

            if travelled >= 0.25 and self.target_path_clear():
                self.mode = 'GO_TO_TARGET'
                self.get_logger().info(
                    f'Target passage clear after {travelled:.2f} m. '
                    'Returning toward the target.'
                )
            elif travelled >= self.detour_distance:
                self.get_logger().info(
                    'Detour limit reached, but target passage is blocked. '
                    'Stopped.',
                    throttle_duration_sec=2.0,
                )
            elif self.front_distance < self.obstacle_stop_distance:
                self.get_logger().info(
                    'Detour path blocked. Waiting.',
                    throttle_duration_sec=2.0,
                )
            else:
                heading_error = self.detour_yaw - self.current_yaw
                heading_error = math.atan2(
                    math.sin(heading_error), math.cos(heading_error)
                )

                # Correct the heading before moving forward.
                if abs(heading_error) < 0.15:
                    cmd.linear.x = 0.12

                cmd.angular.z = max(
                    min(0.8 * heading_error, 0.4), -0.4
                )

            self.cmd_pub.publish(cmd)
            return
        # Calculate the remaining displacement to the target in metres.
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y

        distance = math.sqrt(dx * dx + dy * dy)
        target_angle = math.atan2(dy, dx)

        angle_error = target_angle - self.current_yaw
        # Wrap the heading error to [-pi, pi] for the shorter turn.
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

        cmd = Twist()

        if distance < 0.35:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.cmd_pub.publish(cmd)

            if not self.target_reached:
                self.get_logger().info('Target reached. Rover stopped.')
                self.target_reached = True

            return

        if abs(angle_error) > 0.25:
            cmd.linear.x = 0.0
            cmd.angular.z = max(min(0.5 * angle_error, 0.6), -0.6)
        else:
            cmd.linear.x = min(0.25, 0.25 * distance)
            cmd.angular.z = max(min(0.5 * angle_error, 0.4), -0.4)

        self.cmd_pub.publish(cmd)

        self.get_logger().info(
            f'x={self.current_x:.2f}, y={self.current_y:.2f}, '
            f'distance={distance:.2f}, angle_error={angle_error:.2f}',
            throttle_duration_sec=1.0,
        )
        


def main(args=None):
    rclpy.init(args=args)
    node = RoverGoToTarget()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()