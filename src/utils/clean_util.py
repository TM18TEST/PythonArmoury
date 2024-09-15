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
    def resource_clean_dir_by_name(root_path: str, sub_dir_name_list: List[str], del_dir_name: str) -> None:
        for sub_dir_name in sub_dir_name_list:
            path_obj = Path(os.path.join(root_path, sub_dir_name))
            for path in path_obj.rglob(del_dir_name):
                if path.is_dir():
                    print(f"Deleting directory: {path}")
                    shutil.rmtree(path)
