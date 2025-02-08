#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Git Repository Class Source Code.
"""

import sys
import time
from datetime import datetime, timezone
from typing import Optional

import git

from utils.log_ins import LogUtil
from utils.time_util import TimeDuration
from utils.vcs.git_util import GitUtil

logger = LogUtil.get_logger()


class GitRepoConfig:
    def __init__(self, url: str, local_path: str, username: str, password: str):
        self.url: str = url
        self.local_path: str = local_path
        self.username: str = username
        self.password: str = password


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

    def _construct_remote_repo_url_with_auth_info(self) -> Optional[str]:
        """Construct the URL for cloning with authentication information."""
        url: str = self.remote_repo_url
        if self.username and self.password:
            if url.startswith('http://'):
                return url.replace('http://', f'http://{self.username}:{self.password}@')
            elif url.startswith('https://'):
                return url.replace('https://', f'https://{self.username}:{self.password}@')
            # 如果使用 SSH 协议，可以将认证信息嵌入 ssh-agent 等其他机制
            # elif url.startswith('git@'):
            #     return url.replace('git@', f'git@{self.username}:{self.password}@')
            raise RuntimeError(f'Unsupported repo protocol for authentication: {url}')
        else:
            logger.error("Username and password are required for HTTP cloning.")
            RuntimeError(f'Empty username or password for authentication, url: {url}')

    def clone(self):
        """Clone the remote repository to the local path, using username and password for authentication."""
        try:
            # Construct the URL with authentication
            remote_url = self._construct_remote_repo_url_with_auth_info()

            # Perform the clone operation
            logger.debug("Goto clone repository from %s to %s.", self.remote_repo_url, self.local_repo_path)
            start_time: float = time.time()
            git.Repo.clone_from(remote_url, self.local_repo_path)
            logger.info("Cloned repository successfully from %s to %s, elapsed time: %.3f seconds.",
                        self.remote_repo_url, self.local_repo_path, time.time() - start_time)
        except git.GitCommandError as e:
            logger.exception("Git clone failed, remote: %s, local: %s. Exception: %s",
                             self.remote_repo_url, self.local_repo_path, e)
            raise e
        except Exception as e:
            logger.error("An unexpected error occurred while cloning, remote: %s, local: %s. Exception: %s",
                         self.remote_repo_url, self.local_repo_path, e)
            raise e

    def pull(self):
        """Pull the latest changes from the remote repository into the local repository."""
        try:
            with git.Repo(self.local_repo_path) as r:
                result = r.git.pull()
                logger.info("Pull from remote git repository success, local repo path: %s.", self.local_repo_path)
                return result  # You can return the result of the pull command if you want to use it elsewhere
        except git.GitCommandError as e:
            logger.error("Git pull failed, local repo path: %s. Error: %s", self.local_repo_path, str(e))
            raise RuntimeError(f"Git pull failed, local repo path: {self.local_repo_path}. Error: {str(e)}")
        except Exception as e:
            logger.error("An unexpected error occurred during git pull, local repo path: %s. Error: %s",
                         self.local_repo_path, str(e))
            raise RuntimeError(f"Unexpected error during git pull, "
                               f"local repo path: {self.local_repo_path}. Error: {str(e)}")

    def sync_from_remote(self, branch_name: str = 'all'):
        """Sync the local repository with the remote repository."""
        try:
            with git.Repo(self.local_repo_path) as r:
                if branch_name == 'all':
                    # Fetch all remote branches
                    r.git.fetch('--all')
                    for branch in r.branches:
                        logger.info("Syncing branch: %s", branch.name)
                        r.git.checkout(branch.name)
                        r.git.reset('--hard', f'origin/{branch.name}')
                else:
                    # Fetch a specific branch
                    r.git.fetch()
                    logger.info("Syncing specific branch: %s", branch_name)
                    r.git.reset('--hard', f'origin/{branch_name}')

            logger.info("Successfully synced with remote repository, local repo: %s, remote: %s",
                        self.local_repo_path, self.remote_repo_url)
        except git.GitCommandError as e:
            logger.error("Git command failed while syncing, repo: %s, branch: %s, error: %s",
                         self.local_repo_path, branch_name, str(e))
            raise RuntimeError(f"Git command failed while syncing, repo: {self.local_repo_path}.")
        except Exception as e:
            logger.error("An unexpected error occurred while syncing, repo: %s, branch: %s, error: %s",
                         self.local_repo_path, branch_name, str(e))
            raise RuntimeError(f"Unexpected error during git sync, repo: {self.local_repo_path}.")

    def discard_local_changes(self) -> Optional[bool]:
        """Discard all local changes, including modified and untracked files."""
        try:
            with git.Repo(self.local_repo_path) as r:
                # 执行 git reset --hard 丢弃所有本地提交的修改
                logger.info("Discarding local changes in repo: %s", self.local_repo_path)
                r.git.reset('--hard')

                # 执行 git clean -fd 删除未跟踪的文件和目录
                logger.info("Cleaning untracked files and directories in repo: %s", self.local_repo_path)
                r.git.clean('-fd')

                logger.info("Successfully discarded local changes in repo: %s", self.local_repo_path)
                return True
        except git.GitCommandError as e:
            logger.error("Git command failed while discarding changes, repo: %s. Error: %s",
                         self.local_repo_path, str(e))
            raise RuntimeError(f"Git command failed while discarding changes, repo: {self.local_repo_path}.")
        except Exception as e:
            logger.error("An unexpected error occurred while discarding changes, repo: %s. Error: %s",
                         self.local_repo_path, str(e))
            raise RuntimeError(f'An unexpected error occurred while discarding changes, repo: {self.local_repo_path}. '
                               f'Error: {str(e)}.')

    @staticmethod
    def _has_changes_to_commit(r: git.Repo) -> bool:
        """Check if there are any changes to commit."""
        # 检查工作区是否有改动
        if r.index.diff("HEAD"):
            return True
        # 检查是否有未跟踪的文件
        if r.untracked_files:
            return True
        return False

    def _has_commit(self, repo: git.Repo) -> bool:
        """Check if the repository has any commits (not empty)."""
        try:
            return len(list(repo.iter_commits())) > 0
        except Exception as e:
            logger.warning("Error checking commits, repo: %s, error: %s", self.local_repo_path, str(e))
            return False

    def _initial_commit(self, repo: git.Repo, msg: str):
        """Perform an initial commit if the repository is empty."""
        try:
            # Add all changes (even though there might not be any)
            repo.git.add(all=True)
            # Commit the changes as the first commit
            repo.index.commit(msg)
            logger.info("First commit created in repo: %s", self.local_repo_path)
        except git.GitCommandError:
            raise RuntimeError(f"Git command failed while creating initial commit, repo: {self.local_repo_path}.")
        except Exception:
            raise RuntimeError(f'Unexpected error during initial commit in repo: {self.local_repo_path}.')

    def commit(self, msg: str, all_files: bool = True) -> bool:
        """Commit changes to the local git repository."""
        try:
            with git.Repo(self.local_repo_path) as r:
                # Check if the repository has any commits (empty repo)
                if not self._has_commit(r):
                    logger.info("No commits yet in repo: %s, performing the first commit.", self.local_repo_path)

                    # Perform the first commit (if repo is empty)
                    self._initial_commit(r, msg)
                else:
                    # Add all files or only tracked files
                    if all_files:
                        logger.info("Adding all files for commit in repo: %s", self.local_repo_path)
                        r.git.add(all=True)
                    else:
                        logger.info("Adding tracked files for commit in repo: %s", self.local_repo_path)
                        r.git.add()

                    # Check if there are changes to commit
                    if not self._has_changes_to_commit(r):
                        logger.info("No changes to commit in repo: %s", self.local_repo_path)
                        return False

                # Perform commit
                r.index.commit(msg)
                logger.info("Commit success: repo path: %s, msg: %s, all files: %s.",
                            self.local_repo_path, msg, all_files)
                return True
        except git.GitCommandError:
            raise RuntimeError(f"Git command failed during commit, repo: {self.local_repo_path}.")
        except Exception:
            raise RuntimeError(f"An unexpected error occurred during commit, repo: {self.local_repo_path}.")

    def _has_remote_branches(self, repo: git.Repo) -> bool:
        """Check if the remote repository has any branches."""
        try:
            # Fetch remote references to see if there are any remote branches
            repo.git.fetch('--all')
            remote_branches = repo.git.branch('-r').splitlines()
            return len(remote_branches) > 0
        except git.GitCommandError:
            raise RuntimeError(f"Git command failed during checking remote branches, repo: {self.local_repo_path}.")
        except Exception:
            raise RuntimeError(f"An unexpected error occurred during checking remote branches, "
                               f"repo: {self.local_repo_path}.")

    def push(self, branch_name: str = 'main'):
        """Push local commits to the remote repository."""
        try:
            with git.Repo(self.local_repo_path) as r:
                logger.info("Pushing changes to remote repository, branch: %s", branch_name)

                # Get the remote named 'origin'
                origin = r.remote(name='origin')

                # Check if remote repository has any branches
                if not self._has_remote_branches(r):
                    logger.info("Remote repository is empty. Creating a new branch and pushing to remote.")

                    # If the remote is empty, we initialize with the current branch
                    push_results = r.git.push('--set-upstream', 'origin', branch_name)
                else:
                    # Push the branch to the remote repository
                    push_results = origin.push(refspec=f'{branch_name}:{branch_name}')
                for result in push_results:
                    if hasattr(result, 'flags'):
                        if result.flags & git.PushInfo.ERROR:
                            logger.error("Push to remote failed: %s", result.summary)
                            raise RuntimeError(f"Git push to remote failed: {result.summary}.")
                    else:
                        logger.warning("Unexpected result type: %s, value: %s.", type(result), result)

            logger.info("Successfully pushed to remote repository, local repo: %s, branch: %s",
                        self.local_repo_path, branch_name)
        except git.GitCommandError:
            raise RuntimeError(f"Git command failed during push, repo: {self.local_repo_path}.")
        except Exception:
            raise RuntimeError(f"An unexpected error occurred during push, repo: {self.local_repo_path}.")

    @staticmethod
    def _get_commit_datetime(commit) -> datetime:
        """Helper function to convert commit's timestamp to datetime in UTC."""
        return datetime.fromtimestamp(commit.committed_date, tz=timezone.utc)

    def get_commit_hash_from_timestamp(self, timestamp: int) -> Optional[str]:
        """Get the commit hash closest to the given timestamp using GitPython."""
        commit_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        try:
            with git.Repo(self.local_repo_path) as r:
                # Dynamically get the active branch name
                active_branch = r.active_branch.name

                commit = self._find_commit_by_timestamp(r, commit_time, active_branch)
                if commit:
                    logger.info(f"Found commit at {self._get_commit_datetime(commit)} for timestamp {timestamp}")
                    return commit.hexsha
                else:
                    logger.warning("No commit found for the given timestamp.")
                    return None
        except git.GitCommandError:
            raise RuntimeError(f"Git command failed while fetch commit hash, repo: {self.local_repo_path}.")
        except Exception:
            raise RuntimeError(f"An unexpected error occurred while fetch commit hash, repo: {self.local_repo_path}.")

    def _find_commit_by_timestamp(self, repo: git.Repo, commit_time: datetime, branch_name: str):
        """Find the closest commit to the given timestamp."""
        for commit in repo.iter_commits(branch_name, since=commit_time):
            commit_datetime = self._get_commit_datetime(commit)
            if commit_datetime <= commit_time:
                return commit
        return None

    def get_diff_between_timestamps(self, time_duration: TimeDuration) -> Optional[str]:
        """Get the diff between two timestamps and return it as a formatted string."""
        try:
            commit_hash_1 = self.get_commit_hash_from_timestamp(int(time_duration.start_timestamp_second))
            commit_hash_2 = self.get_commit_hash_from_timestamp(int(time_duration.end_timestamp_second))

            if not commit_hash_1 or not commit_hash_2:
                logger.error("Failed to get commit hashes for the given timestamps.")
                return None

            with git.Repo(self.local_repo_path) as r:
                diff = r.git.diff(commit_hash_1, commit_hash_2)
            return diff
        except git.GitCommandError:
            raise RuntimeError(f"Git command failed, repo: {self.local_repo_path}.")
        except Exception:
            raise RuntimeError(f"An unexpected error occurred, repo: {self.local_repo_path}.")

    def load_tracked_diff(self, with_header: bool = False) -> Optional[str]:
        return GitUtil.load_tracked_diff(self.local_repo_path, with_header)

    def load_untracked_diff(self, with_header: bool = False) -> Optional[str]:
        return GitUtil.load_untracked_diff(self.local_repo_path, with_header)


if __name__ == "__main__":
    sys.exit(0)
