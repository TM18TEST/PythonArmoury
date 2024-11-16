#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: String Utility Class Source Code.
"""


class StrUtil:
    def __init__(self):
        pass

    @staticmethod
    def is_valid_base_number(s: str, base: int) -> bool:
        prefixes = {2: '0b', 8: '0o', 16: '0x'}
        valid_chars = {
            2: '01',
            8: '01234567',
            10: '0123456789',
            16: '0123456789aAbBcCdDeEfF'
        }

        # Check and remove prefixes
        if base in prefixes and s.startswith((prefixes[base], prefixes[base].upper())):
            s = s[2:]

        # Check if the character is within the valid range
        return all(c in valid_chars[base] for c in s) if s else False
