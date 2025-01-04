#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: SMB Gitter Class Source Code.
"""

import os.path

from utils.fs.smb_utils import SmbConn
from utils.vcs.git_repo import GitRepo
from utils.vcs.git_util import GitUtil


class SmbGitter:
    def __init__(self, smb_ip: str, smb_host_name: str, smb_username: str, smb_password: str,
                 smb_service_name: str, smb_entry_path: str,
                 git_remote_repo_path: str, git_local_repo_path: str, git_repo_username: str, git_repo_password: str):
        self.smb_ip: str = smb_ip
        self.smb_host_name: str = smb_host_name
        self.smb_username: str = smb_username
        self.smb_password: str = smb_password
        self.smb_service_name: str = smb_service_name
        self.smb_entry_path: str = smb_entry_path
        self.git_remote_repo_path: str = git_remote_repo_path
        self.git_local_repo_path: str = git_local_repo_path
        self.git_repo_username: str = git_repo_username
        self.git_repo_password: str = git_repo_password
        self.git_repo = GitRepo(self.git_local_repo_path, self.git_remote_repo_path,
                                self.git_repo_username, self.git_repo_password)

    def run(self, commit_msg: str = "Auto commit"):
        # Sync local repo from remote
        if GitUtil.is_git_repository(self.git_local_repo_path):
            self.git_repo.discard_local_changes()
            self.git_repo.sync_from_remote()
        else:
            os.makedirs(self.git_local_repo_path, exist_ok=True)
            self.git_repo.clone()

        # Download recipe file(s) from remote SMB server
        with SmbConn(ip=self.smb_ip, user=self.smb_username, password=self.smb_password,
                     service_name=self.smb_service_name) as s:
            s.download(self.smb_entry_path, self.git_local_repo_path)

        # Commit local changes and then push to remote
        if self.git_repo.commit(commit_msg):
            self.git_repo.push()
