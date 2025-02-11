#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: SMB Client Class Source Code.
"""
import os.path
import sys

import smbclient
import smbclient.shutil

from utils.base_util import BaseUtil
from utils.log_ins import LogUtil

logger = LogUtil.get_logger()


class SmbClient:
    """SMB client class"""

    def __init__(self, server: str, username: str, password: str):
        """Initialize the SmbClient object.

        Args:
            server (str): The address of the SMB server.
            username (str): Username to connect to the SMB server.
            password (str): Password to connect to the SMB server.
        """
        if BaseUtil.is_empty(server):
            raise ValueError(f"Null input server address")
        self._server: str = server
        self._username: str = username
        self._password: str = password
        self._session = None
        logger.debug("Construct SMB client success, server: %s, user: %s.", self._server, self._username)

    def __enter__(self):
        """Initialize the connection when entering the context.

        return:
            SmbClient: The current SmbClient instance for use in `with` statements.
        """
        # Register session (authentication is handled automatically)
        self._session = smbclient.register_session(server=self._server,
                                                   username=self._username, password=self._password)
        logger.debug("Connected to SMB server success, server: %s, user: %s.", self._server, self._username)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the connection and handle exceptions when exiting the context.

        Args:
            exc_type (type): Exception type.
            exc_value (Exception): Exception instance.
            traceback (traceback): Exception tracking information.

        return:
            bool: Returning True means the exception has been handled, False means the exception will be rethrown.
        """
        try:
            if self._session is not None:
                smbclient.delete_session(server=self._server)
                self._session = None
                logger.debug("Delete SMB connection success, server: %s, user: %s.", self._server, self._username)
        except Exception as e:
            logger.exception("Failed to delete SMB connection, server: %s, user: %s. Exception: %s.",
                             self._server, self._username, e)

        # Exception handling:
        #   If an exception occurs, return True to indicate that the exception will no longer be thrown.
        if exc_type:
            logger.error("An exception occurred: %s - %s", exc_type, exc_value)
        return False  # Returns False, indicating that the exception will be rethrown

    def _gen_absolute_path(self, relative_path: str) -> str:
        return rf"\\{self._server}\{relative_path}"

    def is_exist(self, relative_path: str) -> bool:
        return smbclient.path.exists(self._gen_absolute_path(relative_path))

    def is_file(self, relative_path: str) -> bool:
        return smbclient.path.isfile(self._gen_absolute_path(relative_path))

    def is_dir(self, relative_path: str) -> bool:
        return smbclient.shutil.isdir(self._gen_absolute_path(relative_path))

    def scan_dir(self, relative_path: str) -> list[str]:
        entries_name: list[str] = []
        for entry in smbclient.scandir(self._gen_absolute_path(relative_path)):
            entries_name.append(entry.name)
        return entries_name

    def list_files_in_dir(self, relative_path: str) -> list[str]:
        entries_name: list[str] = []
        for entry in smbclient.scandir(self._gen_absolute_path(relative_path)):
            if entry.is_file():
                entries_name.append(entry.name)
        return entries_name

    def list_dirs_in_dir(self, relative_path: str) -> list[str]:
        entries_name: list[str] = []
        for entry in smbclient.scandir(self._gen_absolute_path(relative_path)):
            if entry.is_dir():
                entries_name.append(entry.name)
        return entries_name

    def download_file(self, remote_relative_path: str, local_dir_path: str) -> None:
        remote_absolute_path: str = self._gen_absolute_path(remote_relative_path)
        smbclient.shutil.copy2(remote_absolute_path,
                               os.path.join(local_dir_path, os.path.basename(remote_absolute_path)))

    def upload_file(self, local_absolute_path: str, remote_dir_relative_path: str) -> None:
        remote_absolute_path: str = os.path.join(self._gen_absolute_path(remote_dir_relative_path),
                                                 os.path.basename(local_absolute_path))
        smbclient.shutil.copy2(local_absolute_path, remote_absolute_path)


if __name__ == "__main__":
    with SmbClient("10.105.140.174", "Administrator", "Tm18CimRCS@63.") as c:
        print(c.upload_file(r"D:\Data\Temp\RONS2_PowerOff_Test.txt", "share"))
    sys.exit(0)
