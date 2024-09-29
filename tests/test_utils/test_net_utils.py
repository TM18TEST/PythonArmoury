#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Utility Class Test Cases.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import unittest

from utils.net_util import NetUtil


class TestNetUtil(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_server_pingable(self):
        self.assertTrue(NetUtil.is_server_pingable(dest_addr="www.baidu.com", timeout=10))
        self.assertTrue(NetUtil.is_server_pingable(dest_addr="1.1.1.1", timeout=4))
        self.assertFalse(NetUtil.is_server_pingable(dest_addr="63.254.254.254", timeout=3))


if __name__ == '__main__':
    unittest.main()
