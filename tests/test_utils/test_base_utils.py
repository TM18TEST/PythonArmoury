#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Base Utility Class Test Cases.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import unittest
from unittest.mock import patch

from utils.base_util import BaseUtil


class TestBaseUtil(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch.object(BaseUtil, 'get_project_root_path', return_value='mocker')
    def test_get_project_root_path(self, mocker):
        self.assertEqual(BaseUtil.get_project_root_path(), 'mocker')

        # 验证被打桩方法是否被调用一次
        mocker.assert_called_once()

    def test_is_empty(self):
        self.assertTrue(BaseUtil.is_empty(None))
        self.assertTrue(BaseUtil.is_empty(''))
        self.assertFalse(BaseUtil.is_empty(' '))


if __name__ == '__main__':
    unittest.main()
