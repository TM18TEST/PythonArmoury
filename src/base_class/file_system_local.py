#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Local File System Adapter Class.
"""
import os
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from base_class.file_system import FileSystemAdapter, FsObjType, FsObjAttr
from utils.fs.fs_util import FsUtil
from utils.log_ins import LogUtil

logger = LogUtil.get_logger()


class FileSystemLocal(FileSystemAdapter):
    def connect(self, retries: int = 100, retry_interval_sec: float = 0.5):
        pass

    def disconnect(self):
        pass

    def is_exist(self, path: str) -> bool:
        return os.path.exists(path)

    def is_file(self, path: str) -> bool:
        return os.path.isfile(path)

    def is_dir(self, path: str) -> bool:
        return os.path.isdir(path)

    def list_dir(self, path: str, obj_type: FsObjType = FsObjType.ALL) -> list[str]:
        p = Path(path)
        if obj_type is FsObjType.DIR:
            return [subdir.name for subdir in p.iterdir() if subdir.is_dir()]
        elif obj_type is FsObjType.FILE:
            return [subdir.name for subdir in p.iterdir() if subdir.is_file()]
        elif obj_type is FsObjType.ALL:
            return [subdir.name for subdir in p.iterdir()]
        raise ValueError(f"Unsupported object type: {obj_type}")

    def read_file(self, path: str, **kwargs) -> BinaryIO:
        with open(path, "rb") as f:
            return BytesIO(f.read())

    def write_file(self, data: BinaryIO, path: str, **kwargs):
        with open(path, "wb") as f:
            f.write(data.read())

    def get_attr(self, path: str) -> FsObjAttr:
        return FsObjAttr(access_time=os.path.getatime(path), create_time=os.path.getctime(path),
            modify_time=os.path.getmtime(path))

    def set_attr(self, path: str, attr: FsObjAttr) -> None:
        FsUtil.set_file_times(path, attr.create_time, attr.access_time, attr.modify_time)

    def mk_file(self, path: str, exist_ok: bool = False):
        if exist_ok is False and os.path.isfile(path):
            raise FileExistsError(f"File already exists: {path}")
        with open(path, 'w') as f:
            f.write("")

    def rm_file(self, path: str) -> None:
        os.remove(path)

    def mkdir(self, path: str, exist_ok: bool = False) -> None:
        os.makedirs(path, exist_ok)

    def rmdir(self, path: str) -> None:
        os.rmdir(path)
