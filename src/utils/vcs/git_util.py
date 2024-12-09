#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import os
import sys

from git import Repo
from git.exc import InvalidGitRepositoryError

from utils.base_util import BaseUtil
from utils.fs.file_util import FileUtil
from utils.log_ins import LogUtil

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

    @staticmethod
    def create_git_repository(repo_path: str) -> bool:
        if GitUtil.is_git_repository(repo_path):
            return False
        os.makedirs(repo_path, exist_ok=True)
        Repo.init(repo_path)
        logger.info("Create git repository success, repo path: %s.", repo_path)
        return True

    @staticmethod
    def load_git_untracked_diff(repo_path: str, cached: bool = False) -> str | None:
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
    def export_diff_including_untracked(repo_path: str) -> str | None:
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
    def load_tracked_diff(repo_path: str, with_header: bool = False) -> str | None:
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
    def load_untracked_diff(repo_path: str, with_header: bool = False) -> str | None:
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


if __name__ == "__main__":
    print(GitUtil.is_git_repository("D:\\Data\\Temp\\gittest"))
    print(GitUtil.load_tracked_diff("D:\\Data\\Temp\\gittest", True))
    print(GitUtil.load_untracked_diff("D:\\Data\\Temp\\gittest", True))
    sys.exit(0)
