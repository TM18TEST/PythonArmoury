#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: File Details Class Source Code.
"""
import os.path
import sys
import win32api
from dataclasses import dataclass

from utils.fs.fs_util import FsUtil


@dataclass
class FileDetails:
    file_desc: str = None
    file_ver: str = None
    internal_name: str = None
    legal_copyright: str = None
    original_file_name: str = None
    product_name: str = None
    product_version: str = None
    language: str = None
    legal_trademarks: str = None


class FileDetailsHandler:
    LANGUAGE_ID: str = "040904B0"
    VER_FILE_FMT = """VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(1, 0, 0, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(u'{}', [
                StringStruct(u'FileDescription', u'{}'),
                StringStruct(u'FileVersion', u'{}'),
                StringStruct(u'InternalName', u'{}'),
                StringStruct(u'LegalCopyright', u'{}'),
                StringStruct(u'OriginalFilename', u'{}'),
                StringStruct(u'ProductName', u'{}'),
                StringStruct(u'ProductVersion', u'{}'),
                StringStruct(u'Language', u'{}'),
                StringStruct(u'LegalTrademarks', u'{}')
            ])
        ]),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    ]
)"""

    def __init__(self, file_details: FileDetails, ver_file_path: str):
        self._file_details: FileDetails = file_details
        self._ver_file_path: str = ver_file_path

    def fill_version_data(self):
        if self._file_details.file_desc is None:
            raise ValueError("File description is required.")
        self._file_details.file_ver = self._file_details.file_ver or "1.0.0.0"
        self._file_details.internal_name = self._file_details.internal_name or self._file_details.file_desc
        if self._file_details.legal_copyright is None:
            raise ValueError("Legal copyright is required.")
        self._file_details.product_name = self._file_details.product_name or self._file_details.file_desc
        if self._file_details.product_version is None:
            raise ValueError("Product version is required.")
        self._file_details.language = self._file_details.language or "Language Neutral"
        if self._file_details.legal_trademarks is None:
            raise ValueError("Legal trademarks is required.")

    def format_version_content(self) -> str:
        return self.VER_FILE_FMT.format(
            self.LANGUAGE_ID,
            self._file_details.file_desc,
            self._file_details.file_ver,
            self._file_details.internal_name,
            self._file_details.legal_copyright,
            self._file_details.original_file_name,
            self._file_details.product_name,
            self._file_details.product_version,
            self._file_details.language,
            self._file_details.legal_trademarks
        )

    def write_version_content(self, ver_content: str) -> None:
        with open(self._ver_file_path, "w", encoding="utf-8") as f:
            f.write(ver_content)

    def generate(self) -> None:
        self.fill_version_data()
        content: str = self.format_version_content()
        self.write_version_content(content)

    def clear(self):
        if os.path.exists(self._ver_file_path):
            FsUtil.remove_path(self._ver_file_path)

    @staticmethod
    def get_file_details(file_path: str) -> FileDetails:
        key_prefix: str = f"\\StringFileInfo\\{FileDetailsHandler.LANGUAGE_ID}"
        details = FileDetails(
            file_desc=win32api.GetFileVersionInfo(file_path, f"{key_prefix}\\FileDescription"),
            file_ver=win32api.GetFileVersionInfo(file_path, f"{key_prefix}\\FileVersion"),
            internal_name=win32api.GetFileVersionInfo(file_path, f"{key_prefix}\\InternalName"),
            legal_copyright=win32api.GetFileVersionInfo(file_path, f"{key_prefix}\\LegalCopyright"),
            original_file_name=win32api.GetFileVersionInfo(file_path, f"{key_prefix}\\OriginalFilename"),
            product_name=win32api.GetFileVersionInfo(file_path, f"{key_prefix}\\ProductName"),
            product_version=win32api.GetFileVersionInfo(file_path, f"{key_prefix}\\ProductVersion"),
            language=win32api.GetFileVersionInfo(file_path, f"{key_prefix}\\Language"),
            legal_trademarks=win32api.GetFileVersionInfo(file_path, f"{key_prefix}\\LegalTrademarks")
        )
        return details

    @staticmethod
    def get_file_detailed_version(file_path: str) -> str:
        file_details: FileDetails = FileDetailsHandler.get_file_details(file_path)
        return file_details.product_version


if __name__ == "__main__":
    sys.exit(0)
