#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Running Package Packager Base Class.
"""
import os

from utils.file_details import FileDetails, FileDetailsHandler
from utils.fs.file_util import FileUtil
from utils.fs.fs_util import FsUtil
from utils.subprocess_util import SubprocessUtil


class PackageBase:
    def __init__(self, file_details: FileDetails, ver_file_path: str, spec_file_path: str):
        # Declare some variables of current instance
        self._packaged_file_details: FileDetails = file_details
        self._ver_file_path: str = ver_file_path
        self._spec_file_path: str = spec_file_path
        self._file_details_handler: FileDetailsHandler = FileDetailsHandler(file_details, ver_file_path)

    def cleanup(self):
        pass

    def prepare_env(self):
        self.cleanup()
        os.chdir(FsUtil.get_project_root_path())

    def package_builds(self):
        dir_name: str = self._packaged_file_details.file_desc.replace(" ", "_")
        dir_path: str = os.path.join(FsUtil.get_project_root_path(), "dist", dir_name)
        output_dir_path: str = os.path.join(FsUtil.get_project_root_path(), "Packages")
        os.makedirs(output_dir_path, exist_ok=True)
        output_path: str = os.path.join(output_dir_path, dir_name) + "_v" + self._packaged_file_details.product_version
        FileUtil.compress_dir_to_zip(dir_path, output_path)

    def run(self):
        self.prepare_env()
        self._file_details_handler.generate()
        SubprocessUtil.run_cmd_list(["Pyinstaller", self._spec_file_path, "--clean"])
        self._file_details_handler.clear()
        self.package_builds()
