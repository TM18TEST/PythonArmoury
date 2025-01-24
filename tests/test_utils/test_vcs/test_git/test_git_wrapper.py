#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Utility Class Test Cases.
"""

import os
import unittest

import git

from utils.vcs.git.git_wrapper import GitWrapper
from utils.codec.hash_util import HashUtil
from utils.fs.fs_util import FsUtil


class TestGitBase(unittest.TestCase):
    def setUp(self):
        self.test_root_dir = os.path.join(FsUtil.get_current_project_root_path(), "tests")
        self.test_data_root_dir = os.path.join(self.test_root_dir, "test_data")
        self.test_class_data_root_dir = os.path.join(self.test_data_root_dir,
                                                     "test_tool_sets", "test_bases", "test_git", "test_git_base")

    def tearDown(self):
        FsUtil.force_remove(self.test_class_data_root_dir, not_exist_ok=True)

    def test_clear_git_repository_except_metadata(self):
        test_data_dir = os.path.join(self.test_class_data_root_dir, "test_clear_git_repository_except_metadata")
        FsUtil.remake_dirs(test_data_dir)

        repo: git.Repo = git.Repo.init(test_data_dir)
        repo.close()
        hash_before: str = HashUtil.calculate_directory_hash(test_data_dir)
        self.assertFalse(FsUtil.is_empty_dir(test_data_dir))

        file_path1: str = os.path.join(test_data_dir, "test_file.txt")
        with open(file_path1, "w", encoding="utf-8"):
            pass
        self.assertTrue(os.path.exists(file_path1))

        dir_path: str = os.path.join(test_data_dir, "test_dir")
        os.makedirs(dir_path)
        file_path2: str = os.path.join(dir_path, "test_file2.txt")
        with open(file_path2, "w", encoding="utf-8"):
            pass
        self.assertTrue(os.path.exists(file_path2))

        GitWrapper.clear_git_repository_except_metadata(test_data_dir)
        self.assertFalse(os.path.exists(file_path1))
        self.assertFalse(os.path.exists(dir_path))
        self.assertFalse(os.path.exists(file_path2))
        hash_after: str = HashUtil.calculate_directory_hash(test_data_dir)
        self.assertEqual(hash_before, hash_after)

