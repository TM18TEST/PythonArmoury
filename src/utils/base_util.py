#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Base Utility Class Source Code.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import os
import sys

from utils.fs_util import FsUtil


class BaseUtil:
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
