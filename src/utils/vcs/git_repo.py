#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import os
import sys

from git import Repo

from utils.log_ins import LogUtil
from utils.vcs.git_util import GitUtil

logger = LogUtil.get_logger()


class GitRepo:
    """
    TODO: Set the name and email of committer before commit
    """
    def __init__(self, local_repo_path: str, remote_repo_url: str = None, username: str = None, password: str = None):
        self.local_repo_path: str = local_repo_path
        self.remote_repo_url: str = remote_repo_url
        self.username: str = username
        self.password: str = password
        self.is_cloned: bool = GitUtil.is_git_repository(self.local_repo_path)

    def _construct_remote_repo_url_with_auth_info(self) -> str | None:
        url: str = self.remote_repo_url
        if url.startswith('http://'):
            return url.replace('http://', f'http://{self.username}:{self.password}@')
        # elif url.startswith('git@'):
        #    return url.replace('git@', f'git@{self.username}:{self.password}@')
        raise RuntimeError(f'Unsupported repo protocol: {self.remote_repo_url}')

    def clone(self):
        Repo.clone_from(self._construct_remote_repo_url_with_auth_info(), self.local_repo_path)
        self.is_cloned = True
        logger.info("Clone from remote git repository success, remote: %s, local: %s.",
                    self.remote_repo_url, self.local_repo_path)

    def pull(self):
        with Repo(self.local_repo_path) as r:
            r.git.pull()
        logger.info("Pull from remote git repository success, local repo path: %s.", self.local_repo_path)

    def commit(self, msg: str, all_files: bool = True) -> bool:
        with Repo(self.local_repo_path) as r:
            is_need_commit: bool = (all_files and r.untracked_files)

            r.git.add(all=all_files)

            if not is_need_commit:
                try:
                    if r.index.diff("HEAD"):
                        is_need_commit = True
                except Exception:
                    pass

            if is_need_commit:
                r.index.commit(msg)
                logger.info("Commit git repository success, repo path: %s, msg: %s, all files: %s.",
                            self.local_repo_path, msg, all_files)
                return True
            logger.warning("Unnecessary to commit because there is no changes.")
        return False

    def push(self):
        with Repo(self.local_repo_path) as r:
            origin = r.remote(name="origin")
            # origin.push(self._construct_remote_repo_url_with_auth_info())
            origin.push()
        logger.info("Push to remote git repository success, local : %s, remote: %s.",
                    self.local_repo_path, self.remote_repo_url)

    def load_tracked_diff(self, with_header: bool = False) -> str | None:
        return GitUtil.load_tracked_diff(self.local_repo_path, with_header)

    def load_untracked_diff(self, with_header: bool = False) -> str | None:
        return GitUtil.load_untracked_diff(self.local_repo_path, with_header)

    @staticmethod
    def create_local_git_repository(repo_path: str) -> bool:
        if GitUtil.is_git_repository(repo_path):
            return False
        os.makedirs(repo_path, exist_ok=True)
        Repo.init(repo_path)
        logger.info("Create git repository success, repo path: %s.", repo_path)
        return True


if __name__ == "__main__":
    repo = GitRepo("E:\\CC\\Temp\\gittest",
                   'http://10.106.72.53:3000/recipe_vtec_rep/a1rep0120.git',
                   'Administrator', 'Administrator1')
    print(repo.is_cloned)
    if not repo.is_cloned:
        repo.clone()
    print(repo.load_tracked_diff())
    print(repo.load_untracked_diff())
    repo.commit("test msg", True)
    repo.push()
    sys.exit(0)
