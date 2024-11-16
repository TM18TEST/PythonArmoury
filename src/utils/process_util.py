#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Process Utility Class Source Code.
"""
import ctypes
import os
import _winapi

import psutil


class ProcessUtil:
    # Windows priority constant definition
    WIN_NORMAL_PRIORITY_CLASS = 0x00000020
    WIN_IDLE_PRIORITY_CLASS = 0x00000040
    WIN_HIGH_PRIORITY_CLASS = 0x00000080

    @staticmethod
    def get_current_process_priority() -> int:
        p = psutil.Process(os.getpid())
        return p.nice()

    @staticmethod
    def set_current_process_priority(priority: int) -> None:
        p = psutil.Process(os.getpid())
        p.nice(priority)

    @staticmethod
    def set_current_process_idle_priority() -> None:
        ProcessUtil.set_current_process_priority(psutil.IDLE_PRIORITY_CLASS)

    @staticmethod
    def check_current_process_name(expected_name: str) -> None:
        actual_name = psutil.Process(os.getpid()).name()
        if actual_name != expected_name:
            raise RuntimeError(f"Invalid process name: {actual_name}, expected: {expected_name}.")

    @staticmethod
    def get_process_list_by_name(expected_name: str) -> list[psutil.Process]:
        proc_list: list[psutil.Process] = []
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.name() == expected_name:
                proc_list.append(proc)
        return proc_list

    @staticmethod
    def check_process_num() -> None:
        if len(ProcessUtil.get_process_list_by_name(psutil.Process(os.getpid()).name())) > 1:
            raise RuntimeError(f"There is already a process instance of the same program running.")

    @staticmethod
    def avoid_multi_proc_of_same_prog_by_win_mutex(identifier: str) -> None:
        # 互斥体名称
        mutex_name = "Global\\Mutex." + identifier

        # Windows API 函数
        kernel32 = ctypes.WinDLL('kernel32')
        mutex = kernel32.CreateMutexW(None, True, mutex_name)
        if not mutex:
            raise RuntimeError(f"Failed to create the mutex: {mutex_name}, error: {kernel32.GetLastError()}.")

        # 检查互斥体是否已经存在
        if kernel32.GetLastError() == _winapi.ERROR_ALREADY_EXISTS:
            kernel32.CloseHandle(mutex)
            raise RuntimeError(f"The mutex has already been created: {mutex_name}.")

    @staticmethod
    def acquire_windows_global_mutex(identifier: str) -> object | None:
        # 互斥体名称
        mutex_name = "Global\\Mutex." + identifier

        # Windows API 函数
        kernel32 = ctypes.WinDLL('kernel32')
        mutex = kernel32.CreateMutexW(None, True, mutex_name)
        if not mutex:
            raise RuntimeError(f"Failed to create the mutex: {mutex_name}, error: {kernel32.GetLastError()}.")

        # 检查互斥体是否已经存在
        if kernel32.GetLastError() == _winapi.ERROR_ALREADY_EXISTS:
            kernel32.CloseHandle(mutex)
            raise RuntimeError(f"The mutex has already been created: {mutex_name}.")
        return kernel32, mutex

    @staticmethod
    def release_windows_global_mutex(ctx: object) -> None:
        # Windows API 函数
        kernel32, mutex = ctx
        kernel32.ReleaseMutex(mutex)
        kernel32.CloseHandle(mutex)

    @staticmethod
    def is_process_running(process_name: str) -> bool:
        return any(process.name() == process_name for process in psutil.process_iter(['name']))

    @staticmethod
    def is_excel_process_running() -> bool:
        return ProcessUtil.is_process_running('EXCEL.EXE')
