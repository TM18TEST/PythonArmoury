#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Utility Class Test Cases.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import os
import unittest
from unittest.mock import patch

from utils.fs_util import FsUtil


class TestFsUtil(unittest.TestCase):
    def setUp(self):
        self.test_root_dir = os.path.join(FsUtil.get_current_project_root_path(), "tests")
        self.test_data_root_dir = os.path.join(self.test_root_dir, "test_data")
        self.test_class_data_root_dir = os.path.join(self.test_data_root_dir, "test_utils", "test_fs_utils")

    def tearDown(self):
        try:
            FsUtil.remove_path(self.test_class_data_root_dir)
        except FileNotFoundError:
            pass

    @patch.object(FsUtil, 'get_project_root_path', return_value='mocker')
    def test_get_project_root_path(self, mocker):
        self.assertEqual(FsUtil.get_project_root_path(), 'mocker')

        # Verify whether the stubbed method is called once
        mocker.assert_called_once()

    def test_get_current_project_root_path(self):
        current_project_root_path: str = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.assertEqual(current_project_root_path, FsUtil.get_current_project_root_path())

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

    def test_get_file_extension(self):
        self.assertEqual(FsUtil.get_file_extension("D:\\path\\file.extension"), ".extension")
        self.assertEqual(FsUtil.get_file_extension("D:\\path\\file.ext1.ext2"), ".ext2")


if __name__ == '__main__':
    unittest.main()
