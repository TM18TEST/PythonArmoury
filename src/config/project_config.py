#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import os
from datetime import datetime

from utils.base_util import BaseUtil


class ProjectConfig:
    APP_NAME = "TM18 Python Armoury"
    APP_COMPACT_NAME = APP_NAME.replace(" ", "")
    APP_FILE_SHORT_NAME = APP_NAME.replace(" ", "_")

    SEMAPHORE_NAME = APP_COMPACT_NAME + "Semaphore"
    PROCESS_NAME = APP_FILE_SHORT_NAME + ".exe"
    APP_AUTHOR = "Testing Department Team"
    APP_VERSION = "0.1.1_Alpha_20240915193122_dd8657db"
    COMPANY_NAME = "Xiamen Tianma Display Technology Co., Ltd."
    ICON_FILE = os.path.join(BaseUtil.get_process_root_path(), 'resource', 'images', 'icon.ico')

    # logger
    LOG_DIR = os.path.join("TM18", "Log", APP_COMPACT_NAME)
    LOG_FILE_NAME = APP_FILE_SHORT_NAME.lower() + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
