#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Operating System Utility Class.
"""
import platform
import sys


class OsUtil:
    @staticmethod
    def is_windows():
        return platform.system() == "Windows"

    @staticmethod
    def is_linux():
        return platform.system() == "Linux"

    @staticmethod
    def is_mac():
        return platform.system() == "Darwin"


if __name__ == "__main__":
    sys.exit(0)
