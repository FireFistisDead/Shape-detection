from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
import xacro

def generate_launch_description():
    pkg_dir = get_package_share_directory('ackermann_nav')
    
    world_file = os.path.join(pkg_dir, 'worlds', 'shapes.sdf')
    urdf_file = os.path.join(pkg_dir, 'urdf', 'ack.urdf.xacro')
    
    # Start Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )
    
    # Spawn robot
    doc = xacro.process_file(urdf_file)
    robot_desc = doc.toxml()
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[{'robot_description': robot_desc}]
    )
    
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-string', robot_desc,
                   '-name', 'ackerman_simple',
                   '-z', '0.2'],
        output='screen'
    )
    
    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
        ],
        output='screen'
    )
    
    # Nodes
    perception = Node(
        package='ackermann_nav',
        executable='perception_node',
        output='screen'
    )
    
    control = Node(
        package='ackermann_nav',
        executable='control_node',
        output='screen'
    )
    
    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        spawn,
        bridge,
        perception,
        control
    ])
