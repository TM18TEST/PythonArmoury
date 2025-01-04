#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Utility Class Source Code.
"""

import os
import sys
from typing import AnyStr


class PyInstallerUtil:
    @staticmethod
    def is_run_in_pyinstaller_bundle() -> bool:
        return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

    @staticmethod
    def get_bundle_dir_absolute_path() -> str:
        # PyInstaller will create a temporary folder temp and store the path in _MEIPASS
        if PyInstallerUtil.is_run_in_pyinstaller_bundle():
            return sys._MEIPASS
        raise RuntimeError("Not running from a packaged exe file.")

    @staticmethod
    def get_bundle_exe_file_absolute_path() -> str:
        if PyInstallerUtil.is_run_in_pyinstaller_bundle():
            return sys.executable
        raise RuntimeError("Not running from a packaged exe file.")

    @staticmethod
    def is_run_from_packaged_one_exe_file() -> bool:
        exe_dir = os.path.dirname(PyInstallerUtil.get_bundle_exe_file_absolute_path())
        resource_dir = PyInstallerUtil.get_bundle_dir_absolute_path()
        return resource_dir and exe_dir != resource_dir

    @staticmethod
    def get_packaged_exe_file_path() -> str:
        if PyInstallerUtil.is_run_in_pyinstaller_bundle():
            return sys.executable
        raise RuntimeError("Not running from a packaged exe file.")

    @staticmethod
    def get_packaged_exe_file_dir() -> AnyStr:
        return os.path.dirname(PyInstallerUtil.get_packaged_exe_file_path())

    @staticmethod
    def get_resource_root_dir() -> AnyStr:
        if PyInstallerUtil.is_run_from_packaged_one_exe_file():
            return PyInstallerUtil.get_bundle_dir_absolute_path()
        else:
            return os.path.join(PyInstallerUtil.get_packaged_exe_file_dir(), '_internal')
