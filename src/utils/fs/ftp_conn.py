#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: FTP Utility Class Source Code.
"""
import os.path
from ftplib import FTP, error_perm

from utils.base_util import BaseUtil


class FtpServerInfo:
    def __init__(self, host: str, user: str, passwd: str):
        self.host: str = host
        self.user: str = user
        self.passwd: str = passwd

    @staticmethod
    def is_empty(server_info) -> bool:
        if BaseUtil.is_empty(server_info):
            return True
        if BaseUtil.is_empty(server_info.host) and \
                BaseUtil.is_empty(server_info.user) and \
                BaseUtil.is_empty(server_info.passwd):
            return True
        return False


class FtpUtil:
    DEFAULT_CONNECT_TIMEOUT_SEC = 3

    @staticmethod
    def list_dirs_from_ftp(ftp, path) -> list[str]:
        # 改变工作目录到指定路径
        ftp.cwd(path)

        # 获取指定路径下的文件和目录列表
        items = ftp.nlst()

        # 过滤掉非目录的项
        directories = []
        for item in items:
            try:
                # 尝试改变工作目录到该项，以此判断其是否为目录
                ftp.cwd(item)
                directories.append(item)
                # 返回上一级目录
                ftp.cwd('..')
            except error_perm:
                # 如果不是目录，则忽略异常继续
                continue

        return directories

    @staticmethod
    def list_files_ftp(server: str, username: str, password: str, directory: str = None) -> None:
        # 连接到FTP服务器
        ftp = FTP(server)
        ftp.login(user=username, passwd=password)

        # 切换到指定目录
        ftp.cwd(directory)

        # 获取文件列表
        files = []
        ftp.dir(files.append)

        # 打印文件信息
        for file_info in files:
            print(file_info)

        # 关闭连接
        ftp.quit()

    @staticmethod
    def is_item_exist(server: FtpServerInfo, path: str) -> bool:
        # 连接到FTP服务器
        f = FTP(host=server.host, timeout=FtpUtil.DEFAULT_CONNECT_TIMEOUT_SEC)
        f.login(user=server.user, passwd=server.passwd)

        # 切换到指定目录
        item_dir = os.path.dirname(path)
        f.cwd(item_dir)

        # 获取文件列表
        files = f.nlst()

        # 关闭连接
        f.quit()

        item_name = os.path.basename(path)
        return item_name in files


if __name__ == '__main__':
    print("Hello world!")
    ftp_server = '10.106.160.185'
    ftp_username = 'arrayadm'
    ftp_password = 'Array@dm'
    ftp_directory = 'data'
    FtpUtil.list_files_ftp(ftp_server, ftp_username, ftp_password, ftp_directory)
    exit(0)
