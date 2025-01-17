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
from utils.fs.fs_util import FsUtil


class LogUtil:
    _logger = None
    _lock = threading.Lock()

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
    def get_logger(cls):
        with cls._lock:
            if cls._logger is None:
                cls._logger = logging.getLogger("logger")
                cls._logger.setLevel(logging.DEBUG)
                console_handler = logging.StreamHandler()
                log_file = cls._create_log_file()
                file_handler = logging.FileHandler(log_file)
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - '
                                              'Thread:%(thread)d - %(message)s')
                console_handler.setFormatter(formatter)
                file_handler.setFormatter(formatter)
                cls._logger.addHandler(console_handler)
                cls._logger.addHandler(file_handler)
            return cls._logger
