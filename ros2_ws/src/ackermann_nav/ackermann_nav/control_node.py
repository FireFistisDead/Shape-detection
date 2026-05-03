import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point

class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')
        self.subscription = self.create_subscription(
            Point,
            '/target_error',
            self.error_callback,
            10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # PID / Control Parameters
        self.k_p = 1.2
        self.max_steer = 0.5
        self.speed = 0.6
        
        # Robustness State
        self.last_error_x = 0.0
        self.last_seen_time = self.get_clock().now()
        self.timeout_threshold = 1.0 # seconds
        self.last_steer = 0.0
        self.smoothing = 0.3 # EMA alpha
        
        self.get_logger().info('Robust Control Node started')

    def error_callback(self, msg):
        cmd = Twist()
        current_time = self.get_clock().now()
        
        if msg.z > 0:
            # Target found
            self.last_seen_time = current_time
            self.last_error_x = msg.x
            area = msg.y
            
            if area > 120000:
                # Reached target
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.get_logger().info('Target reached!')
            else:
                cmd.linear.x = self.speed
                target_steer = -self.k_p * msg.x
                
                # Smooth steering to prevent jerky camera movements
                self.last_steer = (self.smoothing * target_steer) + ((1 - self.smoothing) * self.last_steer)
                
                # Clamp steering
                cmd.angular.z = max(min(self.last_steer, self.max_steer), -self.max_steer)
        else:
            # Target lost
            time_since_last_seen = (current_time - self.last_seen_time).nanoseconds / 1e9
            
            if time_since_last_seen < self.timeout_threshold:
                # Maintain last known steering for a bit to recover from flickering
                cmd.linear.x = self.speed * 0.8
                cmd.angular.z = self.last_steer
            else:
                # Truly lost, enter search mode (circle)
                cmd.linear.x = 0.3
                cmd.angular.z = self.max_steer
            
        self.publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
