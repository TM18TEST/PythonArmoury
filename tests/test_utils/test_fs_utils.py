#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Utility Class Test Cases.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import os
import unittest

from utils.fs_util import FsUtil
from utils.base_util import BaseUtil


class TestFsUtil(unittest.TestCase):
    def setUp(self):
        self.test_root_dir = os.path.join(BaseUtil.get_project_root_path(), "tests")
        self.test_data_root_dir = os.path.join(self.test_root_dir, "test_data")
        self.test_class_data_root_dir = os.path.join(self.test_data_root_dir, "test_utils", "test_fs_utils")

    def tearDown(self):
        FsUtil.remove_path(self.test_class_data_root_dir)

    def test_is_empty_directory(self):
        test_data_dir = os.path.join(self.test_class_data_root_dir, "test_is_empty_directory")
        FsUtil.remake_dirs(test_data_dir)

        # Pass empty directory
        self.assertTrue(FsUtil.is_empty_directory(test_data_dir))

        # Pass file
        file_path = os.path.join(test_data_dir, "test.txt")
        with open(file_path, 'w') as file:
            file.write("Hello world!")
        self.assertFalse(FsUtil.is_empty_directory(file_path))

        # Pass non-empty directory
        self.assertFalse(FsUtil.is_empty_directory(test_data_dir))

        # Pass non-exist object
        self.assertFalse(FsUtil.is_empty_directory(os.path.join(test_data_dir, "non_exist")))

    def test_remake_dirs(self):
        test_data_dir = os.path.join(self.test_class_data_root_dir, "test_remake_dirs")
        FsUtil.remake_dirs(test_data_dir)
        self.assertTrue(FsUtil.is_empty_directory(test_data_dir))

        with open(os.path.join(test_data_dir, "test.txt"), 'w') as file:
            file.write("Hello world!")
        FsUtil.remake_dirs(test_data_dir)
        self.assertTrue(FsUtil.is_empty_directory(test_data_dir))

        FsUtil.remove_path(test_data_dir)
        with open(test_data_dir, 'w') as file:
            file.write("Hello world!")
        FsUtil.remake_dirs(test_data_dir)
        self.assertTrue(FsUtil.is_empty_directory(test_data_dir))

        FsUtil.remove_path(test_data_dir)

    def test_move_path_file(self):
        test_data_dir = os.path.join(self.test_class_data_root_dir, "test_move_path")
        FsUtil.remake_dirs(test_data_dir)

        dir1 = os.path.join(test_data_dir, "dir1")
        FsUtil.remake_dirs(dir1)
        dir2 = os.path.join(test_data_dir, "dir2")
        FsUtil.remake_dirs(dir2)
        file_path = os.path.join(dir1, "test.txt")
        with open(file_path, 'w') as f:
            f.write("Hello world!")

        FsUtil.move_path(file_path, dir2)

        self.assertTrue(FsUtil.is_empty_directory(dir1))
        self.assertTrue(os.path.isfile(os.path.join(dir2, "test.txt")))
        with open(os.path.join(dir2, "test.txt"), 'r') as file:
            self.assertEqual("Hello world!", file.read())

    def test_move_path_dir_with_content(self):
        test_data_dir = os.path.join(self.test_class_data_root_dir, "test_move_path")
        FsUtil.remake_dirs(test_data_dir)

        dir1 = os.path.join(test_data_dir, "dir1")
        FsUtil.remake_dirs(dir1)
        dir2 = os.path.join(test_data_dir, "dir2")
        FsUtil.remake_dirs(dir2)

        content_dir = os.path.join(dir1, "content_dir")
        FsUtil.remake_dirs(content_dir)
        with open(os.path.join(content_dir, "test.txt"), 'w') as file:
            file.write("Hello world!")

        FsUtil.move_path(content_dir, dir2)

        self.assertTrue(FsUtil.is_empty_directory(dir1))
        self.assertTrue(os.path.isdir(os.path.join(dir2, "content_dir")))
        self.assertTrue(os.path.isfile(os.path.join(dir2, "content_dir", "test.txt")))
        with open(os.path.join(dir2, "content_dir", "test.txt"), 'r') as file:
            self.assertEqual("Hello world!", file.read())

    def test_move_path_dir_without_content(self):
        test_data_dir = os.path.join(self.test_class_data_root_dir, "test_move_path")
        FsUtil.remake_dirs(test_data_dir)

        dir1 = os.path.join(test_data_dir, "dir1")
        FsUtil.remake_dirs(dir1)
        dir2 = os.path.join(test_data_dir, "dir2")
        FsUtil.remake_dirs(dir2)

        content_dir = os.path.join(dir1, "content_dir")
        FsUtil.remake_dirs(content_dir)

        FsUtil.move_path(content_dir, dir2)

        self.assertTrue(FsUtil.is_empty_directory(dir1))
        self.assertTrue(os.path.isdir(os.path.join(dir2, "content_dir")))


if __name__ == '__main__':
    unittest.main()
