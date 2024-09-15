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
    def clean_old_builds() -> None:
        root_path = BaseUtil.get_project_root_path()
        builds_dir_list: List[str] = ["build", "dist"]
        for entry in builds_dir_list:
            full_path = os.path.join(root_path, entry)
            if os.path.isdir(full_path):
                print(f"Deleting directory: {full_path}")
                shutil.rmtree(full_path)

    @staticmethod
    def clean_cache() -> None:
        root_path = BaseUtil.get_project_root_path()
        src_path = Path(os.path.join(root_path, 'src'))
        test_path = Path(os.path.join(root_path, 'tests'))
        for path in src_path.rglob('__pycache__'):
            if path.is_dir():
                print(f"Deleting directory: {path}")
                shutil.rmtree(path)
        for path in test_path.rglob('__pycache__'):
            if path.is_dir():
                print(f"Deleting directory: {path}")
                shutil.rmtree(path)


if __name__ == "__main__":
    os.chdir(BaseUtil.get_project_root_path())
    CleanUtil.clean_old_builds()
    CleanUtil.clean_cache()
