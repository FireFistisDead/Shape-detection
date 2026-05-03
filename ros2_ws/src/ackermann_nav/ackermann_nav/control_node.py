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
        
        self.k_p = 1.0
        self.max_steer = 0.5
        self.speed = 0.5
        self.get_logger().info('Control Node started')

    def error_callback(self, msg):
        cmd = Twist()
        
        if msg.z > 0:
            # Target found
            area = msg.y
            if area > 100000:
                # Reached target
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
                self.get_logger().info('Target reached, stopping.')
            else:
                cmd.linear.x = self.speed
                # msg.x is normalized error [-1, 1]. Positive means target is right.
                # Right steer in ROS is negative angular.z
                steer = -self.k_p * msg.x
                
                # Clamp steering
                if steer > self.max_steer: steer = self.max_steer
                elif steer < -self.max_steer: steer = -self.max_steer
                
                cmd.angular.z = steer
        else:
            # Target lost, just drive forward slowly and steer to search
            # Ensure Ackermann constraint (always moving if steering)
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
