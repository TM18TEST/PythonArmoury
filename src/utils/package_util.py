#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""
import re
import subprocess
import os
from typing import List, Tuple

from utils.base_util import BaseUtil
from utils.ver_file_util import VerFileData


class VerConfig:
    def __init__(self, ver_file_info: VerFileData = None, organize_name: str = '', short_app_name: str = '',
                 app_auther: str = '', company_name: str = '', app_file_short_name: str = ''):
        self.ver_file_info: VerFileData = VerFileData()
        if ver_file_info:
            self.ver_file_info = ver_file_info

        self.organize_name: str = organize_name
        self.short_app_name: str = short_app_name
        self.app_auther: str = app_auther
        self.company_name: str = company_name
        self.app_file_short_name: str = app_file_short_name


class PackageUtil:
    @staticmethod
    def run_command(command: str) -> None:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        print(result.stdout)
        print(result.stderr)
        if result.returncode != 0:
            raise RuntimeError(f"Command '{command}' failed with exit code {result.returncode}")

    @staticmethod
    def get_git_last_commit_id() -> str:
        """Get the latest Git commit ID"""
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')

    @staticmethod
    def get_git_last_commit_date() -> str:
        result = subprocess.run(['git', 'log', '-1', '--format=%cd', '--date=short'],
                                stdout=subprocess.PIPE, text=True)
        return result.stdout.strip()

    @staticmethod
    def get_git_last_commit_time():
        result = subprocess.run(['git', 'log', '-1', '--format=%cd', '--date=format:%Y%m%d%H%M%S'],
                                stdout=subprocess.PIPE, text=True)
        return result.stdout.strip()

    @staticmethod
    def construct_version_info(ver_num: str, ver_stage: str) -> str:
        commit_time = PackageUtil.get_git_last_commit_time()
        short_commit_id = PackageUtil.get_git_last_commit_id()[:8]
        version = "{}_{}_{}_{}".format(ver_num, ver_stage, commit_time, short_commit_id)
        return version

    @staticmethod
    def overwrite_version_info_in_py_config(ver_config: VerConfig) -> None:
        # Open the file and read its content
        file_path = os.path.join(BaseUtil.get_project_root_path(), "src", "config", "project_config.py")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        key_value_list: List[Tuple[str, str]] = [
            ('ORGANIZE_NAME', ver_config.organize_name),
            ('SHORT_APP_NAME', ver_config.short_app_name),
            ('APP_AUTHOR', ver_config.app_auther),
            ('APP_VERSION', ver_config.ver_file_info.product_version),
            ('COMPANY_NAME', ver_config.company_name),
        ]
        for key, value in key_value_list:
            # Replace the value for specified key
            pattern = r'({}\s*=\s*")([^"]*)(")'.format(key)
            replacement = r'{} = "{}"'.format(key, value)
            content = re.sub(pattern, replacement, content)

        # Update the version to file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def overwrite_version_info_in_rc(ver_config: VerConfig) -> None:
        # Update the version to file
        file_path = os.path.join(BaseUtil.get_project_root_path(), "scripts", "version.rc")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(ver_config.ver_file_info.__str__())

    @staticmethod
    def overwrite_version_info(ver_config: VerConfig = None) -> None:
        if ver_config is None:
            ver_config = VerConfig()
        PackageUtil.overwrite_version_info_in_py_config(ver_config)
        PackageUtil.overwrite_version_info_in_rc(ver_config)
        print("Overwrite the version information success.")

    @staticmethod
    def run_pyinstaller(app_file_short_name: str) -> None:
        print("Starting packaging the program, please wait...")
        cmd = ("pyinstaller " +
               "--version-file=scripts/version.rc " +
               "--add-data=\"resource/images/icon.ico;resource/images\" " +
               "-i=\"resource/images/icon.ico\" " +
               "-Fw src/main.py " +
               "-n \"{}\"".format(app_file_short_name))
        PackageUtil.run_command(cmd)

    @staticmethod
    def pack_app(prj_root_path: str, ver_config: VerConfig) -> None:
        os.chdir(prj_root_path)

        # Update the version information
        PackageUtil.overwrite_version_info(ver_config)

        PackageUtil.run_pyinstaller(ver_config.app_file_short_name)

        # Restore the version information
        PackageUtil.overwrite_version_info(None)


if __name__ == "__main__":
    pass

