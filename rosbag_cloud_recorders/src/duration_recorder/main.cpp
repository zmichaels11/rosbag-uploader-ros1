/*
 * Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */

#include <ros/ros.h>
#include <duration_recorder/duration_recorder.h>
#include <utils/rosbag_file_manager.h>

int main(int argc, char* argv[])
{
  ros::init(argc, argv, "rosbag_duration_recorder");
  Aws::Rosbag::DurationRecorder duration_recorder();
  Aws::Rosbag::Utils::RosbagFileManager rosbag_file_manager();
  ros::spin();
  return 0;
}