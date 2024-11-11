#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Base Utility Class Test Cases.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import unittest

from utils.base_util import BaseUtil


class TestBaseUtil(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_empty(self):
        self.assertTrue(BaseUtil.is_empty(None))
        self.assertTrue(BaseUtil.is_empty(''))
        self.assertFalse(BaseUtil.is_empty(' '))

    def test_is_any_empty(self):
        self.assertTrue(BaseUtil.is_any_empty(None, ' ', ' '))
        self.assertFalse(BaseUtil.is_any_empty(' ', ' ', ' '))
        self.assertTrue(BaseUtil.is_any_empty(None, '', ''))

    def test_is_all_empty(self):
        self.assertFalse(BaseUtil.is_all_empty(None, ' ', ' '))
        self.assertFalse(BaseUtil.is_all_empty(' ', ' ', ' '))
        self.assertTrue(BaseUtil.is_any_empty(None, '', ''))


if __name__ == '__main__':
    unittest.main()
