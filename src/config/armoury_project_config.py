#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime

from utils.fs.fs_util import FsUtil


class ArmouryProjectConfig:
    APP_NAME = "Python Armoury"
    APP_COMPACT_NAME = APP_NAME.replace(" ", "")
    APP_FILE_SHORT_NAME = APP_NAME.replace(" ", "_")

    SEMAPHORE_NAME = APP_COMPACT_NAME + "Semaphore"
    PROCESS_NAME = APP_FILE_SHORT_NAME + ".exe"
    APP_AUTHOR = "Auther"
    APP_VERSION = "0.0.1_Alpha"
    COMPANY_NAME = "XXX Co., Ltd."
    ICON_FILE = os.path.join(FsUtil.get_process_root_path(), 'resource', 'images', 'icon.ico')

    # logger
    LOG_DIR = os.path.join("Log", APP_COMPACT_NAME)
    LOG_FILE_NAME = APP_FILE_SHORT_NAME.lower() + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
