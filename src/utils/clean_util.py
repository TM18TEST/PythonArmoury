#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import os
from pathlib import Path

from utils.fs_util import FsUtil


class CleanUtil:
    @staticmethod
    def clean_dirs(root_path: str, dir_name_list: list[str]) -> None:
        for entry in dir_name_list:
            full_path = os.path.join(root_path, entry)
            if os.path.isdir(full_path):
                print(f"Deleting directory: {full_path}")
                shutil.rmtree(full_path)

    @staticmethod
    def resource_clean_dir_by_name(root_path: str, dir_name_list: list[str], del_dir_name: str) -> None:
        for dir_name in dir_name_list:
            path_obj = Path(os.path.join(root_path, dir_name))
            for path in path_obj.rglob(del_dir_name):
                if path.is_dir():
                    print(f"Deleting directory: {path}")
                    shutil.rmtree(path)


if __name__ == "__main__":
    CleanUtil.clean_dirs(FsUtil.get_project_root_path(), ["build", "dist"])
    CleanUtil.resource_clean_dir_by_name(FsUtil.get_project_root_path(),
                                         ['src', 'tests', 'submodules'], '__pycache__')
