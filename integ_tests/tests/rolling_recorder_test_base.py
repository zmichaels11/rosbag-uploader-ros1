#!/usr/bin/env python
# Copyright (c) 2020, Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://aws.amazon.com/apache2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import glob
import os
import sys
import time
import unittest

from std_msgs.msg import String

import rosbag
import rosnode
import rospy
import rostest
import rostopic

TEST_NODE_NAME = 'test_rolling_recorder_client'
ROLLING_RECORDER_NODE_START_TIMEOUT = 5

class RollingRecorderTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rospy.init_node(TEST_NODE_NAME, log_level=rospy.DEBUG)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.bag_rollover_time = rospy.get_param("~bag_rollover_time")
        self.topics_to_record = rospy.get_param("~topics_to_record")
        self.rosbag_directory = rospy.get_param("~write_directory")

    def tearDown(self):
        pass

    def get_latest_bag_by_regex(self, regex_pattern):
        files = glob.iglob(os.path.join(self.rosbag_directory, regex_pattern))
        paths = [os.path.join(self.rosbag_directory, filename) for filename in files]
        paths_sorted = sorted(paths, key=os.path.getctime, reverse=True)
        return paths_sorted[0]

    def wait_for_rolling_recorder_nodes(self):
        required_nodes = set([
            '/rolling_recorder',
            '/rosbag_record'
        ])
        while not required_nodes.issubset(rosnode.get_node_names()):
            time.sleep(0.1)

    def wait_for_rolling_recorder_node_to_subscribe_to_topic(self):
        rostopic.wait_for_subscriber(self.test_publisher, ROLLING_RECORDER_NODE_START_TIMEOUT)