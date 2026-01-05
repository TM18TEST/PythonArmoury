#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Utility Class Source Code.
"""
import ctypes
import glob
import hashlib
import os
import shutil
import time
from pathlib import Path
import tempfile
from typing import AnyStr

from utils.framework_util import FrameworkUtil
from utils.os_util import OsUtil
from utils.pyinstaller_util import PyInstallerUtil


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
        if PyInstallerUtil.is_run_in_pyinstaller_bundle():
            return PyInstallerUtil.get_resource_root_dir()
        else:
            return FsUtil.get_project_root_path()

    @staticmethod
    def get_current_dir() -> AnyStr:
        if PyInstallerUtil.is_run_in_pyinstaller_bundle():
            return PyInstallerUtil.get_packaged_exe_file_dir()
        else:
            return FsUtil.get_project_root_path()

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
    def is_empty_dir(path: str | Path):
        path_str: str = path
        if isinstance(path, Path):
            path_str = str(path)
        elif isinstance(path, str):
            path = Path(path_str)
        else:
            raise TypeError(f"Invalid type of path: {type(path)}")
        if not os.path.exists(path_str):
            return False
        if not os.path.isdir(path_str):
            return False
        return not any(path.iterdir())

    @staticmethod
    def is_dir_exist_and_not_empty(path: str) -> bool:
        if os.path.exists(path) and os.path.isdir(path):
            return not FsUtil.is_empty_dir(path)
        return False

    @staticmethod
    def _force_remove_in_windows(path: str, not_exist_ok: bool = False) -> None:
        if os.path.isfile(path):
            os.system(f'del /F /Q "{path}"')
        elif os.path.isdir(path):
            os.system(f'rmdir /S /Q "{path}"')
        else:
            if not_exist_ok:
                return
            raise FileNotFoundError(f"Path not found: {path}")

    @staticmethod
    def _force_remove_in_linux(path: str, not_exist_ok: bool = False) -> None:
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
                if not_exist_ok:
                    return
                raise FileNotFoundError("The path({}) is not exist.".format(path))
            else:
                raise TypeError("The path({}) neither a file nor a directory.".format(path))

    @staticmethod
    def force_remove(path: str | Path, not_exist_ok: bool = False) -> None:
        """
        Remove specified file, empty directory or non-empty directory.

        :param path: The path of object to be removed.
        :param not_exist_ok: Discard errors if the path is not exist.
        """
        if isinstance(path, Path):
            path = str(path)
        if OsUtil.is_windows():
            return FsUtil._force_remove_in_windows(path, not_exist_ok)
        elif OsUtil.is_linux() or OsUtil.is_mac():
            return FsUtil._force_remove_in_linux(path, not_exist_ok)
        else:
            raise OSError(f"Unknown OS type")

    @staticmethod
    def remove_path(path: str | Path, not_exist_ok: bool = False) -> None:
        return FsUtil.force_remove(path, not_exist_ok)

    @staticmethod
    def remake_dirs(path: str) -> None:
        FsUtil.force_remove(path, not_exist_ok=True)
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

    @staticmethod
    def set_file_times(file_path, create_timestamp: float, last_modified_timestamp: float,
                       last_access_timestamp: float):
        os.utime(file_path, (last_access_timestamp, last_modified_timestamp))
        if os.name == 'nt':  # Windows
            file_time = create_timestamp
            win_time = int(file_time * 10 ** 7 + 116444736000000000)
            handle = ctypes.windll.kernel32.CreateFileW(
                file_path, 256, 0, None, 3, 128, None
            )
            if handle == -1:
                raise OSError("Unable to open file set creation time")
            c_time = ctypes.c_longlong(win_time)
            ctypes.windll.kernel32.SetFileTime(handle, ctypes.byref(c_time), None, None)
            ctypes.windll.kernel32.CloseHandle(handle)
        else:
            raise RuntimeError(f'Unsupported OS type: {os.name}')

    @staticmethod
    def create_dirs(base_path: str, *dir_paths: str):
        """
        创建多个目录（支持多个路径参数）

        :param base_path: 根目录路径
        :param dir_paths: 任意数量的目录路径参数
        """
        for dir_path in dir_paths:
            full_path = os.path.join(base_path, dir_path)
            os.makedirs(full_path, exist_ok=True)

    @staticmethod
    def create_files(base_path: str, *file_paths: str):
        """
        创建多个文件，支持路径分隔符创建子目录

        :param base_path: 根目录路径
        :param file_paths: 文件路径列表，包含子目录
        """
        for file_path in file_paths:
            full_path = os.path.join(base_path, file_path)
            dir_path = os.path.dirname(full_path)
            os.makedirs(dir_path, exist_ok=True)
            with open(full_path, 'w'):
                pass

    @staticmethod
    def is_exist(path: str, retries: int = 30, delay: float = 0.05):
        """ Combine Pathlib and retry mechanisms to improve the reliability of SMB access """
        for _ in range(retries):
            try:
                p = Path(path)
                return p.exists()
            except Exception as e:
                print(f"Warning: Failed to check {path}, retrying... ({e})")
                time.sleep(delay)
        raise RuntimeError(f"Failed to check {path} in {retries} times, interval: {delay} sec")

    @staticmethod
    def is_dir(path: str, retries: int = 30, delay: float = 0.05):
        """ Combine Pathlib and retry mechanisms to improve the reliability of SMB access """
        for _ in range(retries):
            try:
                p = Path(path)
                if p.exists() and p.is_dir():
                    return True
                else:
                    return False
            except Exception as e:
                print(f"Warning: Failed to check {path}, retrying... ({e})")
                time.sleep(delay)
        raise RuntimeError(f"Failed to check {path} in {retries} times, interval: {delay} sec")

    @staticmethod
    def rename_file(src: str, dst: str):
        FrameworkUtil.call_with_retry(shutil.copy2, src, dst,
                                      exc_list=[FileNotFoundError, PermissionError, OSError])
        FrameworkUtil.call_with_retry(os.remove, src,
                                      exc_list=[FileNotFoundError, PermissionError, OSError])

    @staticmethod
    def rmtree(path: str):
        if not FrameworkUtil.call_with_retry(os.path.exists, path,
                                             exc_list=[FileNotFoundError, PermissionError, OSError]):
            return
        FrameworkUtil.call_with_retry(shutil.rmtree, path,
                                      exc_list=[FileNotFoundError, PermissionError, OSError])

    @staticmethod
    def copytree(src, dst):
        if FrameworkUtil.call_with_retry(os.path.exists, dst,
                                         exc_list=[FileNotFoundError, PermissionError, OSError]):
            FsUtil.rmtree(dst)
        FrameworkUtil.call_with_retry(shutil.copytree, src, dst,
                                      exc_list=[FileNotFoundError, PermissionError, OSError])