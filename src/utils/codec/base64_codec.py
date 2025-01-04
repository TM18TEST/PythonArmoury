#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Base64 Codec Utility Class Source Code.
"""
import base64
import sys


class Base64Codec:
    """ Base64 Codec Utility Class. """
    @staticmethod
    def encode(content: str) -> str:
        return base64.b64encode(content.encode("utf-8")).decode("utf-8")

    @staticmethod
    def decode(content: str) -> str:
        return base64.b64decode(content).decode("utf-8")


if __name__ == "__main__":
    print("The program has been started.")
    text: str = "11111111"
    print(f"{Base64Codec.encode(text)}")
    print("The program is about to exit.")
    sys.exit(0)
