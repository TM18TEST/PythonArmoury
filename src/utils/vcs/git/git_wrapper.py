#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: General Gti Archiver Base Class.
"""
import os
import shutil
import git

from datetime import datetime

from utils.vcs.git.committer.git_committer import GitCommitter
from utils.fs.fs_util import FsUtil
from utils.vcs.git_repo import GitRepo
from utils.vcs.git_util import GitUtil
from utils.log_ins import LogUtil

logger = LogUtil.get_logger()


class GitWrapper:
    @staticmethod
    def clear_git_repository_except_metadata(dir_path: str) -> None:
        """
        Deletes all entries in the specified directory except `.git` directories and `.gitignore` files.

        :param dir_path: The directory path to clean.
        """
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory does not exist: {dir_path}")

        try:
            for entry in os.scandir(dir_path):
                if entry.is_dir():
                    # Keep .git folder
                    if entry.name == ".git":
                        continue
                    FsUtil.force_remove(entry.path)
                elif entry.is_file():
                    # Keep .gitignore files
                    if entry.name == ".gitignore":
                        continue
                    FsUtil.force_remove(entry.path)
        except Exception as e:
            logger.exception(f"Error while cleaning directory: %s. Exception: %s.", dir_path, e)

    @staticmethod
    def init_repo(repo_path: str, repo_url: str = None,
                  repo_username: str = None, repo_password: str = None) -> bool:
        """
        Initialize or clone a Git repository.

        Args:
            repo_path (str): The local directory for the Git repository.
            repo_url (str): The URL of the remote repository. Optional.
            repo_username (str): The username for accessing the remote repository. Optional.
            repo_password (str): The password for accessing the remote repository. Optional.

        Returns:
            bool: True if the repository was initialized or cloned, False if it already exists.
        """
        # Check if the path is already a Git repository
        if GitUtil.is_git_repository(repo_path):
            logger.info("The directory is already a Git repository: %s", repo_path)
            return False

        # Ensure the directory exists
        try:
            os.makedirs(repo_path, exist_ok=True)
        except OSError as e:
            logger.error("Failed to create directory: %s. Error: %s", repo_path, e)
            raise

        # Attempt to clone from a remote repository if all parameters are provided
        if repo_url and FsUtil.is_empty_dir(repo_path):
            if repo_username and repo_password:
                try:
                    r = GitRepo(local_repo_path=repo_path,
                                remote_repo_url=repo_url,
                                username=repo_username,
                                password=repo_password)
                    r.clone()
                    return True
                except Exception as e:
                    logger.error("Failed to clone repository from %s. Error: %s", repo_url, e)
                    raise
            else:
                logger.warning("Missing credentials for cloning repository: %s", repo_url)

        # Initialize a local repository
        logger.info("Initializing a new Git repository at: %s", repo_path)
        try:
            git.Repo.init(repo_path)
            logger.info("Successfully initialized Git repository at: %s", repo_path)
            return True
        except git.exc.GitError as e:
            logger.error("Failed to initialize Git repository: %s. Error: %s", repo_path, e)
            raise

    @staticmethod
    def commit(repo_path: str, group_commits: bool, commit_msg: str = None,
               exclude_files: list[str] = None, exclude_dirs: list[str] = None,
               author_name: str = None, author_email: str = None) -> int:
        """
        Commit changes to a Git repository with optional exclusions and grouped commits.

        Args:
            repo_path (str): Path to the local Git repository.
            group_commits (bool): Whether to group commits by time interval.
            commit_msg (str): Commit message. Defaults to a timestamped message.
            exclude_files (list[str]): List of files to exclude from the commit. Optional.
            exclude_dirs (list[str]): List of directories to exclude from the commit. Optional.
            author_name (str): Author name for commit.
            author_email (str): Author E-Mail for commit.

        Returns:
            int: Number of commits made.

        Raises:
            Exception: If commit operation fails.
        """
        # Use default commit message if not provided
        if not commit_msg:
            commit_msg = "Automatic archive by tool: {}.".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

        # Initialize exclusions if None
        exclude_files = exclude_files or []
        exclude_dirs = exclude_dirs or []

        try:
            # Commit changes using GitCommitter
            with GitCommitter(repo_path) as g:
                # Set exclusions if provided
                if exclude_files or exclude_dirs:
                    g.set_exclusions(exclude_dirs, exclude_files)
                    logger.debug("Exclusions set. Files: %s, Directories: %s", exclude_files, exclude_dirs)

                # Enable grouped commits if requested
                if group_commits:
                    g.set_group_time_interval(GitCommitter.DEFAULT_TIME_INTERVAL_SEC)
                    logger.debug("Grouped commits enabled with interval: %d seconds",
                                 GitCommitter.DEFAULT_TIME_INTERVAL_SEC)

                # Perform the commit
                commit_num: int = g.commit_changes(commit_msg, author_name, author_email)
                if commit_num > 0:
                    logger.info("Commit successful: '%s', number of commits: %d, repo path: %s",
                                commit_msg, commit_num, repo_path)
                else:
                    logger.info("Unnecessary to commit because there is no changes, repo path: %s", repo_path)
                return commit_num

        except Exception as e:
            # Log and raise exceptions for failed commits
            logger.error("Commit failed. Repo path: %s, Error: %s", repo_path, e)
            raise

    @staticmethod
    def _has_any_remote_branch(repo: git.Repo) -> bool:
        """
        Check if there is at least one remote branch in the repository.

        Args:
            repo (git.Repo): The Git repository object.

        Returns:
            bool: True if any remote branch exists, False otherwise.

        Raises:
            RuntimeError: If a Git command fails or another error occurs.
        """
        try:
            # Access remote references directly
            for ref in repo.remote().refs:
                logger.debug("Found remote branch: %s", ref.name)
                return True  # Stop as soon as we find one branch
            logger.debug("No remote branches found in repository: %s", repo.working_tree_dir)
            return False

        except git.GitCommandError as e:
            logger.error("Git command failed while checking remote branches, repo: %s. Error: %s",
                         repo.working_tree_dir, e)
            raise RuntimeError(
                f"Git command failed during checking remote branches, repo: {repo.working_tree_dir}.") from e

        except Exception as e:
            logger.error("Unexpected error occurred while checking remote branches, repo: %s. Error: %s",
                         repo.working_tree_dir, e)
            raise RuntimeError(f"An unexpected error occurred during checking remote branches, "
                               f"repo: {repo.working_tree_dir}.") from e

    @staticmethod
    def push(repo_path: str, branch_name: str = 'main'):
        """Push local commits to the remote repository.

        This method pushes the local commits to the specified remote repository.
        If the remote repository does not contain any branches, it will create a new branch and push it.
        Otherwise, it will push the local branch to the corresponding remote branch.

        Args:
            repo_path (str): The local path to the Git repository.
            branch_name (str, optional): The branch name to push. Defaults to 'main'.

        Raises:
            RuntimeError: If the Git command fails during the push operation.
            RuntimeError: If an unexpected error occurs during the push operation.

        Example:
            GitUtil.push(repo_path="/path/to/local/repo", branch_name="main")

        This will push the local 'main' branch to the 'origin' remote repository.
        """
        try:
            with git.Repo(repo_path) as r:
                logger.info("Pushing changes to remote repository, branch: %s", branch_name)

                # Get the remote named "origin"
                origin = r.remote(name="origin")

                # Check if remote repository has any branches
                if not GitWrapper._has_any_remote_branch(r):
                    logger.info("Remote repository is empty. Creating a new branch and pushing to remote.")

                    # If the remote is empty, we initialize with the current branch
                    push_results = r.git.push("--set-upstream", "origin", branch_name)
                else:
                    # Push the branch to the remote repository
                    push_results = origin.push(refspec=f"{branch_name}:{branch_name}")
                for result in push_results:
                    if hasattr(result, "flags"):
                        if result.flags & git.PushInfo.ERROR:
                            logger.error("Push to remote failed: %s", result.summary)
                            raise RuntimeError(f"Git push to remote failed: {result.summary}.")
                    else:
                        logger.debug("Unexpected result type: %s, value: %s.", type(result), result)

            logger.info("Successfully pushed to remote repository, local repo: %s, branch: %s",
                        repo_path, branch_name)
        except git.GitCommandError:
            raise RuntimeError(f"Git command failed during push, repo: {repo_path}.")
        except Exception:
            raise RuntimeError(f"An unexpected error occurred during push, repo: {repo_path}.")
