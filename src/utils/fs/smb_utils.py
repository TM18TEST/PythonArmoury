#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""

import os
import socket
import sys
from smb.SMBConnection import SMBConnection

from utils.base_util import BaseUtil
from utils.fs.fs_util import FsUtil
from utils.log_ins import LogUtil

logger = LogUtil.get_logger()


class SmbConn:
    """SMB connection management class provides file download and resource management functions.


    This class connects to a remote server via the SMB protocol
        and provides recursive downloading of files and directories.
    The connection is managed through the context manager to ensure automatic cleaning of resources and avoid leakage.
    """

    def __init__(self, ip: str, user: str, password: str, service_name: str, remote_name: str = None):
        """Initialize the SmbConn object.

        Args:
            ip (str): The IP address of the SMB server.
            user (str): Username to connect to the SMB server.
            password (str): Password to connect to the SMB server.
            service_name (str): Service name, that is, shared directory name.
            remote_name (str): The device name of the SMB server.
        """
        self.ip: str = ip
        self.user: str = user
        self.password: str = password
        self.service_name: str = service_name
        self.conn: SMBConnection | None = None

        # Device name
        self.remote_name: str = remote_name
        if BaseUtil.is_empty(self.remote_name):
            host_name, _, _ = socket.gethostbyaddr(self.ip)
            self.remote_name = host_name.split('.')[0]
            logger.info("Remote name is empty, use obtained host name: %s.", self.remote_name)
        logger.debug("Construct SMB connection success, ip: %s, user: %s.", ip, user)

    def __enter__(self):
        """Initialize the connection when entering the context.

        return:
            SmbConn: The current SmbConn instance for use in `with` statements.
        """
        self.conn = SMBConnection(self.user, self.password, '', self.remote_name, use_ntlm_v2=True)
        if not self.conn.connect(self.ip):
            logger.error("Unable to connect to SMB server, ip: %s, user: %s.", self.ip, self.user)
            raise ConnectionError("Unable to connect to SMB server")
        logger.debug("Connected to SMB server success, ip: %s, user: %s.", self.ip, self.user)
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
            if self.conn:
                self.conn.close()
                logger.debug("Closed SMB connection success, ip: %s, user: %s.", self.ip, self.user)
        except Exception as ex:
            logger.error("Failed to close SMB connection, ip: %s, user: %s, error: %s.", self.ip, self.user, str(ex))

        # Exception handling:
        #   If an exception occurs, return True to indicate that the exception will no longer be thrown.
        if exc_type:
            logger.error("An exception occurred: %s - %s", exc_type, exc_value)
        return False  # Returns False, indicating that the exception will be rethrown

    def download(self, remote_path: str, local_path: str) -> None:
        """Recursively download files and directories within an SMB share.

        This method will recursively traverse the remote directory,
            download the file and save it locally, while retaining the timestamp of the file.

        Args:
            remote_path (str): Remote path.
            local_path (str): Local path.

        Raises:
            Exception: If any error occurs during downloading, exception is thrown.
        """
        try:
            entries = self.conn.listPath(self.service_name, remote_path)  # List remote directory contents
            for entry in entries:
                if entry.isDirectory:
                    # Ignore special directories
                    if entry.filename in ['.', '..']:
                        continue

                    # Handle subdirectories
                    new_local_dir = os.path.join(local_path, entry.filename)
                    os.makedirs(new_local_dir, exist_ok=True)
                    logger.debug("Entering directory: %s", entry.filename)
                    self.download(f"{remote_path}/{entry.filename}", new_local_dir)
                else:
                    # Download file
                    local_file_path = os.path.join(local_path, entry.filename)
                    with open(local_file_path, 'wb') as local_file:
                        # Use retrieveFile to download the file and make sure the file has not been modified
                        self.conn.retrieveFile(self.service_name, f"{remote_path}/{entry.filename}", local_file)

                    # Set file time attributes
                    FsUtil.set_file_times(local_file_path, entry.create_time,
                                          entry.last_write_time, entry.last_access_time)
                    logger.debug("Downloaded and set times for the file success: %s", entry.filename)
        except Exception as ex:
            logger.error("Failed to download from SMB server, remote_path: %s, error: %s", remote_path, str(ex))
            raise


if __name__ == "__main__":
    try:
        # Create and use SmbConn objects using context managers
        with SmbConn(ip='192.168.3.200', user='admin', password='', service_name='Share2') as s:
            s.download('Temp\\计算机基本组件认识', 'I:\\Tmp\\smb')
    except Exception as e:
        logger.error(f"Download failed: {e}")
    sys.exit(0)
