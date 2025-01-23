#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Console Utility Class.
"""
import ctypes
import sys

from utils.log_ins import LogUtil
from utils.os_util import OsUtil
from utils.pyinstaller_util import PyInstallerUtil


class ConsoleUtil:
    @staticmethod
    def create_console(console_title: str = "Console"):
        """动态创建控制台窗口"""
        if not OsUtil.is_windows() or not PyInstallerUtil.is_run_in_pyinstaller():
            return
        if ctypes.windll.kernel32.GetConsoleWindow():
            return
        with LogUtil.get_lock():
            ctypes.windll.kernel32.AllocConsole()
            ctypes.windll.kernel32.SetConsoleTitleW(console_title)
            LogUtil.clear_console_handle_within_lock()
            sys.stdout = open("CONOUT$", "w")
            sys.stderr = open("CONOUT$", "w")
            LogUtil.add_console_handle_within_lock()

    @staticmethod
    def hide_console():
        """隐藏控制台窗口"""
        if not OsUtil.is_windows() or not PyInstallerUtil.is_run_in_pyinstaller():
            return
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)

    @staticmethod
    def show_console():
        """显示控制台窗口"""
        if not OsUtil.is_windows() or not PyInstallerUtil.is_run_in_pyinstaller():
            return
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 5)

    @staticmethod
    def close_console():
        """关闭控制台窗口"""
        if not OsUtil.is_windows() or not PyInstallerUtil.is_run_in_pyinstaller():
            return
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.kernel32.FreeConsole()


if __name__ == "__main__":
    sys.exit(0)
