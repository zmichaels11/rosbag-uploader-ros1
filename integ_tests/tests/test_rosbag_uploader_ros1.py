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

import filecmp
import os
import sys
import tempfile
import unittest

import actionlib

from file_uploader_msgs.msg import UploadFilesAction, UploadFilesGoal

import rospy

import rostest

from s3_client import S3Client

PKG = 'rosbag_uploader_ros1_integration_tests'
NAME = 'rosbag_uploader_ros1_integration_tests'
ACTION = '/s3_file_uploader/UploadFiles'
TEST_NODE_NAME = 'upload_files_action_client'
AWS_DEFAULT_REGION = 'us-west-2'


class TestS3FileUploader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rospy.init_node(TEST_NODE_NAME, log_level=rospy.DEBUG)
        s3 = S3Client(extract_s3_region())
        s3_bucket_name = rospy.get_param('/s3_file_uploader/s3_bucket')
        s3.create_bucket(s3_bucket_name)
        s3.wait_for_bucket_create(s3_bucket_name)

    @classmethod
    def tearDownClass(cls):
        s3 = S3Client(extract_s3_region())
        s3_bucket_name = rospy.get_param('/s3_file_uploader/s3_bucket')
        s3.delete_bucket(s3_bucket_name)

    def setUp(self):
        self.s3_bucket = rospy.get_param('/s3_file_uploader/s3_bucket')
        self.s3_region = extract_s3_region()
        self.s3_client = S3Client(self.s3_region)
        self.s3_key_prefix = 'foo/bar'
        self.objects_to_delete = []

    def tearDown(self):
        # delete any temp files created in the bucket as a part of tests
        contents = self.s3_client.list_objects(self.s3_bucket)
        objects_to_delete = map(
            lambda content: content['Key'],
            filter(
                lambda obj: obj['Key'] in self.objects_to_delete,
                contents
            )
        )
        self.s3_client.delete_objects(self.s3_bucket, objects_to_delete)

    def test_upload_file(self):
        client = self._create_upload_files_action_client()
        content_to_upload = 's3 file uploader integration test content'
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            result = self._upload_temp_file(
                client,
                content_to_upload,
                temp_file
            )
            self._assert_successful_upload(result, temp_file.name)

    def _create_upload_files_action_client(self):
        client = actionlib.SimpleActionClient(ACTION, UploadFilesAction)
        res = client.wait_for_server()
        self.assertTrue(res, 'Failed to connect to action server')
        return client

    def _upload_temp_file(self, client, content_to_upload, temp_file):
        temp_file.write(content_to_upload)
        temp_file.flush()
        goal = UploadFilesGoal(
            upload_location=self.s3_key_prefix,
            files=[temp_file.name]
        )
        client.send_goal(goal)
        client.wait_for_result(rospy.Duration.from_sec(15.0))
        return client.get_result()

    def _assert_successful_upload(self, result, temp_file_name):
        self.assertEqual(
            len(result.files_uploaded),
            1,
            'Found %d files' % len(result.files_uploaded))
        uploaded_s3_file_path = result.files_uploaded[0]
        # mark the uploaded test file for delete upon tearDown
        self.objects_to_delete.append(uploaded_s3_file_path)
        uploaded_s3_key_prefix, uploaded_s3_key = os.path.split(
            uploaded_s3_file_path)
        self.assertEqual(
            uploaded_s3_key_prefix,
            self.s3_key_prefix,
            'File uploaded to unexpected location in s3')
        self.assertEqual(
            uploaded_s3_key,
            os.path.basename(temp_file_name),
            'Uploaded file name mismatch')
        self._assert_uploaded_content(uploaded_s3_file_path, temp_file_name)

    def _assert_uploaded_content(self, s3_key, temp_file_name):
        with tempfile.NamedTemporaryFile() as f:
            self.s3_client.download_file(self.s3_bucket, s3_key, f.name)
            self.assertTrue(
                filecmp.cmp(f.name, temp_file_name),
                'Local file content did not match uploaded content')


def extract_s3_region():
    s3_region = rospy.get_param(
        '/s3_file_uploader/aws_client_configuration/region')
    if not s3_region:
        return AWS_DEFAULT_REGION
    return s3_region


if __name__ == '__main__':
    rostest.rosrun(PKG, NAME, TestS3FileUploader, sys.argv)