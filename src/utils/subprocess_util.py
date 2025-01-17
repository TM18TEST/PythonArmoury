#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Subprocess Utility Class.
"""
import subprocess
import sys


class SubprocessUtil:
    @staticmethod
    def run_cmd(cmd: str) -> None:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        print(result.stdout)
        print(result.stderr)
        if result.returncode != 0:
            raise RuntimeError(f"Command '{cmd}' failed with exit code {result.returncode}")

    @staticmethod
    def run_cmd_list(cmd: list[str]) -> None:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        print(result.stdout)
        print(result.stderr)
        if result.returncode != 0:
            raise RuntimeError(f"Command '{cmd}' failed with exit code {result.returncode}")


if __name__ == "__main__":
    sys.exit(0)
