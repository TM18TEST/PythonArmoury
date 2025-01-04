#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Git Utility Class Source Code.
"""
import glob
import os
import shutil
import sys
from datetime import datetime
from typing import Optional

import git
from git import Repo
from git.exc import InvalidGitRepositoryError, GitCommandError, NoSuchPathError

from utils.base_util import BaseUtil
from utils.fs.file_util import FileUtil
from utils.log_ins import LogUtil
from utils.time_util import TimeDuration

logger = LogUtil.get_logger()


class GitUtil:
    def __init__(self, local_repo_path: str, repo_url: str = None, username: str = None, password: str = None):
        self.local_repo_path: str = local_repo_path
        self.repo_url: str = repo_url
        self.username: str = username
        self.password: str = password

    @staticmethod
    def is_git_repository(dir_path: str) -> bool:
        try:
            Repo(dir_path).git_dir
            return True
        except InvalidGitRepositoryError:
            return False
        except NoSuchPathError:
            return False

    @staticmethod
    def delete_entries_except_git_data(dir_path: str) -> None:
        for item in glob.glob(os.path.join(dir_path, '*')):
            if os.path.isdir(item):
                if '.git' not in item:
                    shutil.rmtree(item)
            else:
                if '.gitignore' not in item:
                    os.remove(item)

    @staticmethod
    def create_local_empty_git_repo(repo_path: str) -> bool:
        if GitUtil.is_git_repository(repo_path):
            return False
        os.makedirs(repo_path, exist_ok=True)
        Repo.init(repo_path)
        return True

    @staticmethod
    def clone_git_repository(repo_url: str, local_repo_path: str, username: str, password: str):
        try:
            repo = Repo.clone_from(
                repo_url,
                local_repo_path,
                env={
                    'GIT_ASKPASS': 'echo',
                    'GIT_USERNAME': username,
                    'GIT_PASSWORD': password
                }
            )
            repo.close()
        except GitCommandError as exc:
            logger.error("Error cloning repository: %s", str(exc))
            raise exc

    @staticmethod
    def create_git_repository(repo_path: str) -> bool:
        if GitUtil.is_git_repository(repo_path):
            return False
        os.makedirs(repo_path, exist_ok=True)
        Repo.init(repo_path)
        logger.info("Create git repository success, repo path: %s.", repo_path)
        return True

    @staticmethod
    def load_git_untracked_diff(repo_path: str, cached: bool = False) -> Optional[str]:
        repo = Repo(repo_path)
        if not repo.is_dirty(untracked_files=True):
            return None
        diff = repo.git.diff(cached=cached)
        return diff

    @staticmethod
    def commit_all_untracked(repo_path: str, msg: str, all_files: bool = True) -> bool:
        repo = Repo(repo_path)
        repo.git.add(all=all_files)
        if repo.index.diff("HEAD") or repo.untracked_files:
            repo.index.commit(msg)
            logger.info("Commit git repository success, repo path: %s, msg: %s, all files: %s.",
                        repo_path, msg, all_files)
            return True
        return False

    @staticmethod
    def export_git_diff(repo_path, output_path):
        """
        导出 Git 仓库中未提交的差异到指定文件。
        :param repo_path: Git 仓库路径
        :param output_path: 差异内容导出的文件路径
        """
        # 打开仓库
        repo = Repo(repo_path)
        if repo.is_dirty(untracked_files=True):  # 确保仓库有未提交更改
            print("发现未提交的更改，正在提取差异...")

            # 提取暂存区（staged changes）的差异
            staged_diff = repo.git.diff(cached=True)

            # 提取工作区（unstaged changes）的差异
            unstaged_diff = repo.git.diff()

            # 将差异内容保存到文件
            with open(output_path, "w", encoding="utf-8") as diff_file:
                if staged_diff:
                    diff_file.write("### Staged Changes ###\n")
                    diff_file.write(staged_diff + "\n\n")
                if unstaged_diff:
                    diff_file.write("### Unstaged Changes ###\n")
                    diff_file.write(unstaged_diff + "\n\n")

            print(f"未提交的差异已导出到 {output_path}")
        else:
            print("没有未提交的更改，跳过导出")

    @staticmethod
    def export_diff_including_untracked(repo_path: str) -> Optional[str]:
        """导出 Git 仓库中的未提交差异，包括未受版本控制文件。

        Args:
            repo_path (str): Git 仓库路径。
            output_file (str): 输出的 diff 文件路径。

        Returns:
            None
        """
        try:
            # 打开 Git 仓库
            repo = Repo(repo_path)

            # 检查仓库状态，是否有未提交或未受版本控制的更改
            if not repo.is_dirty(untracked_files=True):
                return None

            # 获取已版本控制文件的未提交差异
            tracked_diff = repo.git.diff()
            if not BaseUtil.is_empty(tracked_diff):
                tracked_diff = "# Tracked diff\r\n" + tracked_diff

            # 获取未受版本控制的文件列表
            untracked_files = repo.untracked_files

            # 准备未受版本控制文件的差异内容
            untracked_diff = ""
            for file in untracked_files:
                file_path = os.path.join(repo_path, file)
                if os.path.isfile(file_path):
                    if FileUtil.is_binary_file(file_path):
                        untracked_diff += f"\n\n--- {file} (untracked, binary) ---"
                    else:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        untracked_diff += f"\n\n--- {file} (untracked) ---\n{content}"
            untracked_diff = "# Untracked files content\r\n" + untracked_diff

            diff = tracked_diff + "\r\n\r\n" + untracked_diff
            return diff
        except Exception as e:
            print(f"发生错误: {e}")

    @staticmethod
    def load_tracked_diff(repo_path: str, with_header: bool = False) -> Optional[str]:
        """导出 Git 仓库中的未提交差异，包括未受版本控制文件。

        Args:
            repo_path (str): Git 仓库路径。
            with_header (bool): Start with content header or not

        Returns:
            None
        """
        # 打开 Git 仓库
        repo = Repo(repo_path)

        # 检查仓库状态，是否有未提交或未受版本控制的更改
        if not repo.is_dirty(untracked_files=False):
            return None

        # 获取已版本控制文件的未提交差异
        tracked_diff = repo.git.diff()
        if BaseUtil.is_empty(tracked_diff):
            return None
        if with_header:
            tracked_diff = "# Tracked File(s) Content\r\n" + tracked_diff
        return tracked_diff

    @staticmethod
    def load_untracked_diff(repo_path: str, with_header: bool = False) -> Optional[str]:
        """导出 Git 仓库中的未提交差异，包括未受版本控制文件。

        Args:
            repo_path (str): Git 仓库路径。
            with_header (bool): Start with content header or not

        Returns:
            None
        """
        # 打开 Git 仓库
        repo = Repo(repo_path)

        # 检查仓库状态，是否有未提交或未受版本控制的更改
        if not repo.is_dirty(untracked_files=True):
            return None

        # 获取未受版本控制的文件列表
        untracked_files = repo.untracked_files

        # 准备未受版本控制文件的差异内容
        untracked_diff = ""
        for file in untracked_files:
            file_path = os.path.join(repo_path, file)
            if not os.path.isfile(file_path):
                continue

            if FileUtil.is_binary_file(file_path):
                untracked_diff += f"\r\n--- {file} (untracked, binary) ---"
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                untracked_diff += f"\r\n--- {file} (untracked) ---\r\n{content}"
        if BaseUtil.is_empty(untracked_diff):
            return None
        if with_header:
            untracked_diff = "# Untracked File(s) Content\r\n" + untracked_diff
        return untracked_diff

    @staticmethod
    def export_changes_between_time_points(local_repo_path: str, time_duration: TimeDuration) -> Optional[str]:
        start_time: str = datetime.fromtimestamp(time_duration.start_timestamp_second).strftime('%Y-%m-%d %H:%M:%S')
        end_time: str = datetime.fromtimestamp(time_duration.end_timestamp_second).strftime('%Y-%m-%d %H:%M:%S')

        with Repo(local_repo_path) as r:
            commits = list(r.iter_commits(since=start_time, until=end_time))
            if not commits:
                return None

            # Get the first and last commit in the range
            start_commit = commits[-1]
            end_commit = commits[0]

            # Ensure start_commit has a parent (not the first commit)
            start_commit = start_commit.parents[0] if start_commit.parents else start_commit

            # Return the diff between commits
            # the diff will contain end_commit but not start_commit
            diff = r.git.diff(start_commit, end_commit)
            return diff

    @staticmethod
    def should_include(path: str, repo_path: str, exclude_dirs: list[str], exclude_files: list[str]) -> bool:
        """Check if a file or directory should be included based on exclusion rules.

        Args:
            path (str): The path to the file or directory to check.
            repo_path (str): The root path of the repository.
            exclude_dirs (list[str]): List of directories to exclude.
            exclude_files (list[str]): List of files to exclude.

        Returns:
            bool: True if the file should be included, False otherwise.
        """
        # Ensure the path is relative to the repository
        relative_path = os.path.normpath(path)

        # Check if the path starts with any of the excluded directories
        for exclude_dir in exclude_dirs:
            if relative_path.startswith(exclude_dir + os.sep):
                return False

        # Check if the file is in the excluded files list
        if os.path.basename(relative_path) in exclude_files:
            return False

        return True

    @staticmethod
    def add_files_to_stage(repo_path: str, exclude_dirs: list[str] = None, exclude_files: list[str] = None) -> bool:
        """Add files to the git staging area excluding specified directories and files.

        Args:
            repo_path (str): The path to the Git repository.
            exclude_dirs (list[str], optional): List of directories to exclude. Defaults to None.
            exclude_files (list[str], optional): List of files to exclude. Defaults to None.
        """
        exclude_dirs = exclude_dirs if exclude_dirs is not None else []
        exclude_files = exclude_files if exclude_files is not None else []

        with git.Repo(repo_path) as repo:
            exclusions = [f":(exclude){path}" for path in exclude_dirs + exclude_files]

            # 添加所有文件到暂存区，同时排除指定的目录和文件
            repo.git.add("--all", "--", *exclusions)
            # repo.git.add(all=True)
            logger.debug("exclusions: %s.", exclusions)
            return True
            files_to_add = []
            files_to_remove = []

            # Collect untracked files
            files_to_add.extend([
                file_path for file_path in repo.untracked_files
                if GitUtil.should_include(file_path, repo_path, exclude_dirs, exclude_files)
            ])

            # Collect modified files
            files_to_add.extend([
                item.a_path for item in repo.index.diff(None)
                if GitUtil.should_include(item.a_path, repo_path, exclude_dirs, exclude_files)
            ])

            # Collect files marked for deletion
            if repo.head.is_valid():
                files_to_remove.extend([
                    item.a_path for item in repo.index.diff("HEAD")
                    if
                    item.deleted_file and GitUtil.should_include(item.a_path, repo_path, exclude_dirs, exclude_files)
                ])

            # Batch add the files to the git staging area
            if files_to_add:
                # 按批次添加文件
                batch_size = 1  # 每次添加 100 个文件
                for i in range(0, len(files_to_add), batch_size):
                    batch = files_to_add[i:i + batch_size]
                    # logger.info("Goto add files: %s.", batch)
                    # repo.index.add(batch)
                    repo.git.add(batch)
                logger.info("Add files: %s.", files_to_add)

            # Batch remove deleted files from the git staging area
            if files_to_remove:
                # 按批次添加文件
                batch_size = 1  # 每次添加 100 个文件
                for i in range(0, len(files_to_remove), batch_size):
                    batch = files_to_remove[i:i + batch_size]
                    repo.git.rm(batch)
                logger.info("Remove files: %s.", files_to_remove)

            # Commit the changes
            return (len(files_to_add) > 0) or (len(files_to_remove) > 0)


if __name__ == "__main__":
    print(GitUtil.is_git_repository("D:\\Data\\Temp\\gittest"))
    print(GitUtil.load_tracked_diff("D:\\Data\\Temp\\gittest", True))
    print(GitUtil.load_untracked_diff("D:\\Data\\Temp\\gittest", True))
    sys.exit(0)
