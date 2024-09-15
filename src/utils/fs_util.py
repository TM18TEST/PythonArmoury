#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Utility Class Source Code.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""
import hashlib
import os
import shutil
from pathlib import Path
from typing import List
import tempfile


class FsUtil:
    @staticmethod
    def get_subdirectories_obj(path: str) -> List[Path]:
        p = Path(path)
        return [subdir for subdir in p.iterdir() if subdir.is_dir()]

    @staticmethod
    def get_subdirectory_names(path: str) -> List[str]:
        p = Path(path)
        return [subdir.name for subdir in p.iterdir() if subdir.is_dir()]

    @staticmethod
    def get_os_temp_dir() -> str:
        return tempfile.gettempdir()

    @staticmethod
    def is_empty_directory(path: str) -> bool:
        return os.path.isdir(path) and not os.listdir(path)

    @staticmethod
    def remove_path(path: str) -> None:
        """
        Remove specified file, empty directory or non-empty directory.

        :param path: The path of object to be removed.
        """
        if os.path.isfile(path):
            # Remove file
            os.remove(path)
        elif os.path.isdir(path):
            # Try to remove empty directory
            try:
                os.rmdir(path)
            except OSError:
                # Remove the directory by calling "shutil.rmtree" if the directory is not empty
                shutil.rmtree(path)
        else:
            if not os.path.exists(path):
                raise FileNotFoundError("The path({}) is not exist.".format(path))
            else:
                raise TypeError("The path({}) neither a file nor a directory.".format(path))

    @staticmethod
    def remake_dirs(path: str) -> None:
        if os.path.exists(path):
            FsUtil.remove_path(path)
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def move_path(src: str, dst_dir: str):
        """
        Cut file(s) or directory to the specified directory.

        :param src: Source file or directory path
        :param dst_dir: target directory path
        """
        # Make sure the target directory exists
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir, exist_ok=True)

        # Get the base name of the source path
        basename = os.path.basename(src)
        # Construct target path
        dst = os.path.join(dst_dir, basename)

        # Determine whether the source path is a file or a directory
        if os.path.isfile(src):
            # If it is a file, move the file
            shutil.move(src, dst)
        elif os.path.isdir(src):
            # If it is a directory, move the directory
            shutil.move(src, dst)
        else:
            # The destination directory does not exist
            raise NotADirectoryError("Target directory not exist: {}".format(dst_dir))

    @staticmethod
    def calculate_sha1(file_path) -> str:
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as file:
            while chunk := file.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()

    @staticmethod
    def search_files_in_dir(directory: str, target_filename: str) -> List[str]:
        matches = []
        # os.walk 递归地遍历目录树
        for root, dirs, files in os.walk(directory):
            # 检查每个文件是否匹配目标文件名
            if target_filename in files:
                # 构建文件的绝对路径并添加到结果列表
                matches.append(os.path.join(root, target_filename))
        return matches
