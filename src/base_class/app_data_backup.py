#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Description: Application Data Backup Base Class.
"""
from dataclasses import dataclass
from typing import Callable, Any, Tuple, Dict, Optional

from base_class.data_backup import DataBackup, DataBackupParam


@dataclass
class FuncCall:
    func: Callable[..., Any]
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = None

    def execute(self):
        if self.kwargs is None:
            self.kwargs = {}
        return self.func(*self.args, **self.kwargs)


@dataclass
class AppDataBackupParam:
    data_backup_param: DataBackupParam
    start_app_func: Optional[FuncCall] = None
    stop_app_func: Optional[FuncCall] = None


class AppDataBackup(DataBackup):
    """
    Application Data Backup Base Class.
    """

    def __init__(self, param: AppDataBackupParam):
        # Declare some variables of current instance
        super().__init__(param.data_backup_param)
        self._app_stopped: bool = False
        self._start_app_func: Optional[FuncCall] = param.start_app_func
        self._stop_app_func: Optional[FuncCall] = param.stop_app_func

    def stop_app(self) -> bool:
        if self._stop_app_func is not None:
            self._stop_app_func.execute()
            return True
        return False

    def pre_backup(self) -> None:
        self._app_stopped = self.stop_app()

    def start_app(self) -> bool:
        if self._start_app_func is not None:
            self._start_app_func.execute()
            return True
        return False

    def post_backup(self) -> None:
        if self.start_app():
            self._app_stopped = False

    def run(self) -> str:
        try:
            backup_path: str = super().run()
        except Exception:
            if self._app_stopped:
                self.start_app()
            raise
        return backup_path
