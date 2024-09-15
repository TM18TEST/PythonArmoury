#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright©2024 Xiamen Tianma Display Technology Co., Ltd. All rights reserved.
"""
import logging

from PySide6 import QtWidgets
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMessageBox, QStyle


class CustomMessageBox(QMessageBox):
    # Define a custom signal with the QMessageBox instance and the result
    finished_with_box = Signal(QMessageBox, int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def done(self, result):
        # Emit the custom signal with the QMessageBox instance and the result
        self.finished_with_box.emit(self, result)
        super().done(result)


class QtMsgBox:
    DEFAULT_MAX_MSG_BOX_NUM = 8

    def __init__(self, max_box_num: int = None, logger: logging.Logger = None):
        if max_box_num is None:
            self._max_box_num = QtMsgBox.DEFAULT_MAX_MSG_BOX_NUM
        else:
            self._max_box_num = max_box_num
        self._msg_box_list = []
        self._logger = logger or logging.getLogger(__name__)

    @staticmethod
    def fill_msg_box(msg_box: QMessageBox, title: str, err_msg: str,
                     window_icon: QtWidgets.QStyle.StandardPixmap,
                     box_icon: QMessageBox.Icon) -> None:
        # Set the title of message box
        msg_box.setWindowIcon(msg_box.style().standardIcon(window_icon))
        msg_box.setWindowTitle(title)

        # Set the content of message box
        msg_box.setText(err_msg)

        # Set the icon of message box
        msg_box.setIcon(box_icon)

    @staticmethod
    def exec(title: str, err_msg: str, box_icon: QMessageBox.Icon) -> None:
        # Create an object of message box
        msg_box = QMessageBox()

        QtMsgBox.fill_msg_box(msg_box, title, err_msg, QStyle.StandardPixmap.SP_MessageBoxInformation, box_icon)

        # Execute the message box
        msg_box.exec()

    def show(self, title: str, err_msg: str, box_icon: QMessageBox.Icon) -> None:
        if len(self._msg_box_list) >= self._max_box_num:
            self._logger.warning("Too many message box, discard new one, error message: %s.", err_msg)
            return

        # Create an object of custom message box
        msg_box = CustomMessageBox()

        QtMsgBox.fill_msg_box(msg_box, title, err_msg, QStyle.StandardPixmap.SP_MessageBoxInformation, box_icon)

        # Set the handler for box close event
        msg_box.finished_with_box.connect(self.on_message_box_closed)

        self._msg_box_list.append(msg_box)

        # Show the message box in non-blocking mode
        msg_box.show()
        msg_box.raise_()
        msg_box.activateWindow()

    def on_message_box_closed(self, msg_box, result):
        self._logger.info("Received close event, instance: %s, result: %d.", msg_box, result)
        if msg_box in self._msg_box_list:
            self._msg_box_list.remove(msg_box)
            self._logger.info("Removed close event from list success.")
