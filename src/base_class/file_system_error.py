#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Error Exceptions.
"""


class FileSystemError(Exception):
    """统一文件系统异常基类"""
    pass


class FsConnectionError(FileSystemError):
    pass


class FsFileNotFoundError(FileSystemError):
    pass


class FsPermissionError(FileSystemError):
    pass
