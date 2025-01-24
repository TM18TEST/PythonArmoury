#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Hash Utility Class Source Code.
"""
import hashlib
import os


class HashUtil:
    @staticmethod
    def calculate_file_hash_digest(file_path: str, hash_algorithm='md5') -> bytes:
        """
        Calculate the hash value of the entire file.

        Args:
            file_path (str): The path of the file to be hashed.
            hash_algorithm (str, optional): The hashing algorithm to use (default is 'md5').

        Returns:
            bytes: The resulting hash value of the entire file.

        Raises:
            ValueError: If the specified file does not exist.
        """
        if not os.path.isfile(file_path):
            raise ValueError(f"The specified path is not a file: {file_path}")

        # Hash the content of each file
        with open(file_path, 'rb', encoding="utf-8") as f:
            file_hash = hashlib.new(hash_algorithm)
            while chunk := f.read(8192):  # Read file in chunks
                file_hash.update(chunk)
            # Return the final hash as digest bytes
            return file_hash.digest()

    @staticmethod
    def calculate_file_hash(file_path: str, hash_algorithm='md5') -> str:
        """
        Calculate the hash value of the entire file.

        Args:
            file_path (str): The path of the file to be hashed.
            hash_algorithm (str, optional): The hashing algorithm to use (default is 'md5').

        Returns:
            str: The resulting hash value of the entire file.

        Raises:
            ValueError: If the specified file does not exist.
        """
        if not os.path.isfile(file_path):
            raise ValueError(f"The specified path is not a file: {file_path}")

        # Hash the content of each file
        with open(file_path, 'rb') as file:
            file_hash = hashlib.new(hash_algorithm)
            while chunk := file.read(8192):  # Read file in chunks
                file_hash.update(chunk)
            # Return the final hash as a hexadecimal string
            return file_hash.hexdigest()

    @staticmethod
    def calculate_directory_hash(dir_path: str, hash_algorithm='md5') -> str:
        """
        Calculate the hash value of the entire directory, including all files and subdirectories.

        Args:
            dir_path (str): The path of the directory to be hashed.
            hash_algorithm (str, optional): The hashing algorithm to use (default is 'md5').

        Returns:
            str: The resulting hash value of the entire directory.

        Raises:
            ValueError: If the specified directory does not exist.
        """
        if not os.path.isdir(dir_path):
            raise ValueError(f"The specified path is not a directory: {dir_path}")

        # Create a hash object
        hash_func = hashlib.new(hash_algorithm)

        # Collect all files in the directory recursively
        for dir_path, dir_names, filenames in os.walk(dir_path):
            for filename in sorted(filenames):  # Sort files to ensure consistent hash order
                file_path = os.path.join(dir_path, filename)
                # Hash the content of each file
                file_hash_digest = HashUtil.calculate_file_hash_digest(file_path, hash_algorithm)
                # Update the overall directory hash with the file hash
                hash_func.update(file_hash_digest)

        # Return the final hash as a hexadecimal string
        return hash_func.hexdigest()
