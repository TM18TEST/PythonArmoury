#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Network Utility Class Source Code.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

from ping3 import ping


class NetUtil:
    @staticmethod
    def is_server_pingable(dest_addr: str, timeout: int = 4) -> bool:
        try:
            resp_time = ping(dest_addr=dest_addr, timeout=timeout)
            if resp_time:
                return True
        except (TimeoutError, ConnectionError):
            pass
        except Exception:
            pass
        return False
