#!/bin/bash

ament_copyright rosbag_cloud_recorders rosbag_uploader_ros1_integration_tests s3_common s3_file_uploader
ament_cppcheck rosbag_cloud_recorders rosbag_uploader_ros1_integration_tests s3_common s3_file_uploader
ament_cpplint rosbag_cloud_recorders rosbag_uploader_ros1_integration_tests s3_common s3_file_uploader
ament_uncrustify rosbag_cloud_recorders rosbag_uploader_ros1_integration_tests s3_common s3_file_uploader
ament_xmllint rosbag_cloud_recorders rosbag_uploader_ros1_integration_tests s3_common s3_file_uploader