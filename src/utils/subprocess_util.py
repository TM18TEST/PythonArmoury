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
            raise RuntimeError(f"Command '{cmd}' failed with exit code {result.returncode}, stderr: {result.stderr}")

    @staticmethod
    def run_cmd_without_window(cmd: str | list[str]) -> subprocess.CompletedProcess:
        # shell=True 禁用命令解释器
        # capture_output=True 捕获输出
        # text=True 将输出转换为字符串
        # creationflags=subprocess.CREATE_NO_WINDOW 在Windows上防止弹出新的控制台窗口
        p = subprocess.run(cmd, shell=True, capture_output=True,
                           text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return p

    @staticmethod
    def popen_stdout(cmd: str | list[str]) -> int:
        p = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr, text=True)
        p.wait()
        return p.returncode


if __name__ == "__main__":
    sys.exit(0)
