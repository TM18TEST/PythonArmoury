#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: SMB Utility Class Source Code.
"""

import os
import shutil
import socket
import sys
from typing import Optional
from smb.SMBConnection import SMBConnection

from utils.base_util import BaseUtil
from utils.fs.fs_util import FsUtil
from utils.log_ins import LogUtil
from utils.vcs.git_repo import GitRepo

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
        self.conn: Optional[SMBConnection] = None

        # Device name
        self.remote_name: str = remote_name
        if BaseUtil.is_empty(self.remote_name):
            try:
                host_name, _, _ = socket.gethostbyaddr(self.ip)
            except Exception as e:
                logger.exception("Failed to get host name by IP address, ip: %s. Exception: %s.", ip, e)
                host_name = ''
            self.remote_name = host_name.split('.')[0]
            logger.info("Remote host name is empty, use obtained host name: %s.", self.remote_name)
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
        except Exception as e:
            logger.exception("Failed to close SMB connection, ip: %s, user: %s. Exception: %s.",
                             self.ip, self.user, e)

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
        except Exception as e:
            logger.exception("Failed to download from SMB server, remote_path: %s. Exception: %s", remote_path, e)
            raise


def _simple_smb_server_test():
    server_list: list[tuple[str, str]] = [
        ("A1REP0120", "10.106.73.74"),
        ("A1REP0130", "10.106.73.73"),
        ("A1REP0220", "10.106.73.181"),
        ("A1REP0320", "10.106.73.72"),
        ("A1REP0330", "10.106.73.71"),
        ("A1REP0420", "10.106.73.115"),
        ("A1REP0430", "10.106.73.114"),
        ("A1REP0520", "10.106.73.113"),
        ("A1REP0530", "10.106.73.112"),
        ("A1REP0620", "10.106.73.111"),
        ("A1REP0720", "10.106.73.182"),
        ("A1REP0730", "10.106.73.183"),
        ("A1REP0820", "10.106.73.184"),
        ("A1REP0830", "10.106.73.185"),
        ("P1REP0120", "10.106.72.36"),
        ("P1REP0130", "10.106.72.35"),
        ("P1REP0400", "10.106.73.186"),
    ]
    success_list: list[str] = []
    fail_list: list[str] = []
    for name, ip in server_list:
        try:
            host_name, _, _ = socket.gethostbyaddr(ip)
            remote_name = host_name.split('.')[0]
            logger.info("Get host name success: %s -%s.", name, remote_name)
        except Exception as exp:
            logger.exception("Get host name failed: %s, exp: %s.", ip, str(exp))
            remote_name = name

        try:
            conn = SMBConnection("VTEC", "VTEC", '', remote_name, use_ntlm_v2=True)
            if not conn.connect(ip, timeout=1):
                logger.error("Unable to connect to SMB server, ip: %s, server: %s.", ip, name)
                fail_list.append(name + " " + ip)
                continue
            conn.close()
        except Exception as exp:
            logger.exception("Connect failed: %s, exp: %s.", ip, str(exp))
            fail_list.append(name + " " + ip)
            continue
        logger.info("Connected to SMB server success, ip: %s, server: %s.", ip, name)
        success_list.append(name + " " + ip)
    logger.info("success list: %s, \r\nfail list: %s.", success_list, fail_list)


if __name__ == "__main__":
    """
    try:
        # Create and use SmbConn objects using context managers
        with SmbConn(ip='192.168.3.200', user='admin', password='', service_name='Share2') as s:
            s.download('Temp\\计算机基本组件认识', 'I:\\Tmp\\smb')
    except Exception as e:
        logger.error(f"Download failed: {e}")
    sys.exit(0)
    """

    paths: list[tuple[str, str]] = [
        ('10.106.73.74', 'a1rep0120'),
        ('10.106.73.73', 'a1rep0130'),
        ('10.106.73.181', 'a1rep0220'),
        ('10.106.73.72', 'a1rep0320'),
        ('10.106.73.71', 'a1rep0330'),
        ('10.106.73.115', 'a1rep0420'),
        ('10.106.73.114', 'a1rep0430'),
        ('10.106.73.113', 'a1rep0520'),
        ('10.106.73.112', 'a1rep0530'),
        ('10.106.73.111', 'a1rep0620'),
        ('10.106.73.182', 'a1rep0720'),
        ('10.106.73.183', 'a1rep0730'),
        ('10.106.73.184', 'a1rep0820'),
        ('10.106.73.185', 'a1rep0830'),
        ('10.106.72.36', 'p1rep0120'),
        ('10.106.72.35', 'p1rep0130'),
    ]
    for ip_addr, identify in paths:
        local_pah: str = os.path.join('E:\\Recipes\\VTecRep3', identify)
        FsUtil.force_remove(local_pah, not_exist_ok=True)
        os.makedirs(local_pah, exist_ok=True)
        repo = GitRepo(
            local_repo_path=local_pah,
            remote_repo_url=f'http://192.168.1.2:3000/recipe/{identify}.git',
            username='tool',
            password='11111111'
        )
        repo.clone()
        shutil.copytree(f'\\\\{ip_addr}\\env\\Recipe\\', local_pah, dirs_exist_ok=True)
        logger.info("%s %s", ip_addr, identify)
    sys.exit(0)
