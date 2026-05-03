import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        self.publisher = self.create_publisher(Point, '/target_error', 10)
        self.br = CvBridge()
        self.get_logger().info('Perception Node started')

    def image_callback(self, msg):
        try:
            cv_image = self.br.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {e}')
            return

        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        
        # Red color bounds (Gazebo ambient 0.8 0.1 0.1)
        lower_red1 = np.array([0, 70, 20])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 20])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2
        
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        target_error = Point()
        target_error.z = -1.0 # default: not found
        
        if contours:
            # Find largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            if area > 100:
                # Calculate centroid
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    
                    height, width, _ = cv_image.shape
                    
                    # Normalize error to [-1, 1]
                    error_x = (cX - width / 2) / (width / 2)
                    
                    target_error.x = float(error_x)
                    target_error.y = float(area)
                    target_error.z = 1.0 # found
                    
        self.publisher.publish(target_error)

def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
