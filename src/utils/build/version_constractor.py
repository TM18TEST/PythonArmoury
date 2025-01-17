#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Version File Constructor.
"""
import os
import shutil
import sys
from dataclasses import dataclass

from utils.fs.fs_util import FsUtil


@dataclass
class VersionStruct:
    file_desc: str = None
    file_ver: str = None
    inter_name: str = None
    legal_copyright: str = None
    original_filename: str = None
    product_name: str = None
    product_ver: str = None
    language: str = None
    legal_trademarks: str = None


class VerFileConstructor:
    """
    Json Profile Parser Base Class.
    """
    VERSION_FMT: str = """VSVersionInfo(
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
            StringTable(u'040904B0', [
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

    def __init__(self, file_path: str, ver_struct: VersionStruct):
        # Declare some variables of current instance
        self._file_path: str = file_path
        self._ver_struct: VersionStruct = ver_struct

    def _fill_ver_info(self) -> None:
        if self._ver_struct.file_desc is None:
            raise ValueError("Null file description.")
        if self._ver_struct.file_ver is None:
            self._ver_struct.file_ver = "1.0.0.0"
        if self._ver_struct.inter_name is None:
            self._ver_struct.inter_name = self._ver_struct.file_desc
        if self._ver_struct.legal_copyright is None:
            self._ver_struct.legal_copyright = "© Xiamen Tianma Display Technology. All rights reserved."
        if self._ver_struct.original_filename is None:
            self._ver_struct.original_filename = self._ver_struct.file_desc.replace(" ", "_") + ".exe"
        if self._ver_struct.product_name is None:
            self._ver_struct.product_name = self._ver_struct.file_desc
        if self._ver_struct.product_ver is None:
            raise ValueError("Null product version.")
        if self._ver_struct.language is None:
            self._ver_struct.language = "Language Neutral"
        if self._ver_struct.legal_trademarks is None:
            self._ver_struct.legal_trademarks = "Xiamen Tianma Display Technology Co., Ltd."

    def run(self) -> None:
        self._fill_ver_info()

        file_content: str = self.VERSION_FMT.format(
            self._ver_struct.file_desc,
            self._ver_struct.file_ver,
            self._ver_struct.inter_name,
            self._ver_struct.legal_copyright,
            self._ver_struct.original_filename,
            self._ver_struct.product_name,
            self._ver_struct.product_ver,
            self._ver_struct.language,
            self._ver_struct.legal_trademarks
        )
        with open(self._file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)

    def clear(self):
        if os.path.exists(self._file_path):
            shutil.rmtree(self._file_path)


if __name__ == "__main__":
    _file_path: str = os.path.join(FsUtil.get_current_dir(), "version.rc")
    _ver: VersionStruct = VersionStruct(
        file_desc="TM18 VTech Rep Recipe Archiver",
        product_ver="0.0.3_Alpha"
    )
    runner = VerFileConstructor(_file_path, _ver)
    runner.run()
    sys.exit(0)
