#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Compress Utility Class.
"""
import mimetypes
import os
import tarfile
import zipfile


class CompressUtil:
    @staticmethod
    def check_zip_file(path: str) -> None:
        with zipfile.ZipFile(path, 'r') as f:
            bad_file = f.testzip()
            if bad_file:
                raise zipfile.BadZipFile(f"Bad files: {bad_file}")

    @staticmethod
    def check_compressed_file(path: str, compress_fmt: str = "zip") -> None:
        if compress_fmt == "zip":
            return CompressUtil.check_zip_file(path)
        raise NotImplementedError(f"Not implemented compressed format: {compress_fmt}")

    @staticmethod
    def compress(input_path: str, output_path: str, fmt: str = "zip", level: int = 5) -> None:
        """
        Compress a file or folder
        :param input_path: File or folder path to compress
        :param output_path: Generated compressed file path
        :param fmt: Compression format, supports "zip", "tar.gz", "tar.bz2", "tar.xz"
        :param level: Compression level (zip: 0[No compression] - 9[Maximum compression])
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input path does not exist: {input_path}")

        if fmt == "zip":
            try:
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=level) as f:
                    if os.path.isdir(input_path):
                        for root, _, files in os.walk(input_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                f.write(file_path, os.path.relpath(file_path, input_path))
                    else:
                        f.write(input_path, os.path.basename(input_path))
            except Exception as e:
                raise RuntimeError(f"Failed to create zip file: {e}")
        elif fmt in ["tar.gz", "tar.bz2", "tar.xz"]:
            mode = "w:" + fmt.split(".")[-1]  # Parse format
            try:
                with tarfile.open(output_path, mode) as f:
                    f.add(input_path, arcname=os.path.basename(input_path))
            except Exception as e:
                raise RuntimeError(f"Failed to create tar file: {e}")
        else:
            raise NotImplementedError("Unsupported format! Use 'zip', 'tar.gz', 'tar.bz2', or 'tar.xz'.")

    @staticmethod
    def decompress(input_path: str, output_dir: str) -> None:
        """
        Decompress the file
        :param input_path: Compressed file path
        :param output_dir: Decompress target directory
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input path does not exist: {input_path}")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        mime_type, _ = mimetypes.guess_type(input_path)
        if mime_type in ["application/zip", "application/x-zip-compressed"]:
            try:
                with zipfile.ZipFile(input_path, 'r') as zipf:
                    zipf.extractall(output_dir)
            except Exception as e:
                raise RuntimeError(f"Failed to extract zip file: {e}")

        elif mime_type in ["application/x-tar", "application/gzip", "application/x-bzip2", "application/x-xz"]:
            try:
                with tarfile.open(input_path, 'r:*') as tarf:
                    tarf.extractall(output_dir)
            except Exception as e:
                raise RuntimeError(f"Failed to extract tar file: {e}")
        else:
            raise NotImplementedError(f"Unsupported format: {mime_type}! Use 'zip', 'tar.gz', 'tar.bz2', or 'tar.xz'.")
