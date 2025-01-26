#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Data Backup Base Class.
"""
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from utils.base_util import BaseUtil
from utils.fs.compress_util import CompressUtil
from utils.fs.fs_util import FsUtil


@dataclass
class DataBackupParam:
    src_path: str
    dst_dir_path: str
    backup_file_name_prefix: str = None
    max_backups_num: int = None
    compress_fmt: str = 'zip'
    compress_level: int = None


class DataBackup:
    """
    Data Backup Base Class.
    """

    def __init__(self, param: DataBackupParam):
        # Declare some variables of current instance
        self._src_path: str = param.src_path
        self._dst_dir_path: str = param.dst_dir_path
        self._backup_file_name_prefix: str = param.backup_file_name_prefix
        self._max_backups_num: Optional[int] = param.max_backups_num
        self._compress_fmt: Optional[str] = param.compress_fmt
        self._compress_level: Optional[int] = param.compress_level

    def check_params(self) -> None:
        if not os.path.exists(self._src_path):
            raise FileNotFoundError(f"Source not exist: {self._src_path}")
        if self._max_backups_num < 0:
            raise ValueError(f"Invalid max backups num: {self._max_backups_num}")

    def pre_backup(self) -> None:
        pass

    def prepare_env(self) -> None:
        os.makedirs(self._dst_dir_path, exist_ok=True)

    def construct_backup_name_prefix(self) -> str:
        """
        Construct the name prefix of new backup.

        Returns:
            str: The constructed backup name prefix.
        """
        if not BaseUtil.is_empty(self._backup_file_name_prefix):
            return self._backup_file_name_prefix
        return os.path.basename(self._src_path) + "_backup_"

    def construct_backup_name(self) -> str:
        """
        Construct the name of new backup.

        Returns:
            str: The constructed backup name.
        """
        return (self.construct_backup_name_prefix() +
                datetime.now().strftime("%Y%m%d_%H%M%S") +
                "." + self._compress_fmt)

    def do_backup(self) -> str:
        """
        Construct the name of new backup.

        Returns:
            str: The path of new backup.
        """
        backup_name: str = self.construct_backup_name()
        backup_path: str = os.path.join(self._dst_dir_path, backup_name)
        CompressUtil.compress(self._src_path, backup_path,
                              fmt=self._compress_fmt, level=self._compress_level)
        return backup_path

    def check_backup(self, path: str) -> None:
        CompressUtil.check_compressed_file(path, self._compress_fmt)

    def list_backups(self) -> list[str]:
        # list backups and its modification time
        prefix: str = self.construct_backup_name_prefix()
        path_times: list[tuple[str, float]] = []
        for entries in os.listdir(self._dst_dir_path):
            if not entries.startswith(prefix):
                continue
            path: str = os.path.join(self._dst_dir_path, entries)
            path_times.append((path, os.path.getmtime(path)))

        # Sort the backups by modification time
        path_times = sorted(path_times, key=lambda x: x[1])
        matches: list[str] = [f[0] for f in path_times]
        return matches

    def rotate(self) -> None:
        if self._max_backups_num is None:
            return
        backups: list[str] = self.list_backups()
        if len(backups) <= self._max_backups_num:
            return
        del_num: int = len(backups) - self._max_backups_num
        for i in range(del_num):
            FsUtil.remove_path(backups[i])

    def post_backup(self) -> None:
        pass

    def run(self) -> str:
        self.check_params()
        self.prepare_env()
        self.pre_backup()
        backup_path: str = self.do_backup()
        self.check_backup(backup_path)
        self.rotate()
        self.post_backup()
        return backup_path
