#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Base Utility Class Source Code.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import os
import sys
from typing import AnyStr


class BaseUtil:
    # Windows priority constant definition
    WIN_NORMAL_PRIORITY_CLASS = 0x00000020
    WIN_IDLE_PRIORITY_CLASS = 0x00000040
    WIN_HIGH_PRIORITY_CLASS = 0x00000080

    @staticmethod
    def get_project_root_path() -> AnyStr:
        current_dir: AnyStr = os.path.abspath(os.path.dirname(__file__))
        directory = current_dir
        while True:
            if os.path.isdir(os.path.join(directory, '.git')):
                return directory
            if directory == os.path.dirname(directory):
                raise ValueError(f'Path does not exist, current dir: {current_dir}')
            directory = os.path.dirname(directory)

    @staticmethod
    def get_process_root_path() -> AnyStr:
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller will create a temporary folder temp and store the path in _MEIPASS
            base_path = sys._MEIPASS
        else:
            base_path = BaseUtil.get_project_root_path()
        return base_path

    @staticmethod
    def is_empty(value) -> bool:
        # Check whether the value is None
        if value is None:
            return True

        # Check if it is a string and has zero length
        if isinstance(value, str) and len(value) == 0:
            return True

        # Check if it is a list, tuple, set, dictionary, and the length is zero
        if isinstance(value, (list, tuple, set, dict)) and len(value) == 0:
            return True

        # By default, objects are considered non-null
        return False
