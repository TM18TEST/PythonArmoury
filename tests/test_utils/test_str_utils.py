#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: String Utility Class Test Cases.
"""

import unittest

from utils.str_util import StrUtil


class TestStrUtil(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_valid_base_number(self):
        self.assertFalse(StrUtil.is_valid_base_number(" 10 ", 16))  # False, 带非数字字符
        self.assertFalse(StrUtil.is_valid_base_number("", 16))  # False, 空字串

        self.assertTrue(StrUtil.is_valid_base_number("1010", 2))  # True, 二进制
        self.assertTrue(StrUtil.is_valid_base_number("0b1010", 2))  # True, 带0b前缀的二进制
        self.assertTrue(StrUtil.is_valid_base_number("755", 8))  # True, 八进制
        self.assertTrue(StrUtil.is_valid_base_number("0o755", 8))  # True, 带0o前缀的八进制
        self.assertTrue(StrUtil.is_valid_base_number("123", 10))  # True, 十进制
        self.assertTrue(StrUtil.is_valid_base_number("1A3F", 16))  # True, 十六进制
        self.assertTrue(StrUtil.is_valid_base_number("0x1A3F", 16))  # True, 带0x前缀的十六进制


if __name__ == '__main__':
    unittest.main()
