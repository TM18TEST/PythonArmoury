#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Json Profile Parser Base Class.
"""
import json
import os
from typing import Optional

from utils.fs.fs_util import FsUtil
from utils.log_ins import LogUtil

logger = LogUtil.get_logger()


class JsonParser:
    """
    Json Profile Parser Base Class.
    """

    def __init__(self, profile_path: str = None, default_profile_name: str = None):
        # Declare some variables of current instance
        self._profile_path: str = profile_path
        self._default_profile_name: str = default_profile_name

        # Update profile path then parse parameter(s) from it
        self._update_profile_path()
        self._parse_profile()

    @staticmethod
    def get_default_profile_path(default_profile_name: str) -> Optional[str]:
        """
        Locate the default profile file path.

        Returns:
            Optional[str]: The path to the default profile if found, otherwise None.
        """
        # Check current directory for the profile
        current_dir_profile = os.path.join(FsUtil.get_current_dir(), default_profile_name)
        if os.path.isfile(current_dir_profile):
            return current_dir_profile

        # Check default resource/config directory for the profile
        default_dir_profile = os.path.join(FsUtil.get_process_root_path(), "resource", "config", default_profile_name)
        if os.path.isfile(default_dir_profile):
            return default_dir_profile

        raise FileNotFoundError(f"Unable to locate the default profile: {current_dir_profile}, {default_dir_profile}.")

    def _update_profile_path(self) -> None:
        """
        Update the profile path by checking the input and default paths.

        Raises:
            FileNotFoundError: If no valid profile path can be determined.
        """
        if self._profile_path:
            logger.info("Using input profile, path: %s.", self._profile_path)
            return

        self._profile_path = self.get_default_profile_path(self._default_profile_name)
        logger.info("Using profile: %s.", self._profile_path)

    def _do_parsr_profile_content(self, json_data) -> None:
        pass

    def _parse_profile(self) -> None:
        """
        Parse parameter(s) from specified profile file.

        Raises:
            FileNotFoundError: If the profile file is not found.
            IOError: If the profile file cannot be accessed.
            ValueError: If the profile format is invalid.
            KeyError: If required keys are missing in the JSON.
        """
        try:
            with open(self._profile_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)

            # Do parse parameter(s) from specified profile file
            self._do_parsr_profile_content(json_data)

        except FileNotFoundError as e:
            logger.exception(f"Cannot find the profile: {self._profile_path}. Error: {e}")
            raise
        except IOError as e:
            logger.exception(f"Cannot access the profile: {self._profile_path}. Error: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.exception(f"Invalid format in the profile: {self._profile_path}. Error: {e}")
            raise
        except KeyError as e:
            logger.exception(f"Missing required key in the profile JSON, profile: {self._profile_path}. Error: {e}")
            raise
