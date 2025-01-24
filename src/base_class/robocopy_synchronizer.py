#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: General Robocopy Synchronizer Base Class.
"""
import concurrent.futures
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict

from base_class.json_parser import JsonParser
from base_class.thread_pool_task_executor import ThreadPoolTaskExecutor
from utils.log_ins import LogUtil
from utils.subprocess_util import SubprocessUtil

logger = LogUtil.get_logger()


@dataclass
class RobocopyTaskParam:
    ident: str = None
    src_path: str = None
    dst_path: str = None
    exclude_files: list[str] = None
    exclude_dirs: list[str] = None
    log_path: str = None


class RobocopySynchronizer(ThreadPoolTaskExecutor, JsonParser):
    NAME: str = "General Robocopy Synchronizer"
    DEFAULT_PROFILE_NAME: str = "robocopy_synchronizer.json"

    def __init__(self, profile_path: str = None, default_profile_name: str = None):

        self._robocopy_tasks_param_list: list[RobocopyTaskParam] = []

        # Initialize the base class
        JsonParser.__init__(self, profile_path=profile_path,
                            default_profile_name=default_profile_name or self.DEFAULT_PROFILE_NAME)
        ThreadPoolTaskExecutor.__init__(self, task_count=len(self._robocopy_tasks_param_list))

    @staticmethod
    def parse_global_param(json_data) -> RobocopyTaskParam:
        robocopy_sync_json_data = json_data.get("robocopy_synchronizer")
        if robocopy_sync_json_data is None:
            logger.info("Cannot get 'robocopy_synchronizer' section from the profile.")
            return RobocopyTaskParam()

        param = RobocopyTaskParam(src_path=robocopy_sync_json_data.get("src_path_fmt"),
                                  dst_path=robocopy_sync_json_data.get("dst_path_fmt"),
                                  exclude_files=robocopy_sync_json_data.get("exclude_files"),
                                  exclude_dirs=robocopy_sync_json_data.get("exclude_dirs"),
                                  log_path=robocopy_sync_json_data.get("log_path_fmt"))
        return param

    @staticmethod
    def generate_archive_map(global_param: RobocopyTaskParam, map_json) -> RobocopyTaskParam:
        ip: str = map_json.get("ip")
        task_param = RobocopyTaskParam(ident=map_json.get("id"),
                                       src_path=map_json.get("robocopy_src_path") or global_param.src_path.format(ip),
                                       dst_path=map_json.get("robocopy_dst_path") or global_param.dst_path.format(
                                           map_json.get("id").upper()), exclude_files=map_json.get(
                "robocopy_exclude_files") or global_param.exclude_files,
                                       exclude_dirs=map_json.get("robocopy_exclude_dirs") or global_param.exclude_dirs,
                                       log_path=map_json.get("robocopy_log_path") or global_param.log_path.format(
                                           map_json.get("id").upper()))
        return task_param

    def _do_parsr_profile_content(self, json_data):
        """
        Parse the profile file and populate maps.

        Raises:
            ValueError: If the map list is empty.
        """
        # Parse global parameter(s)
        global_robocopy_param: RobocopyTaskParam = self.parse_global_param(json_data)

        # Parse parameter(s) of current instance
        for map_json in json_data["maps"]:
            self._robocopy_tasks_param_list.append(self.generate_archive_map(global_robocopy_param, map_json))
        if not self._robocopy_tasks_param_list:
            raise ValueError("Map list is empty.")
        logger.info("Successfully parse instance variable(s) from profile, maps count: %d.",
                    len(self._robocopy_tasks_param_list))

        # Parse parameter(s) of base instance
        super()._do_parsr_profile_content(json_data)

    @staticmethod
    def robocopy_mirror(param: RobocopyTaskParam) -> int:
        """
        Executes a mirror sync using Robocopy.

        Args:
            param (RobocopyTaskParam): Parameter(s) set of robocopy task.

        Returns:
            int: Exit code

        Raises:
            FileNotFoundError: If the source directory does not exist.
            NotADirectoryError: If the source or destination path is not a directory.
            TypeError: If exclude_dirs is not a list.
            RuntimeError: If subprocess run failed.
        """
        # Validate source path
        if not os.path.exists(param.src_path):
            raise FileNotFoundError(f"Source directory '{param.src_path}' does not exist.")
        if not os.path.isdir(param.src_path):
            raise NotADirectoryError(f"Source path '{param.src_path}' is not a directory.")

        # Create destination path
        if not os.path.isdir(param.dst_path):
            if os.path.exists(param.dst_path):
                raise NotADirectoryError(f"Destination path '{param.dst_path}' is exist but not a directory.")
            logger.info("Destination directory is not exist, create it firstly: %s.", param.dst_path)
            os.makedirs(param.dst_path)

        # Create log file
        if param.log_path is not None:
            if not isinstance(param.log_path, str):
                raise ValueError(f"Log file '{param.log_path}' is not string.")
            if not os.path.isfile(param.log_path):
                logger.info("Log file is not exist, create it firstly: %s.", param.log_path)
                os.makedirs(os.path.dirname(param.log_path), exist_ok=True)
                with open(param.log_path, "w", encoding="utf-8"):
                    pass

        # Construct the Robocopy command
        cmd = ["robocopy", param.src_path, param.dst_path, "/MIR", "/MT", "/Z", "/R:3", "/W:5"]

        # Add excluded file(s)
        if param.exclude_files and len(param.exclude_files):
            cmd.extend(["/XF", *param.exclude_files])

        # Add excluded directories
        if param.exclude_dirs and len(param.exclude_dirs):
            cmd.extend(["/XD", *param.exclude_dirs])

        # Add log file
        if param.log_path:
            cmd.extend(["/TEE", f"/LOG+:{param.log_path}"])

        # Execute the Robocopy command
        process = SubprocessUtil.run_cmd_without_window(cmd)
        if process.returncode >= 8:
            logger.error("Mirror sync failed: %s -> %s, result code: %d, cmd: %s\r\nstdout:\r\n%s\r\nstderr:\r\n%s.",
                         param.src_path, param.dst_path, process.returncode, cmd, process.stdout.strip(),
                         process.stderr.strip())
            raise RuntimeError(f"Robocopy mirror sync failed: {process.returncode}")
        logger.info("Mirror sync succeeded: %s -> %s, cmd: %s.", param.src_path, param.dst_path, cmd)
        return 0

    def _submit_tasks(self, executor: concurrent.futures.ThreadPoolExecutor) -> Dict[concurrent.futures.Future, Any]:
        return {executor.submit(self.robocopy_mirror, param=task_param): task_param for task_param in
                self._robocopy_tasks_param_list}

    @staticmethod
    def _validate_result(result: Any, task_data: RobocopyTaskParam) -> None:
        if result != 0:
            raise RuntimeError(f"Invalid result code for: {result}")

    def _get_task_index(self, task_data: RobocopyTaskParam) -> int:
        return self._robocopy_tasks_param_list.index(task_data)

    @staticmethod
    def _get_task_id(task_data: RobocopyTaskParam) -> str:
        return task_data.ident

    def run(self) -> None:
        self.concurrent_run_tasks()
        logger.info("Mirror sync for all maps succeeded, synced num: %d.", len(self._robocopy_tasks_param_list))


if __name__ == "__main__":
    logger.info("The program has been started.")
    runner = RobocopySynchronizer(profile_path="D:\\Data\\Projects\\TM18TEST\\New\\ToolBox\\robocopy_synchronizer.json")
    runner.run()
    logger.info("The program is about to exit.")
    sys.exit(0)
