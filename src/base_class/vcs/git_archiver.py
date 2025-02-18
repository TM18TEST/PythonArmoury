#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: General Gti Archiver Base Class.
"""
import sys
import concurrent.futures
from dataclasses import dataclass
from typing import Any, Dict, Optional

from base_class.json_parser import JsonParser
from base_class.thread_pool_task_executor import ThreadPoolTaskExecutor
from utils.codec.base64_codec import Base64Codec
from utils.vcs.git.git_wrapper import GitWrapper
from utils.log_ins import LogUtil

logger = LogUtil.get_logger()


@dataclass
class GitArchiveTaskParam:
    ident: str = None
    dir_path: str = None

    # Clone parameter(s) also used to push
    url: str = None
    username: str = None
    password: str = None

    # Commit parameter(s)
    exclude_files: list[str] = None
    exclude_dirs: list[str] = None
    group_commits: bool = None
    commit_msg: str = None
    author_name: str = None
    author_email: str = None

    # Push parameter(s)
    push_after_commit: bool = None


class GitArchiver(JsonParser, ThreadPoolTaskExecutor):
    NAME: str = "General Gti Archiver"
    DEFAULT_PROFILE_NAME: str = "git_archiver.json"

    def __init__(self, profile_path: str = None, default_profile_name: str = None):
        # Declare some variables of current instance
        self._archive_tasks_param_list: list[GitArchiveTaskParam] = []
        self._max_workers: Optional[int] = None

        # Initialize the base class
        JsonParser.__init__(self, profile_path=profile_path,
                            default_profile_name=default_profile_name or self.DEFAULT_PROFILE_NAME)
        ThreadPoolTaskExecutor.__init__(self, task_count=len(self._archive_tasks_param_list),
                                        max_workers=self._max_workers)

    @staticmethod
    def parse_global_param(json_data) -> GitArchiveTaskParam:
        git_archiver_json_data = json_data.get("git_archiver")
        if git_archiver_json_data is None:
            logger.info("Cannot get 'git_archiver' section from the profile.")
            return GitArchiveTaskParam()

        param = GitArchiveTaskParam(
            dir_path=git_archiver_json_data.get("path_fmt"),
            url=git_archiver_json_data.get("url_fmt"),
            username=git_archiver_json_data.get("username"),
            password=git_archiver_json_data.get("password"),
            exclude_files=git_archiver_json_data.get("exclude_files"),
            exclude_dirs=git_archiver_json_data.get("exclude_dirs"),
            group_commits=git_archiver_json_data.get("group_commits"),
            commit_msg=git_archiver_json_data.get("commit_msg"),
            author_name=git_archiver_json_data.get("commit_author_name"),
            author_email=git_archiver_json_data.get("commit_author_name"),
            push_after_commit=git_archiver_json_data.get("push_after_commit"),
        )
        if param.password is None and git_archiver_json_data.get("encoded_password") is not None:
            param.password = Base64Codec.decode(git_archiver_json_data.get("encoded_password"))
        return param

    @staticmethod
    def generate_archive_map(global_param: GitArchiveTaskParam, map_json) -> GitArchiveTaskParam:
        ident: str = map_json.get("id")
        task_param = GitArchiveTaskParam(
            ident=ident,
            dir_path=map_json.get("repo_dir_path") or global_param.dir_path.format(ident.upper()),
            url=map_json.get("repo_url") if "repo_url" in map_json else (
                global_param.url.format(ident.lower()) if global_param.url else None
            ),
            username=map_json.get("repo_username") or global_param.username,
            password=map_json.get("repo_password") or global_param.password,
            exclude_files=map_json.get("repo_exclude_files") or global_param.exclude_files,
            exclude_dirs=map_json.get("repo_exclude_dirs") or global_param.exclude_dirs,
            group_commits=map_json.get("repo_group_commits") or global_param.group_commits,
            commit_msg=map_json.get("repo_commit_msg") or global_param.commit_msg,
            author_name=map_json.get("repo_author_name") or global_param.author_name,
            author_email=map_json.get("repo_author_email") or global_param.author_email,
            push_after_commit=map_json.get("repo_push_after_commit") or global_param.push_after_commit,
        )
        if task_param.password is None and map_json.get("repo_encoded_password") is not None:
            task_param.password = Base64Codec.decode(map_json.get("encoded_password"))
        return task_param

    def _do_parsr_profile_content(self, json_data):
        """
        Parse the profile file and populate maps.

        Raises:
            ValueError: If the map is empty.
        """

        # Parse global parameter(s)
        task_param: GitArchiveTaskParam = self.parse_global_param(json_data)
        if "git_archiver" in json_data and "max_workers" in json_data.get("git_archiver"):
            self._max_workers = json_data.get("git_archiver").get("max_workers")
            logger.debug("Max workers: %d.", self._max_workers)

        # Parse map(s)
        for map_json in json_data["maps"]:
            self._archive_tasks_param_list.append(self.generate_archive_map(task_param, map_json))
        if not self._archive_tasks_param_list:
            raise ValueError("Archive task list is empty.")
        logger.info("Successfully parse profile, archive task count: %d.", len(self._archive_tasks_param_list))

    def _pre_init_repo(self, ident: str, dir_path: str, repo_url: str = None,
                       repo_username: str = None, repo_password: str = None) -> None:
        logger.debug("Do nothing in Pre-InitRepo step, id: %s, dir path: %s.", ident, dir_path)

    def _pre_commit(self, ident: str, dir_path: str) -> None:
        logger.debug("Do nothing in pre-commit step, id: %s, dir path: %s.", ident, dir_path)

    def _post_push(self, ident: str, dir_path: str) -> None:
        logger.debug("Do nothing in post-push step, id: %s, dir path: %s.", ident, dir_path)

    # @staticmethod
    def _archive_by_git(self, param: GitArchiveTaskParam) -> int:
        """Archives the specified directory into a Git repository.

        If the directory is not a Git repository, initializes one and commits
        all files.

        Args:
            param: Parameter(s) set of archive task.

        Raises:
            FileNotFoundError: If the path is not a directory
            OSError: If the directory cannot be created.
            git.exc.GitError: If a Git operation fails.
        """
        # Initialize Git repository
        self._pre_init_repo(param.ident, param.dir_path)
        GitWrapper.init_repo(repo_path=param.dir_path,
                             repo_url=param.url,
                             repo_username=param.username,
                             repo_password=param.password)

        # Commit changes
        self._pre_commit(param.ident, param.dir_path)
        commit_num: int = GitWrapper.commit(repo_path=param.dir_path,
                                            group_commits=param.group_commits,
                                            commit_msg=param.commit_msg,
                                            exclude_files=param.exclude_files,
                                            exclude_dirs=param.exclude_dirs,
                                            author_name=param.author_name,
                                            author_email=param.author_email)
        # push after commit
        if commit_num > 0 and param.url and param.username and param.password and param.push_after_commit:
            GitWrapper.push(repo_path=param.dir_path)
        self._post_push(param.ident, param.dir_path)
        return 0

    def _submit_tasks(self, executor: concurrent.futures.ThreadPoolExecutor) -> Dict[concurrent.futures.Future, Any]:
        return {executor.submit(self._archive_by_git,
                                param=task_param): task_param for task_param in self._archive_tasks_param_list}

    @staticmethod
    def _validate_result(result: Any, task_data: Any) -> None:
        if result != 0:
            raise RuntimeError(f"Invalid result code for: {result}")

    def _get_task_index(self, task_data: Any) -> int:
        return self._archive_tasks_param_list.index(task_data)

    @staticmethod
    def _get_task_id(task_data: Any) -> str:
        return task_data.ident

    def run(self) -> None:
        # Run task(s) concurrently
        self.concurrent_run_tasks()
        logger.info("Git archive for all maps succeeded, archived num: %d.", len(self._archive_tasks_param_list))


if __name__ == "__main__":
    logger.info("The program has been started.")
    archiver = GitArchiver()
    archiver.run()
    logger.info("The program is about to exit.")
    sys.exit(0)
