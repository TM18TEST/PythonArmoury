#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Process Utility Class Test Cases.
"""

import unittest
import psutil

from utils.process_util import ProcessUtil


class TestProcessUtil(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_set_current_process_lowest_priority(self) -> None:
        self.assertEqual(psutil.NORMAL_PRIORITY_CLASS, ProcessUtil.get_current_process_priority())
        ProcessUtil.set_current_process_idle_priority()
        self.assertEqual(psutil.IDLE_PRIORITY_CLASS, ProcessUtil.get_current_process_priority())


if __name__ == '__main__':
    unittest.main()
