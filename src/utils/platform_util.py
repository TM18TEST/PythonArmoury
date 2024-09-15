#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import platform


class PlatformUtil:
    LINUX_PLATFORM_NAME = "Linux"
    MACOS_PLATFORM_NAME = "Darwin"
    WINDOWS_PLATFORM_NAME = "Windows"

    @staticmethod
    def is_windows_platform() -> bool:
        return platform.system() == PlatformUtil.WINDOWS_PLATFORM_NAME
