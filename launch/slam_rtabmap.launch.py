import os
import xacro
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription, conditions
from launch.actions import (DeclareLaunchArgument, GroupAction, IncludeLaunchDescription)
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution, ThisLaunchFileDir
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource

import launch.actions
import launch_ros.actions


def to_urdf(xacro_path, urdf_path=None):
    """Convert the given xacro file to URDF file.
    * xacro_path -- the path to the xacro file
    * urdf_path -- the path to the urdf file
    """
    # If no URDF path is given, use a temporary file
    if urdf_path is None:
        urdf_path = os.path.join(
            get_package_share_directory("afrl_ur_launch"),
            "urdf",
            "ur_withenvironment.urdf")
    # open and process file
    doc = xacro.process_file(xacro_path)
    # open the output file
    out = xacro.open_output(urdf_path)
    out.write(doc.toprettyxml(indent='  '))

    return urdf_path  # Return path to the urdf file

def generate_launch_description():
    # Note: tf_prefix is not supported as an argument to the xacro file for robot/joint state publishers
    # Convert xacro to urdf for robot_state_publisher and joint_state_publisher
    '''xacro_file = os.path.join(
            get_package_share_directory("afrl_ur_launch"),
            "urdf",
            "ur_withenvironment.urdf.xacro")
    print("Robot description xacro_file : {}".format(xacro_file))

    urdf_path = to_urdf(xacro_file) # convert, xacro to urdf
    urdf = open(urdf_path).read()
    print("Robot description urdf_path : {}".format(urdf_path))

    # rviz_config_file = PathJoinSubstitution([FindPackageShare("azure_kinect_ros_driver"), "rviz", "rtab_azure.rviz"])

    # Variable used for the flag to publish a standalone azure_description instead of the default robot_description parameter
    remappings = [('robot_description', 'azure_description')]'''

    return LaunchDescription([
    DeclareLaunchArgument(
        'overwrite_robot_description',
        default_value="false" ,
        description="Flag to publish a standalone azure_description instead of the default robot_description parameter."),
    DeclareLaunchArgument(
        'no_rviz',
        default_value="true"),
    ##############################################
    DeclareLaunchArgument(
        'depth_enabled',
        default_value="true",
        description="Enable or disable the depth camera"),
    DeclareLaunchArgument(
        'depth_mode',
        default_value="NFOV_UNBINNED",
        description="Set the depth camera mode, which affects FOV, depth range, and camera resolution. See Azure Kinect documentation for full details. Valid options: NFOV_UNBINNED, NFOV_2X2BINNED, WFOV_UNBINNED, WFOV_2X2BINNED, and PASSIVE_IR"),
    DeclareLaunchArgument(
        'depth_unit',
        default_value="16UC1",
        description='Depth distance units. Options are: "32FC1" (32 bit float metre) or "16UC1" (16 bit integer millimetre)'),
    DeclareLaunchArgument(
        'color_enabled',
        default_value="true",
        description="Enable or disable the color camera"),
    DeclareLaunchArgument(
        'color_format',
        default_value="bgra",
        description="The format of RGB camera. Valid options: bgra, jpeg"),
    DeclareLaunchArgument(
        'color_resolution',
        default_value="1536P",
        description="Resolution at which to run the color camera. Valid options: 720P, 1080P, 1440P, 1536P, 2160P, 3072P"),
    DeclareLaunchArgument(
        'fps',
        default_value="30",
        description="FPS to run both cameras at. Valid options are 5, 15, and 30"),
    DeclareLaunchArgument(
        'point_cloud',
        default_value="false",
        description="Generate a point cloud from depth data. Requires depth_enabled"),
    DeclareLaunchArgument(
        'rgb_point_cloud',
        default_value="false",
        description="Colorize the point cloud using the RBG camera. Requires color_enabled and depth_enabled"),
    DeclareLaunchArgument(
        'point_cloud_in_depth_frame',
        default_value="false",
        description="Whether the RGB pointcloud is rendered in the depth frame (true) or RGB frame (false). Will either match the resolution of the depth camera (true) or the RGB camera (false)."),
    DeclareLaunchArgument( # Not a parameter of the node, rather a launch file parameter
        'required',
        default_value="false",
        description="Argument which specified if the entire launch file should terminate if the node dies"),
    DeclareLaunchArgument(
        'sensor_sn',
        default_value="",
        description="Sensor serial number. If none provided, the first sensor will be selected"),
    DeclareLaunchArgument(
        'recording_file',
        default_value="",
        description="Absolute path to a mkv recording file which will be used with the playback api instead of opening a device"),
    DeclareLaunchArgument(
        'recording_loop_enabled',
        default_value="false",
        description="If set to true the recording file will rewind the beginning once end of file is reached"),
    DeclareLaunchArgument(
        'body_tracking_enabled',
        default_value="false",
        description="If set to true the joint positions will be published as marker arrays"),
    DeclareLaunchArgument(
        'body_tracking_smoothing_factor',
        default_value="0.0",
        description="Set between 0 for no smoothing and 1 for full smoothing"),
    DeclareLaunchArgument(
        'rescale_ir_to_mono8',
        default_value="false",
        description="Whether to rescale the IR image to an 8-bit monochrome image for visualization and further processing. A scaling factor (ir_mono8_scaling_factor) is applied."),
    DeclareLaunchArgument(
        'ir_mono8_scaling_factor',
        default_value="1.0",
        description="Scaling factor to apply when converting IR to mono8 (see rescale_ir_to_mono8). If using illumination, use the value 0.5-1. If using passive IR, use 10."),
    DeclareLaunchArgument(
        'imu_rate_target',
        default_value="100",
        description="Desired output rate of IMU messages. Set to 0 (default) for full rate (1.6 kHz)."),
    DeclareLaunchArgument(
        'wired_sync_mode',
        default_value="0",
        description="Wired sync mode. 0: OFF, 1: MASTER, 2: SUBORDINATE."),
    DeclareLaunchArgument(
        'subordinate_delay_off_master_usec',
        default_value="0",
        description="Delay subordinate camera off master camera by specified amount in usec."),
    launch_ros.actions.Node(
        package='azure_kinect_ros_driver',
        executable='node',
        output='screen',
        parameters=[
            {'depth_enabled': launch.substitutions.LaunchConfiguration('depth_enabled')},
            {'depth_mode': launch.substitutions.LaunchConfiguration('depth_mode')},
            {'depth_unit': launch.substitutions.LaunchConfiguration('depth_unit')},
            {'color_enabled': launch.substitutions.LaunchConfiguration('color_enabled')},
            {'color_format': launch.substitutions.LaunchConfiguration('color_format')},
            {'color_resolution': launch.substitutions.LaunchConfiguration('color_resolution')},
            {'fps': launch.substitutions.LaunchConfiguration('fps')},
            {'point_cloud': launch.substitutions.LaunchConfiguration('point_cloud')},
            {'rgb_point_cloud': launch.substitutions.LaunchConfiguration('rgb_point_cloud')},
            {'point_cloud_in_depth_frame': launch.substitutions.LaunchConfiguration('point_cloud_in_depth_frame')},
            {'sensor_sn': launch.substitutions.LaunchConfiguration('sensor_sn')},
            {'recording_file': launch.substitutions.LaunchConfiguration('recording_file')},
            {'recording_loop_enabled': launch.substitutions.LaunchConfiguration('recording_loop_enabled')},
            {'body_tracking_enabled': launch.substitutions.LaunchConfiguration('body_tracking_enabled')},
            {'body_tracking_smoothing_factor': launch.substitutions.LaunchConfiguration('body_tracking_smoothing_factor')},
            {'rescale_ir_to_mono8': launch.substitutions.LaunchConfiguration('rescale_ir_to_mono8')},
            {'ir_mono8_scaling_factor': launch.substitutions.LaunchConfiguration('ir_mono8_scaling_factor')},
            {'imu_rate_target': launch.substitutions.LaunchConfiguration('imu_rate_target')},
            {'wired_sync_mode': launch.substitutions.LaunchConfiguration('wired_sync_mode')},
            {'subordinate_delay_off_master_usec': launch.substitutions.LaunchConfiguration('subordinate_delay_off_master_usec')}]),

    DeclareLaunchArgument(
        'frame_id',
        default_value="camera_base",
        description="Visual/Icp odometry frame ID for TF"),
    DeclareLaunchArgument(
        'camera_info_topic',
        default_value="/depth/camera_info",
        description=""),
    DeclareLaunchArgument(
        'depth_topic',
        default_value="/depth/image_raw",
        description=""),
    DeclareLaunchArgument(
        'rgb_topic',
        default_value="/rgb_to_depth/image_raw",
        description=""),
    DeclareLaunchArgument(
        'queue_size',
        default_value="30",
        description=""),
    DeclareLaunchArgument(
        'rtabmap_viz',
        default_value="false",
        description=""),
    DeclareLaunchArgument(
        'rviz',
        default_value="true",
        description=""),
    DeclareLaunchArgument(
        'approx_sync',
        default_value="true",
        description="(sec) 0 means infinite interval duration (used with approx_sync=true)"),
    DeclareLaunchArgument(
        'rtabmap_args',
        default_value="--delete_db_on_start",
        description=""),
    IncludeLaunchDescription(
        PythonLaunchDescriptionSource(['/opt/ros/humble/share/rtabmap_launch/launch', '/rtabmap.launch.py']),
        launch_arguments={'frame_id': launch.substitutions.LaunchConfiguration('frame_id'),
                          'camera_info_topic' : launch.substitutions.LaunchConfiguration('camera_info_topic'),
                          'depth_topic' : launch.substitutions.LaunchConfiguration('depth_topic'),
                          'rgb_topic' : launch.substitutions.LaunchConfiguration('rgb_topic'),
                          'queue_size' : launch.substitutions.LaunchConfiguration('queue_size'),
                          'rtabmap_viz' : launch.substitutions.LaunchConfiguration('rtabmap_viz'),
                          'rviz' : launch.substitutions.LaunchConfiguration('rviz'),
                          'approx_sync' : launch.substitutions.LaunchConfiguration('approx_sync'),
                          'rtabmap_args' : launch.substitutions.LaunchConfiguration('rtabmap_args')
                          }.items(),
    ),
    ])