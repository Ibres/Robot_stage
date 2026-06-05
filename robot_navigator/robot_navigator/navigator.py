#!/usr/bin/env python3

import math
import rclpy

from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from tf_transformations import euler_from_quaternion

GO_TO_GOAL = "GO_TO_GOAL"
AVOID_OBSTACLE = "AVOID_OBSTACLE"
MISSION_COMPLETE = "MISSION_COMPLETE"


class Navigator(Node):

    def __init__(self):
        super().__init__("navigator")
        self.odom_sub = self.create_subscription(Odometry, "/odom", self.odom_callback, 10)
        self.scan_sub = self.create_subscription(LaserScan, "/base_scan", self.scan_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.timer = self.create_timer(0.1, self.control_loop)
        self.avoid_counter = 0

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.front = float("inf")
        self.left = float("inf")
        self.right = float("inf")

        self.goals = [(7.0, 7.0), (7.0, -3.0)]
        self.goal_index = 0
        self.state = GO_TO_GOAL

        self.get_logger().info("Navigator started")

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        _, _, self.yaw = euler_from_quaternion([q.x, q.y, q.z, q.w])

    def scan_callback(self, msg):
        ranges = [r if math.isfinite(r) else msg.range_max for r in msg.ranges]

        n = len(ranges)
        center = n // 2

        self.front = min(ranges[center-15:center+15])
        self.left = min(ranges[int(0.75*n):])
        self.right = min(ranges[:int(0.25*n)])

        self.get_logger().info(
            f"F:{self.front:.2f} L:{self.left:.2f} R:{self.right:.2f}"
    )
    def normalize_angle(self, angle):
        while angle > math.pi: angle -= 2 * math.pi
        while angle < -math.pi: angle += 2 * math.pi
        return angle

    def stop_robot(self):
        cmd = Twist()
        self.cmd_pub.publish(cmd)

    def go_to_goal(self):
        goal_x, goal_y = self.goals[self.goal_index]

        dx = goal_x - self.x
        dy = goal_y - self.y

        distance = math.hypot(dx, dy)

        desired_yaw = math.atan2(dy, dx)
        yaw_error = self.normalize_angle(desired_yaw - self.yaw)
        
        self.get_logger().info(
            f"x={self.x:.2f} "
            f"y={self.y:.2f} "
            f"yaw={self.yaw:.2f} "
            f"dist={distance:.2f} "
            f"err={yaw_error:.2f}"
)

        if distance < 0.3:
            self.goal_index += 1

            if self.goal_index >= len(self.goals):
                self.state = MISSION_COMPLETE
                self.stop_robot()

            return

        if self.front < 0.6:
            self.state = AVOID_OBSTACLE
            self.avoid_counter = 12
            return

        cmd = Twist()
        if abs(yaw_error) > 0.3:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5 * yaw_error
        else:
            cmd.linear.x = 0.3
            cmd.angular.z = 0.2 * yaw_error
        self.cmd_pub.publish(cmd)
        

    def avoid_obstacle(self):
        cmd = Twist()
        cmd.linear.x = 0.05
        cmd.angular.z = 0.6 if self.left > self.right else -0.6
        self.cmd_pub.publish(cmd)

    def control_loop(self):
        if self.state == MISSION_COMPLETE:
            self.stop_robot()

        elif self.state == GO_TO_GOAL:
            self.go_to_goal()

        elif self.state == AVOID_OBSTACLE:
            self.avoid_counter -= 1

        if self.avoid_counter <= 0:
            self.state = GO_TO_GOAL

        self.avoid_obstacle()
def main(args=None):
    rclpy.init(args=args)
    node = Navigator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.stop_robot()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
