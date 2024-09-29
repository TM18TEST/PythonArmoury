#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Network Utility Class Source Code.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

from ping3 import ping


class NetUtil:
    """
    A utility class for network-related operations.
    """
    @staticmethod
    def is_server_pingable(dest_addr: str, timeout: int = 4) -> bool:
        """
        Determine if the server at the specified address is reachable via ping.

        Parameters:
            dest_addr (str): The destination address to ping.
            timeout (int): The maximum time in seconds to wait for a response.

        Returns:
            bool: True if the server is reachable; False otherwise.
        """
        try:
            return ping(dest_addr=dest_addr, timeout=timeout) is not None
        except (TimeoutError, ConnectionError):
            return False
