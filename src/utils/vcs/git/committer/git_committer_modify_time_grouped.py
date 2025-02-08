#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Git Committer Grouped By Modified Time.
"""
import os
import sys
import time

import git
from datetime import datetime, timezone, timedelta
from typing import Optional

from utils.log_ins import LogUtil

logger = LogUtil.get_logger()


class ModifyTimeGroupedCommitter:
    """Git Committer Grouped By Modified Time."""

    def __init__(self, repo_path: str, time_diff_sec: float = 3600.0,
                 exclude_files: list[str] = None, exclude_dirs: list[str] = None,
                 commit_msg: Optional[str] = None, author_name: str = None, author_email: str = None):
        """
        Args:
            repo_path (str): The path to the Git repository.
            time_diff_sec (float): The time difference (in seconds) used to group files by modification time.
            exclude_files (Optional[list[str]]): A list of files to exclude from commits.
            exclude_dirs (Optional[list[str]]): A list of directories to exclude from commits.
            commit_msg (Optional[str]): The commit message.
        """
        self._repo_path: str = repo_path
        self._time_diff_sec: float = time_diff_sec
        self._exclude_files: set[str] = set(exclude_files) if exclude_files else set()
        self._exclude_dirs: set[str] = set(os.path.normpath(d) for d in exclude_dirs) if exclude_dirs else set()
        self._commit_msg: str = commit_msg or (
            f"Automatic update by tool, update time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        )
        self._commit_author: Optional[git.Actor] = None
        if author_name and author_email:
            self._commit_author = git.Actor(name=author_name, email=author_email)
        self._file_path_modify_time_list: Optional[list[tuple[str, float]]] = []
        self._grouped_files: list[list[tuple[str, float]]] = []

    @staticmethod
    def get_repo_changes_files(repo_path: str,
                               exclude_files: set, exclude_dirs: set) -> Optional[list[tuple[str, float]]]:
        """
        Get the list of changed files (modified or untracked) in the repository.
        Exclude files and directories specified in `exclude_files` and `exclude_dirs`.

        Args:
            repo_path (str): The path to the Git repository.
            exclude_files (set): A set of file names to exclude.
            exclude_dirs (set): A set of directory paths to exclude.

        Returns:
            Optional[list[tuple[str, float]]]: A list of tuples containing file paths and their modification times.
        """
        start_time: float = time.time()
        with git.Repo(repo_path) as repo:
            # TODO: Time-consuming optimize, 120 Second
            modified_files = [item.a_path for item in repo.index.diff(None)]
            untracked_files = repo.untracked_files
            changes_files = modified_files + untracked_files
        logger.debug("Collect changes from repo success, elapsed time: %.3f seconds.", time.time() - start_time)

        file_list = []
        for file in changes_files:
            file_abs_path = os.path.join(repo_path, file)

            # Exclude files or directories
            if file in exclude_files or os.path.dirname(file) in exclude_dirs:
                continue

            try:
                if os.path.exists(file_abs_path):
                    modify_time = os.path.getmtime(file_abs_path)
                else:
                    modify_time = time.time()
                file_list.append((file, modify_time))
            except OSError as e:
                logger.warning("Error getting modification time for %s: %s", file_abs_path, e)
        logger.debug("Get changes success, elapsed time: %.3f seconds.", time.time() - start_time)
        return file_list

    @staticmethod
    def group_files_by_modify_time(file_list: list[tuple[str, float]],
                                   time_diff_sec: float) -> list[list[tuple[str, float]]]:
        """
        Group files by modification time based on a specified time difference.

        Args:
            file_list (list[tuple[str, float]]): A list of tuples containing file paths and their modification times.
            time_diff_sec (float): The time difference in seconds for grouping files.

        Returns:
            list[list[tuple[str, float]]]: A list of groups, each containing files with close modification times.
        """
        start_time: float = time.time()
        file_list.sort(key=lambda x: x[1])
        logger.debug("Sort files by modification time success, elapsed time: %.3f seconds.", time.time() - start_time)
        start_time = time.time()

        grouped_files = []
        current_group = []
        last_modify_time = None

        for file_path, modify_time in file_list:
            # First file or within the time difference
            if last_modify_time is None or abs(modify_time - last_modify_time) <= time_diff_sec:
                current_group.append((file_path, modify_time))
            else:
                # Start a new group
                grouped_files.append(current_group)
                current_group = [(file_path, modify_time)]

            last_modify_time = modify_time

        # Append the last group if any
        if current_group:
            grouped_files.append(current_group)

        logger.debug("Group files by modification time success, elapsed time: %.3f seconds.", time.time() - start_time)
        return grouped_files

    @staticmethod
    def create_commits_by_group(repo_path: str, grouped_change_files: list[list[tuple[str, float]]],
                                commit_msg: str, commit_author: git.Actor = None) -> int:
        """
        Create Git commits for each group of modified files.

        Args:
            repo_path (str): The path to the Git repository.
            grouped_change_files (list[list[tuple[str, float]]]): A list of file groups to commit.
            commit_msg (str): The commit message.
            commit_author (git.Actor): The commit author info.

        Returns:
            int: The number of commits created.
        """
        commit_num = 0
        with git.Repo(repo_path) as repo:
            for group in grouped_change_files:
                start_time = time.time()
                # Add all files in the group
                # TODO: Time-consuming optimize
                for file_relpath, _ in group:
                    repo.git.add(file_relpath)
                logger.debug("Successfully add changes files in one group, file num: %d, elapsed time: %.3f seconds.",
                             len(group), time.time() - start_time)

                # Use the modification time of the last file in the group as the commit time
                commit_time = datetime.fromtimestamp(group[-1][1], tz=timezone(timedelta(hours=8)))

                # Commit the changes
                repo.index.commit(message=commit_msg, author=commit_author,
                                  author_date=commit_time, commit_date=commit_time)
                commit_num += 1
                logger.debug("Successfully commit for one group, file num: %d, elapsed time: %.3f seconds.",
                             len(group), time.time() - start_time)

        return commit_num

    def run(self) -> int:
        """
        Execute the commit process: fetch changed files, group them by modification time, and commit them.

        Returns:
            Optional[int]: The number of commits created.
        """
        # Get changes files
        start_time: float = time.time()
        self._file_path_modify_time_list = self.get_repo_changes_files(self._repo_path, self._exclude_files,
                                                                       self._exclude_dirs)
        if not self._file_path_modify_time_list:
            logger.info("No changes detected in the repository: %s.", self._repo_path)
            return 0
        logger.debug("Successfully get changes files, file num: %d, elapsed time: %.3f seconds.",
                     len(self._file_path_modify_time_list), time.time() - start_time)

        # Group files by modified time
        start_time = time.time()
        self._grouped_files = self.group_files_by_modify_time(self._file_path_modify_time_list, self._time_diff_sec)
        logger.debug("Successfully group files by modified time, group num: %d, elapsed time: %.3f seconds.",
                     len(self._grouped_files), time.time() - start_time)

        # Commit by group
        start_time = time.time()
        commit_num = self.create_commits_by_group(self._repo_path, self._grouped_files,
                                                  self._commit_msg, self._commit_author)
        logger.debug("Successfully committed changes by group, total commits: %d, elapsed time: %.3f seconds.",
                     commit_num, time.time() - start_time)
        return commit_num


if __name__ == "__main__":
    logger.info("The program has been started.")
    committer = ModifyTimeGroupedCommitter(
        repo_path="J:\\Tmp\\A1REP0120_Recipes\\env\\Recipe",
        exclude_files=["998@Mark_Inline.recipe"],
        exclude_dirs=["AutoRepair", "AutoRepairImage"]
    )
    committer.run()
    logger.info("The program is about to exit.")
    sys.exit(0)
