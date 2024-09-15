#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: String Utility Class Source Code.
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""


class VerFileData:
    def __init__(self, file_desc: str = '', file_ver: str = '', internal_name: str = '', legal_copyright: str = '',
                 original_name: str = '', product_name: str = '', product_version: str = '', language: str = '',
                 legal_trademarks: str = ''):
        self.file_desc: str = file_desc
        self.file_ver: str = file_ver
        self.internal_name: str = internal_name
        self.legal_copyright: str = legal_copyright
        self.original_name: str = original_name
        self.product_name: str = product_name
        self.product_version: str = product_version
        self.language: str = language
        self.legal_trademarks: str = legal_trademarks

        self.comma_file_ver: str
        self._parse_file_version()

    def _parse_file_version(self) -> None:
        if self.file_ver is None or self.file_ver == '':
            self.comma_file_ver = ''
            return
        if not self.file_ver.replace('.', '').isdigit() or \
                '..' in self.file_ver or \
                self.file_ver.startswith('.') or \
                self.file_ver.endswith('.'):
            raise ValueError(f"Invalid file version: {self.file_ver}")

        self.comma_file_ver = self.file_ver.replace('.', ', ')

    def __str__(self) -> str:
        return "VSVersionInfo(\n\
    ffi=FixedFileInfo(\n\
        filevers=({}),\n\
        mask=0x3f,\n\
        flags=0x0,\n\
        OS=0x40004,\n\
        fileType=0x1,\n\
        subtype=0x0,\n\
        date=(0, 0)\n\
    ),\n\
    kids=[\n\
        StringFileInfo([\n\
            StringTable(u'040904B0', [\n\
                StringStruct(u'FileDescription', u'{}'),\n\
                StringStruct(u'FileVersion', u'{}'),\n\
                StringStruct(u'InternalName', u'{}'),\n\
                StringStruct(u'LegalCopyright', u'{}'),\n\
                StringStruct(u'OriginalFilename', u'{}'),\n\
                StringStruct(u'ProductName', u'{}'),\n\
                StringStruct(u'ProductVersion', u'{}'),\n\
                StringStruct(u'Language', u'{}'),\n\
                StringStruct(u'LegalTrademarks', u'{}')\n\
            ])\n\
        ]),\n\
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])\n\
    ]\n\
)".format(self.comma_file_ver, self.file_desc, self.file_ver, self.internal_name,
          self.legal_copyright, self.original_name, self.product_name, self.product_version,
          self.language, self.legal_trademarks)


if __name__ == "__main__":
    ver_data = VerFileData('TM18 File Compliance Monitor', '1.0.0.0', 'TM18 File Compliance Monitor',
                           '© Xiamen Tianma Display Technology. All rights reserved.',
                           'TM18_File_Compliance_Monitor.exe',
                           'TM18 File Compliance Monitor',
                           '0.1.2',
                           'Language Neutral',
                           'Xiamen Tianma Display Technology Co., Ltd.')
    content = ver_data.__str__()
    print(content)
