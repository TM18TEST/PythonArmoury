#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""
import re
import subprocess
import os

from utils.base_util import BaseUtil


class PackageUtil:
    VER_NUM = '0.0.1'
    VER_STAGE = 'Alpha'

    @staticmethod
    def get_project_root_path() -> str:
        return BaseUtil.get_project_root_path()

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
    def cleanup() -> None:
        print("Starting cleaning some remains, please wait...")
        prj_root_dir = PackageUtil.get_project_root_path()
        clean_script = os.path.join(prj_root_dir, "scripts", "clean.py")
        PackageUtil.run_command("python {}".format(clean_script))

    @staticmethod
    def construct_version_info() -> str:
        commit_time = PackageUtil.get_git_last_commit_time()
        short_commit_id = PackageUtil.get_git_last_commit_id()[:8]
        version = "{}_{}_{}_{}".format(PackageUtil.VER_NUM,
                                       PackageUtil.VER_STAGE,
                                       commit_time,
                                       short_commit_id)
        return version

    @staticmethod
    def overwrite_version_info_in_py_config(version: str) -> None:
        # Open the file and read its content
        file_path = os.path.join(PackageUtil.get_project_root_path(), "src", "config", "project_config.py")
        with open(file_path, 'r', encoding='utf-8') as file:
            old_content = file.read()

        # Replace the version
        pattern = r'(APP_VERSION\s*=\s*")([^"]*)(")'
        replacement = r'APP_VERSION = "{}"'.format(version)
        new_content = re.sub(pattern, replacement, old_content)

        # Update the version to file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

    @staticmethod
    def overwrite_version_info_in_rc(version: str) -> None:
        # Open the file and read its content
        file_path = os.path.join(PackageUtil.get_project_root_path(), "scripts", "version.rc")
        with open(file_path, 'r', encoding='utf-8') as file:
            old_content = file.read()

        # Replace the version
        pattern = r"(StringStruct\(u'ProductVersion',\s*u')(.*?)(?='\))"
        replacement = rf"StringStruct(u'ProductVersion', u'{version}"
        new_content = re.sub(pattern, replacement, old_content)

        # Update the version to file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)

    @staticmethod
    def overwrite_version_info(version: str) -> None:
        PackageUtil.overwrite_version_info_in_py_config(version)
        PackageUtil.overwrite_version_info_in_rc(version)
        print("Overwrite the version information success: {}.".format(version))

    @staticmethod
    def run_pyinstaller() -> None:
        print("Starting packaging the program, please wait...")
        cmd = ("pyinstaller " +
               "--version-file=scripts/version.rc " +
               "--add-data=\"resource/images/icon.ico;resource/images\" " +
               "-i=\"resource/images/icon.ico\" " +
               "-Fw src/main.py " +
               "-n \"Python_Armoury\"")
        PackageUtil.run_command(cmd)


if __name__ == "__main__":
    os.chdir(PackageUtil.get_project_root_path())
    PackageUtil.cleanup()

    # Overwrite the version information
    new_version_info = PackageUtil.construct_version_info()
    PackageUtil.overwrite_version_info(new_version_info)

    PackageUtil.run_pyinstaller()

    # Restore the version information
    PackageUtil.overwrite_version_info("")
