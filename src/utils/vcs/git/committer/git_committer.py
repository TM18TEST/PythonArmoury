#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: General Gti Committer Base Class.
"""
from typing import Optional

import git

from utils.log_ins import LogUtil
from utils.vcs.git.committer.git_committer_modify_time_grouped import ModifyTimeGroupedCommitter
from utils.vcs.git_util import GitUtil

logger = LogUtil.get_logger()


class GitCommitter:
    """Git committer class with support for basic commits, exclusion rules,
    and batch commits based on file modification time.

    Attributes:
        repo_path: str, path to the Git repository.
        repo: Repo, GitPython's Repo instance.
        exclude_dirs: set[str], set of directories to exclude.
        exclude_files: set[str], set of files to exclude.
    """
    DEFAULT_TIME_INTERVAL_SEC = 3600.0

    def __init__(self, repo_path: str):
        """Initializes GitCommitter.

        Args:
            repo_path: str, path to the Git repository.
        """
        self.repo_path = repo_path
        self.repo: Optional[git.Repo] = None
        self.exclude_dirs_list: Optional[list[str]] = None
        self.exclude_files_list: Optional[list[str]] = None
        self.exclude_dirs: Optional[set[str]] = None
        self.exclude_files: Optional[set[str]] = None
        self.time_diff_sec: Optional[int] = None

    def __enter__(self):
        """Enter the context and open the repository."""
        self.repo = git.Repo(self.repo_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context and close the repository."""
        if self.repo is not None:
            self.repo.close()
            self.repo = None

    def set_exclusions(self, dirs: list[str], files: list[str]) -> None:
        """Sets directories and files to exclude from commits.

        Args:
            dirs: list[str], list of directories to exclude.
            files: list[str], list of files to exclude.
        """
        self.exclude_dirs_list = dirs
        self.exclude_files_list = files
        self.exclude_dirs = set(dirs)
        self.exclude_files = set(files)

    def set_group_time_interval(self, time_diff_sec: float = None) -> None:
        """Sets time interval unit as second used to group change files by modification time.

        Args:
            time_diff_sec: float | None, time interval in seconds to group files to difference commit
                           based on their modification time.
        """
        self.time_diff_sec = time_diff_sec

    def commit_changes(self, message: str, author_name: str = None, author_email: str = None) -> int:
        """Commits changes to the repository, optionally batching by modification time.

        Args:
            message: str, commit message.
            author_name: str, author's Name
            author_email: str, author's E-Mail
        """
        # Group commits by files modification time
        commit_num: int = 0
        if self.time_diff_sec is not None:
            commit_num = ModifyTimeGroupedCommitter(repo_path=self.repo_path,
                                                    time_diff_sec=self.time_diff_sec,
                                                    exclude_files=self.exclude_files_list,
                                                    exclude_dirs=self.exclude_dirs_list,
                                                    commit_msg=message,
                                                    author_name=author_name,
                                                    author_email=author_email).run()
            return commit_num

        # Commit changes normally
        try:
            if GitUtil.add_files_to_stage(self.repo_path, self.exclude_dirs_list, self.exclude_files_list):
                with git.Repo(self.repo_path) as repo:
                    if author_name and author_email:
                        author = git.Actor(name=author_name, email=author_email)
                        repo.index.commit(message=message, author=author)
                    else:
                        repo.index.commit(message=message)
                    logger.info("Commit successful: %s, directory: %s", message, self.repo_path)
                    commit_num += 1
            else:
                logger.debug("No changes to commit: %s", self.repo_path)
        except git.exc.GitError as e:
            logger.error("Git operation failed for directory: %s. Error: %s", self.repo_path, e)
            raise
        return commit_num
