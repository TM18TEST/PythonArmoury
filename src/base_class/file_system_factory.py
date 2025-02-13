#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File System Factory Class.
"""
from base_class.file_system import FileSystemAdapter
from base_class.file_system_local import FileSystemLocal
from base_class.file_system_smb import FileSystemSmb
from utils.log_ins import LogUtil

logger = LogUtil.get_logger()


class FileSystemFactory:
    _protocols = {
        "file": FileSystemLocal,
        "smb": FileSystemSmb,
        "ftp": None
    }

    @classmethod
    def register_protocol(cls, protocol: str, adapter_class) -> None:
        cls._protocols[protocol] = adapter_class

    @classmethod
    def create(cls, protocol: str, **kwargs) -> FileSystemAdapter:
        adapter_class = cls._protocols.get(protocol)
        if not adapter_class:
            raise ValueError(f"Unsupported protocol: {protocol}")
        return adapter_class(**kwargs)
