#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File Utility Class Source Code.
"""

class FileUtil:
    @staticmethod
    def is_binary_file(file_path: str) -> bool:
        """检查文件是否为二进制文件。

        Args:
            file_path (str): 文件路径。

        Returns:
            bool: 如果是二进制文件则返回 True，否则返回 False。
        """
        try:
            with open(file_path, 'rb') as file:
                # 读取部分内容检查是否包含非文本字符
                chunk = file.read(1024)
                return b'\0' in chunk
        except Exception as e:
            print(f"无法检查文件 {file_path} 是否为二进制: {e}")
            return False
