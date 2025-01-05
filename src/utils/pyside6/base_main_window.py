#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base class for main window with common functionality.
"""
import contextlib
import ctypes
import inspect
import logging
import os
from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot

from utils.process_util import ProcessUtil
from utils.pyside6.msg_box_mgr import MsgBoxMgr


class BaseMainWindow(QMainWindow):
    """Base class for main window with common functionality."""

    def __init__(self, window_title: str, window_icon_file: str,
                 parent=None, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the main window with the specified title and icon.

        :param window_title: The title of the window.
        :param window_icon_file: The file path for the window icon.
        :param parent: The parent widget (optional).
        :param logger: A logging.Logger instance for logging (optional).
        """
        super().__init__(parent)
        self._logger = logger
        self._window_title: str = window_title
        self._window_icon_file: str = window_icon_file
        self._ui_log_printer = None
        self._single_proc_ctx = None
        self._init_window()
        self._acquire_windows_global_mutex()
        self._log("%s initialized.", self._window_title)

    def setup_ui_log_printer(self, ui_log_printer):
        """Set up the UI log printer for logging messages in the UI."""
        self._ui_log_printer = ui_log_printer

    def __del__(self):
        """Ensure that the global mutex is released when the window is destroyed."""
        self._log("Start destructing the main window.")
        with contextlib.suppress(Exception):
            self._release_windows_global_mutex()

    def _acquire_windows_global_mutex(self) -> None:
        """
        Acquire a global mutex to ensure that only one instance of the program runs at a time.

        Raises:
            Exception: If unable to acquire the mutex, indicating that another instance may be running.
        """
        try:
            self._single_proc_ctx = ProcessUtil.acquire_windows_global_mutex(self._window_title.replace(" ", ""))
        except Exception as e:
            if self._logger:
                self._logger.exception("Failed to acquire the single instance global mutex.")
            MsgBoxMgr.exec(self._window_title + " - Run Error",
                           "There is already a process instance of the same program running.",
                           QMessageBox.Icon.Critical)
            raise e
        self._log("Acquire the single instance global mutex success.")

    def _release_windows_global_mutex(self) -> None:
        """
        Release the acquired global mutex to allow other instances of the program to run.

        Logs a success message if the mutex is released, or a warning if no mutex was acquired.
        """
        if hasattr(self, '_single_proc_ctx') and self._single_proc_ctx:
            ProcessUtil.release_windows_global_mutex(self._single_proc_ctx)
            self._single_proc_ctx = None
            self._log("Release the acquired single instance global mutex success.")
        else:
            self._log("Unnecessary to release the acquired single instance global mutex.", level=logging.WARNING)

    def _init_window(self) -> None:
        """Initialize the window title, icon, and set the application taskbar icon."""
        # Set window title
        self.setWindowTitle(self._window_title)

        # Set window icon
        self.setWindowIcon(QIcon(self._window_icon_file))

        # Set App taskbar icon
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    def _log(self, message: str, *args, level: int = logging.INFO) -> None:
        """Log a message at the specified level with optional formatting."""
        if self._logger:
            if args:
                message = message % args
            self._logger.log(level, message)

    def ui_log(self, message: str, *args, level: int = logging.INFO) -> None:
        """
        Log messages in both UI and system logger with optional formatting.

        :param message: The log message to output, supports formatting.
        :param args: Arguments for formatting the log message.
        :param level: The logging level. Defaults to INFO.
        """
        # Format log messages
        if args:
            message = message % args

        # Print to the UI log box
        if self._ui_log_printer:
            level_str = logging.getLevelName(level)
            date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._ui_log_printer(f'{date_time} {level_str} {message}')

        # Print to system
        frame = inspect.currentframe().f_back
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        self._log(message + f" [Called from {filename}:{lineno}]", level=level)

    @Slot()
    def common_slot(self) -> None:
        """A common slot function."""
        self._log("Common slot triggered.")
        print("This is a common slot function.")

    @Slot()
    def save_file(self) -> None:
        """
        Save the contents of the text edit to a file.

        This method is meant to be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method.")
