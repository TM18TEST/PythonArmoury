#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Base Utility Class Source Code.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""


class BaseUtil:
    """
    A utility class for common operations.
    """

    @staticmethod
    def is_empty(value) -> bool:
        """
        Check if the given value is considered empty.

        Args:
            value: The value to check for emptiness.

        Returns:
            bool: True if the value is empty; False otherwise.
        """
        # Check whether the value is None
        if value is None:
            return True

        # Check if it is a string and has zero length
        if isinstance(value, str):
            return len(value) == 0

        # Check if it is a list, tuple, set, or dictionary, and the length is zero
        if isinstance(value, (list, tuple, set, dict)):
            return len(value) == 0

        # By default, objects are considered non-empty
        return False
