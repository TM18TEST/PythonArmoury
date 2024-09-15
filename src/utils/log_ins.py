#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Log Utility Class Source Code.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import os
import logging
import tempfile
import threading

from config.project_config import ProjectConfig


class LogUtil:
    _logger = None
    _lock = threading.Lock()

    @staticmethod
    def _create_log_file() -> str:
        log_dir = os.path.join(tempfile.gettempdir(), ProjectConfig.LOG_DIR)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, ProjectConfig.LOG_FILE_NAME)
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
