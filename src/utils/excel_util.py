#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import sys


class CellUnit:
    def __init__(self, row: int = None, column: int = None, value: str = None):
        self.row: int = row
        self.column: int = column
        self.value: str = value


if __name__ == "__main__":
    sys.exit(0)
