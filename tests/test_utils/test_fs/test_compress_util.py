#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Compress Utility Class Test Cases.
"""

import os
import unittest

from utils.fs.compress_util import CompressUtil
from utils.fs.fs_util import FsUtil
from utils.codec.hash_util import HashUtil


class TestCompressUtil(unittest.TestCase):
    def setUp(self):
        self.test_root_dir = os.path.join(FsUtil.get_current_project_root_path(), "tests")
        self.test_data_root_dir = os.path.join(self.test_root_dir, "test_data")
        self.test_class_data_root_dir = os.path.join(self.test_data_root_dir, "test_utils", "test_compress_util")
        FsUtil.remake_dirs(self.test_class_data_root_dir)

    def tearDown(self):
        FsUtil.force_remove(self.test_class_data_root_dir, not_exist_ok=True)

    def test_compress_then_decompress(self):
        # Prepare test data
        test_data_dir = os.path.join(self.test_class_data_root_dir, "test_compress_then_decompress")
        to_be_compress_dir = os.path.join(test_data_dir, "to_be_compress")
        os.makedirs(to_be_compress_dir, exist_ok=True)
        with open(os.path.join(to_be_compress_dir, "1.txt"), "w", encoding="utf-8") as f:
            f.write("Hello world Txt!")
        self.assertTrue(os.path.isfile(os.path.join(to_be_compress_dir, "1.txt")))
        with open(os.path.join(to_be_compress_dir, "2.log"), "w", encoding="utf-8") as f:
            f.write("Hello world Log!")
        self.assertTrue(os.path.isfile(os.path.join(to_be_compress_dir, "2.log")))

        # Compress the data
        compressed_file = to_be_compress_dir + ".zip"
        CompressUtil.compress(to_be_compress_dir, compressed_file, level=9)
        self.assertTrue(os.path.isfile(compressed_file))

        # Check the compressed data
        CompressUtil.check_zip_file(compressed_file)

        # Decompress the compressed data
        decompressed_dir = os.path.join(test_data_dir, "to_be_compress")
        CompressUtil.decompress(compressed_file, decompressed_dir)

        # Compare the hashsum of directory between before compress and decompressed
        compress_dir_hash = HashUtil.calculate_directory_hash(to_be_compress_dir)
        decompressed_dir_hash = HashUtil.calculate_directory_hash(decompressed_dir)
        self.assertEqual(compress_dir_hash, decompressed_dir_hash)
