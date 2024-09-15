#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import shutil
import os
from pathlib import Path
from typing import List

from utils.base_util import BaseUtil


class CleanUtil:
    @staticmethod
    def clean_dirs(root_path: str, dir_name_list: List[str]) -> None:
        for entry in dir_name_list:
            full_path = os.path.join(root_path, entry)
            if os.path.isdir(full_path):
                print(f"Deleting directory: {full_path}")
                shutil.rmtree(full_path)

    @staticmethod
    def resource_clean_dir_by_name(root_path: str, dir_name_list: List[str]) -> None:
        root_path = BaseUtil.get_project_root_path()
        dir_list = ['src', 'tests', 'submodules']
        for dir_name in dir_list:
            path_obj = Path(os.path.join(root_path, dir_name))
            for path in path_obj.rglob('__pycache__'):
                if path.is_dir():
                    print(f"Deleting directory: {path}")
                    shutil.rmtree(path)


if __name__ == "__main__":
    os.chdir(BaseUtil.get_project_root_path())
    CleanUtil.clean_old_builds()
    CleanUtil.clean_cache()
