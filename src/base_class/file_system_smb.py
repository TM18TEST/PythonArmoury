#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: SMB File System Adapter Class.
"""
import time
from io import BytesIO
from typing import BinaryIO

import smbclient
import smbclient.shutil
import smbprotocol.exceptions

from base_class.file_system import FileSystemAdapter, FsObjType, FsObjAttr
from utils.base_util import BaseUtil
from utils.fs.fs_util import FsUtil
from utils.log_ins import LogUtil

logger = LogUtil.get_logger()


class FileSystemSmb(FileSystemAdapter):
    def __init__(self, server: str, username: str, password: str):
        if BaseUtil.is_empty(server):
            raise ValueError(f"Null input server address")
        self._server: str = server
        self._username: str = username
        self._password: str = password
        self._session = None

    def _gen_absolute_path(self, absolute_path: str = None, relative_path: str = None) -> str:
        if absolute_path is None and relative_path is None:
            raise ValueError(f"None absolute & relative path")
        if absolute_path is not None:
            return absolute_path
        return rf"\\{self._server}\{relative_path}"

    def connect(self, retries: int = 100, retry_interval_sec: float = 0.5):
        for i in range(retries):
            try:
                self._session = smbclient.register_session(server=self._server,
                                                           username=self._username,
                                                           password=self._password)
                logger.debug("Connected to SMB server success, server: %s, username: %s.", self._server, self._username)
                return
            except Exception as e:
                logger.warning("Failed to register session: %d/%d, server: %s, exception: %s, retrying...",
                               i + 1, retries, self._server, e)
                time.sleep(retry_interval_sec)
                continue
        logger.error("Failed to register session in %d times, server: %s, username: %s, interval %.2f sec.",
                     retries, self._server, self._username, retry_interval_sec)
        raise RuntimeError(f"Failed to register session to SMB server: {self._server}, username: {self._username}")

    def disconnect(self):
        if self._session is not None:
            smbclient.delete_session(server=self._server)
            self._session = None
            logger.debug("Disconnect from SMB connection success, server: %s, user: %s.", self._server, self._username)

    def is_exist(self, path: str) -> bool:
        return smbclient.path.exists(path)

    def is_file(self, path: str) -> bool:
        return smbclient.path.isfile(path)

    def is_dir(self, path: str) -> bool:
        return smbclient.path.isdir(path)

    def list_dir(self, absolute_path: str = None, relative_path: str = None,
                 obj_type: FsObjType = FsObjType.ALL) -> list[str]:
        absolute_path: str = self._gen_absolute_path(absolute_path, relative_path)
        if obj_type is FsObjType.DIR:
            return [entry.name for entry in smbclient.scandir(absolute_path) if entry.is_dir()]
        elif obj_type is FsObjType.FILE:
            return [entry.name for entry in smbclient.scandir(absolute_path) if entry.is_file()]
        elif obj_type is FsObjType.ALL:
            return [entry.name for entry in smbclient.scandir(absolute_path)]
        raise ValueError(f"Unsupported object type: {obj_type}")

    def read_file(self, relative_path: str, **kwargs) -> BinaryIO:
        with smbclient.open_file(self._gen_absolute_path(relative_path), "rb") as f:
            return BytesIO(f.read())

    def write_file(self, data: BinaryIO, relative_path: str, **kwargs):
        with smbclient.open_file(self._gen_absolute_path(relative_path), "wb") as f:
            f.write(data.read())

    def get_attr(self, relative_path: str) -> FsObjAttr:
        absolute_path: str = self._gen_absolute_path(relative_path)
        return FsObjAttr(access_time=smbclient.path.getatime(absolute_path),
                         create_time=smbclient.path.getctime(absolute_path),
                         modify_time=smbclient.path.getmtime(absolute_path))

    def set_attr(self, relative_path: str, attr: FsObjAttr) -> None:
        FsUtil.set_file_times(self._gen_absolute_path(relative_path), attr.create_time, attr.access_time,
                              attr.modify_time)

    def mk_file(self, relative_path: str, exist_ok: bool = False):
        absolute_path: str = self._gen_absolute_path(relative_path)
        if exist_ok is False and smbclient.path.isfile(absolute_path):
            raise FileExistsError(f"File already exists: {relative_path}")
        with smbclient.open_file(absolute_path, 'w') as f:
            f.write("")

    def rm_file(self, relative_path: str) -> None:
        smbclient.shutil.remove(self._gen_absolute_path(relative_path))

    def mkdir(self, relative_path: str, exist_ok: bool = False) -> None:
        smbclient.shutil.makedirs(self._gen_absolute_path(relative_path), exist_ok)

    def rmdir(self, relative_path: str) -> None:
        smbclient.shutil.rmdir(self._gen_absolute_path(relative_path))

    @staticmethod
    def copy_file_with_metadata(src: str, dst: str, retries: int = 100, retry_interval_sec: float = 0.5) -> None:
        for i in range(retries):
            try:
                smbclient.shutil.copy2(src, dst)
                return
            except smbprotocol.exceptions.SMBOSError as e:
                logger.warning("Failed to copy file: %d/%d, src path: %s, exception: %s, retrying...",
                               i + 1, retries, src, e)
                time.sleep(retry_interval_sec)
                continue
        logger.error("Failed to copy file in %d times, src path: %s, interval %.2f sec.",
                     retries, src, retry_interval_sec)
        raise FileNotFoundError(f"Failed to copy file from {src} to {dst}")

    @staticmethod
    def copystat(src: str, dst: str, retries: int = 100, retry_interval_sec: float = 0.5) -> None:
        for i in range(retries):
            try:
                smbclient.shutil.copystat(src, dst)
                return
            except smbprotocol.exceptions.SMBOSError as e:
                logger.warning("Failed to copy stat: %d/%d, src path: %s, exception: %s, retrying...",
                               i + 1, retries, src, e)
                time.sleep(retry_interval_sec)
                continue
        logger.error("Failed to copy stat in %d times, src path: %s, interval %.2f sec.",
                     retries, src, retry_interval_sec)
        raise FileNotFoundError(f"Failed to copy stat from {src} to {dst}")
