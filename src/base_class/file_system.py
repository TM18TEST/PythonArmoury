#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Abstract Base Class.
"""
import dataclasses
from abc import ABC, abstractmethod
from typing import BinaryIO


class FsObjType(enumerate):
    UNKNOWN = 0
    FILE = 1
    DIR = 2
    ALL = 3


class PathType(enumerate):
    UNKNOWN = 0
    ABSOLUTE = 1
    RELATIVE = 2


@dataclasses.dataclass
class FsObjAttr:
    access_time: float
    modify_time: float
    create_time: float


class FileSystemAdapter(ABC):
    @abstractmethod
    def connect(self, retries: int = 100, retry_interval_sec: float = 0.5):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def is_exist(self, path: str) -> bool:
        pass

    @abstractmethod
    def is_file(self, path: str) -> bool:
        pass

    @abstractmethod
    def is_dir(self, path: str) -> bool:
        pass

    @abstractmethod
    def list_dir(self, path: str, obj_type: FsObjType = FsObjType.ALL) -> list[str]:
        pass

    @abstractmethod
    def read_file(self, remote_path: str, **kwargs) -> BinaryIO:
        pass

    @abstractmethod
    def write_file(self, data: BinaryIO, remote_path: str, **kwargs):
        pass

    @abstractmethod
    def get_attr(self, path: str) -> FsObjAttr:
        pass

    @abstractmethod
    def set_attr(self, path: str, attr: FsObjAttr) -> None:
        pass

    @abstractmethod
    def mk_file(self, path: str, exist_ok: bool = False) -> None:
        pass

    @abstractmethod
    def rm_file(self, path: str) -> None:
        pass

    @abstractmethod
    def mkdir(self, path: str, exist_ok: bool = False) -> None:
        pass

    @abstractmethod
    def rmdir(self, path: str) -> None:
        pass
