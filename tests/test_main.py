#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Test Cases Entry.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import os
import unittest

if __name__ == '__main__':
    # 创建测试套件
    loader = unittest.TestLoader()

    # 当前目录是 tests 目录
    current_dir = os.path.dirname(__file__)

    # 递归发现 tests 目录下的所有测试模块
    suite = loader.discover(start_dir=current_dir, pattern='*.py', top_level_dir=current_dir)

    # 运行测试
    runner = unittest.TextTestRunner()
    runner.run(suite)
