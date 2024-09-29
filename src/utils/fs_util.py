#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Utility Class Source Code.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""
import glob
import hashlib
import os
import shutil
import sys
from pathlib import Path
import tempfile
from typing import AnyStr


class FsUtil:
    @staticmethod
    def get_project_root_path() -> AnyStr:
        current_dir: AnyStr = os.path.abspath(os.path.dirname(__file__))
        directory = current_dir
        while True:
            if os.path.isdir(os.path.join(directory, '.git')):
                return directory
            if directory == os.path.dirname(directory):
                raise ValueError(f'Path does not exist, current dir: {current_dir}')
            directory = os.path.dirname(directory)

    @staticmethod
    def get_current_project_root_path() -> AnyStr:
        current_dir: AnyStr = os.path.abspath(os.path.dirname(__file__))
        directory = current_dir
        while True:
            if os.path.exists(os.path.join(directory, '.git')):
                return directory
            if directory == os.path.dirname(directory):
                raise ValueError(f'Path does not exist, current dir: {current_dir}')
            directory = os.path.dirname(directory)

    @staticmethod
    def get_process_root_path() -> AnyStr:
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller will create a temporary folder temp and store the path in _MEIPASS
            base_path = sys._MEIPASS
        else:
            base_path = FsUtil.get_project_root_path()
        return base_path

    @staticmethod
    def is_run_from_packaged_exe_file() -> bool:
        return getattr(sys, 'frozen', False)

    @staticmethod
    def get_packaged_exe_file_path() -> str:
        if FsUtil.is_run_from_packaged_exe_file():
            return sys.executable
        return ''

    @staticmethod
    def get_packaged_exe_file_dir() -> AnyStr:
        return os.path.dirname(FsUtil.get_packaged_exe_file_path())

    @staticmethod
    def get_current_dir() -> AnyStr:
        if FsUtil.is_run_from_packaged_exe_file():
            return FsUtil.get_packaged_exe_file_dir()
        else:
            return FsUtil.get_process_root_path()

    @staticmethod
    def get_subdirectories_obj(path: str) -> list[Path]:
        p = Path(path)
        return [subdir for subdir in p.iterdir() if subdir.is_dir()]

    @staticmethod
    def get_subdirectory_names(path: str) -> list[str]:
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
    def search_files_in_dir(directory: str, target_filename: str) -> list[str]:
        matches = []
        # os.walk 递归地遍历目录树
        for root, dirs, files in os.walk(directory):
            # 检查每个文件是否匹配目标文件名
            if target_filename in files:
                # 构建文件的绝对路径并添加到结果列表
                matches.append(os.path.join(root, target_filename))
        return matches

    @staticmethod
    def list_file_paths_with_extensions(dir_path: str, extensions: list[str]) -> list[str]:
        files = []
        for ext in extensions:
            files.extend(glob.glob(os.path.join(dir_path, f'*.{ext}')))
        return files

    @staticmethod
    def list_file_names_with_extensions(dir_path: str, extensions: list[str]) -> list[str]:
        files = FsUtil.list_file_paths_with_extensions(dir_path, extensions)
        return [os.path.basename(file) for file in files]

    @staticmethod
    def get_file_extension(file: str):
        _, file_extension = os.path.splitext(file)
        return file_extension

    @staticmethod
    def resource_find_oldest_file_in_dir(dir_path: str, file_name: str) -> str:
        oldest_file_path: str = ''
        oldest_file_time: float = float('inf')

        # Recursively traverse directories
        for sub_dir_path, _, filenames in os.walk(dir_path):
            if file_name in filenames:
                file_path = os.path.join(sub_dir_path, file_name)
                file_time = os.path.getmtime(file_path)

                # Update the file with the earliest modification time
                if file_time < oldest_file_time:
                    oldest_file_time = file_time
                    oldest_file_path = file_path

        return oldest_file_path
