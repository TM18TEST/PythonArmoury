#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""
import re
import subprocess
import os

from utils.fs_util import FsUtil
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
        file_path = os.path.join(FsUtil.get_project_root_path(), "src", "config", "project_config.py")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        key_value_list: list[(str, str)] = [
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
        file_path = os.path.join(FsUtil.get_project_root_path(), "scripts", "version.rc")
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
    def run_pyinstaller(app_file_short_name: str, add_paths: list[(str, str)], one_file: bool) -> None:
        add_data_str: str = ""
        for add_src, add_dst in add_paths:
            add_data_str += "--add-data=\"{};{}\" ".format(add_src, add_dst)

        print("Starting packaging the program, please wait...")
        cmd = ("pyinstaller " +
               "--version-file=scripts/version.rc " +
               add_data_str +
               "-i=\"resource/images/icon.ico\" " +
               "-{}w src/main.py ".format("F" if one_file else "") +
               "-n \"{}\"".format(app_file_short_name))
        PackageUtil.run_command(cmd)

    @staticmethod
    def pack_app(prj_root_path: str, ver_config: VerConfig, add_paths: list[(str, str)],
                 one_file: bool, ui_files: (str, str) = None) -> None:
        os.chdir(prj_root_path)

        # Update the version information
        PackageUtil.overwrite_version_info(ver_config)

        if ui_files:
            # Generate the Python code from ui file
            PackageUtil.overwrite_version_info(ver_config)
            cmd = "pyside6-uic resource/ui/mainwindow.ui -o src/front_end/ui/generated/ui_mainwindow.py".format(ui_files[0], ui_files[1])
            cmd = "pyside6-uic {} -o {}".format(ui_files[0], ui_files[1])
            PackageUtil.run_command(cmd)

        PackageUtil.run_pyinstaller(ver_config.app_file_short_name, add_paths, one_file)

        # Restore the version information
        product_version = ver_config.ver_file_info.product_version
        product_version = product_version[:product_version.find('_', product_version.find('_') + 1)]
        ver_config.ver_file_info.product_version = product_version
        PackageUtil.overwrite_version_info(ver_config)


if __name__ == "__main__":
    pass

