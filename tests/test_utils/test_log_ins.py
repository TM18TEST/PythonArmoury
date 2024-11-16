#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Log Utility Class Test Cases.
"""

import unittest

from utils.log_ins import LogUtil


class TestLogUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_logger(self):
        logger1 = LogUtil.get_logger()
        logger2 = LogUtil.get_logger()
        self.assertEqual(logger1, logger2)


if __name__ == '__main__':
    unittest.main()
