#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Test Cases Main Used to Run All Test Cases.
"""

import os
import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    current_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir=current_dir, pattern='*.py', top_level_dir=current_dir)
    runner = unittest.TextTestRunner()
    runner.run(suite)
