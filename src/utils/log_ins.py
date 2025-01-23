#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Log Utility Class Source Code.
"""
import os
import logging
import tempfile
import threading
from datetime import datetime
from typing import Optional

from utils.fs.fs_util import FsUtil


class LogUtil:
    LOG_FMT: str = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - Thread:%(thread)d - %(message)s"
    _logger: Optional[logging.Logger] = None
    _lock: threading.Lock = threading.Lock()

    @staticmethod
    def _create_log_file() -> str:
        # logger
        log_dir = os.path.join(FsUtil.get_current_dir(), "log")
        log_file_name = datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"

        log_dir = os.path.join(tempfile.gettempdir(), log_dir)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, log_file_name)
        return log_file

    @classmethod
    def get_lock(cls) -> threading.Lock:
        return cls._lock

    @classmethod
    def clear_console_handle_within_lock(cls) -> None:
        # 移除已存在的 StreamHandler
        if cls._logger is not None:
            for handler in cls._logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    cls._logger.removeHandler(handler)

    @classmethod
    def clear_console_handle(cls) -> None:
        with cls._lock:
            cls.clear_console_handle_within_lock()

    @classmethod
    def create_console_log_handle(cls) -> logging.Handler:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(cls.LOG_FMT)
        console_handler.setFormatter(formatter)
        return console_handler

    @classmethod
    def add_console_handle_within_lock(cls) -> None:
        if cls._logger is not None:
            cls._logger.addHandler(cls.create_console_log_handle())

    @classmethod
    def add_console_handle(cls) -> None:
        with cls._lock:
            cls.add_console_handle_within_lock()

    @classmethod
    def get_logger(cls):
        with cls._lock:
            if cls._logger is None:
                cls._logger = logging.getLogger("logger")
                cls._logger.setLevel(logging.DEBUG)
                log_file = cls._create_log_file()
                file_handler = logging.FileHandler(log_file)
                formatter = logging.Formatter(cls.LOG_FMT)
                file_handler.setFormatter(formatter)
                cls._logger.addHandler(cls.create_console_log_handle())
                cls._logger.addHandler(file_handler)
            return cls._logger
