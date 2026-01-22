#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
from typing import Optional, List, Dict

import win32cred
import pywintypes


class WindowsCredentialManager:
    """
    A robust Windows Credential Manager wrapper for SMB credentials.

    This class provides CRUD operations for Windows credentials and
    optional SMB session cleanup to avoid credential/session conflicts.
    """

    CRED_TYPE = win32cred.CRED_TYPE_GENERIC
    CRED_PERSIST = win32cred.CRED_PERSIST_LOCAL_MACHINE

    # =========================
    # Public API
    # =========================

    def list_credentials(self) -> List[Dict]:
        """
        List all Windows credentials.

        Returns:
            List of credential metadata dictionaries.
        """
        try:
            credentials = win32cred.CredEnumerate(None, 0)
        except pywintypes.error:
            return []

        result = []
        for cred in credentials:
            result.append({
                "TargetName": cred.get("TargetName"),
                "UserName": cred.get("UserName"),
                "Type": cred.get("Type"),
                "Persist": cred.get("Persist"),
            })
        return result

    def get_credential(self, target: str) -> Optional[Dict]:
        """
        Get a specific credential by target name.

        Args:
            target: Credential target (e.g. \\192.168.1.10)

        Returns:
            Credential dictionary or None if not found.
        """
        try:
            cred = win32cred.CredRead(target, self.CRED_TYPE, 0)
        except pywintypes.error:
            return None

        return {
            "TargetName": cred.get("TargetName"),
            "UserName": cred.get("UserName"),
            "Password": self._decode_password(cred.get("CredentialBlob")),
            "Persist": cred.get("Persist"),
        }

    def add_or_update_credential(
        self,
        target: str,
        username: str,
        password: str,
        reset_smb_session: bool = True,
    ) -> None:
        """
        Add or update a Windows credential.

        This operation is idempotent: existing credentials with the same
        target will be overwritten.

        Args:
            target: SMB server target (e.g. \\192.168.1.10)
            username: Username (DOMAIN\\user or HOST\\user)
            password: Password
            reset_smb_session: Whether to drop existing SMB sessions first
        """
        if reset_smb_session:
            self.reset_smb_access(target)

        credential = {
            "Type": self.CRED_TYPE,
            "TargetName": target,
            "UserName": username,
            "CredentialBlob": password.encode("utf-16-le"),
            "Persist": self.CRED_PERSIST,
        }

        win32cred.CredWrite(credential, 0)

    def delete_credential(
        self,
        target: str,
        reset_smb_session: bool = True,
    ) -> None:
        """
        Delete a Windows credential.

        Args:
            target: Credential target
            reset_smb_session: Whether to drop existing SMB sessions first
        """
        if reset_smb_session:
            self.reset_smb_access(target)

        try:
            win32cred.CredDelete(target, self.CRED_TYPE, 0)
        except pywintypes.error:
            # Deleting a non-existing credential is safe (idempotent behavior)
            pass

    def reset_smb_access(self, target: str) -> None:
        """
        Forcefully remove existing SMB connections to avoid credential conflicts.

        This is critical when switching users for the same SMB server.

        Args:
            target: SMB server target
        """
        self._net_use_delete(target)

    # =========================
    # Internal helpers
    # =========================

    @staticmethod
    def _decode_password(blob: Optional[bytes]) -> Optional[str]:
        """
        Decode Windows credential password blob.

        Args:
            blob: Raw credential blob

        Returns:
            Decoded password or None
        """
        if not blob:
            return None
        return blob.decode("utf-16-le")

    @staticmethod
    def _net_use_delete(target: str) -> None:
        """
        Execute 'net use <target> /delete /y' to clear SMB sessions.

        This function is intentionally tolerant to failures to keep
        higher-level logic stable.

        Args:
            target: SMB server target
        """
        try:
            subprocess.run(
                ["net", "use", target, "/delete", "/y"],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            # Never propagate SMB cleanup errors
            pass
