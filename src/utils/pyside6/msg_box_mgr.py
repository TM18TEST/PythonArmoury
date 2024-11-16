#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logging import Logger

from PySide6 import QtWidgets
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMessageBox, QStyle

class ManagedMsgBox(QMessageBox):
    # Define a custom signal with the QMessageBox instance and the result
    finished_with_box = Signal(QMessageBox, int)

    def __init__(self, parent = None, logger: Logger=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._logger = logger

    def done(self, result):
        # Emit the custom signal with the QMessageBox instance and the result
        if self._logger:
            self._logger.info("ManagedMessageBox done called.")
        self.finished_with_box.emit(self, result)
        super().done(result)

    def closeEvent(self, event):
        """
        Avoid the problem of causing the main process to exit when
            closing the message box displayed using the show method
            through the close button in the upper right corner of the window.
        :param event: Contains information about the close event
        """
        if self._logger:
            self._logger.info("ManagedMessageBox closeEvent called.")
        super().closeEvent(event)  # 确保调用父类的 closeEvent


class MsgBoxMgr:
    DEFAULT_MAX_MSG_BOX_NUM = 8

    def __init__(self, parent = None, logger=None, max_box_num: int = None):
        self._parent = parent
        self._logger = logger
        self._max_box_num = max_box_num or MsgBoxMgr.DEFAULT_MAX_MSG_BOX_NUM
        self._msg_box_list = []

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

        MsgBoxMgr.fill_msg_box(msg_box, title, err_msg, QStyle.StandardPixmap.SP_MessageBoxInformation, box_icon)

        # Execute the message box
        msg_box.exec()

    def show(self, title: str, err_msg: str, box_icon: QMessageBox.Icon) -> None:
        if len(self._msg_box_list) >= self._max_box_num:
            if self._logger:
                self._logger.warning("Too many message box, discard new one, error message: %s.", err_msg)
            return

        # Create an object of custom message box
        msg_box = ManagedMsgBox(self._parent)

        MsgBoxMgr.fill_msg_box(msg_box, title, err_msg, QStyle.StandardPixmap.SP_MessageBoxInformation, box_icon)

        # Set the handler for box close event
        msg_box.finished_with_box.connect(self.on_message_box_closed)

        self._msg_box_list.append(msg_box)

        # Show the message box in non-blocking mode
        msg_box.show()
        msg_box.raise_()
        msg_box.activateWindow()

    def on_message_box_closed(self, msg_box, result):
        if self._logger:
            self._logger.info("Received close event, instance: %s, result: %d.", msg_box, result)
        if msg_box in self._msg_box_list:
            self._msg_box_list.remove(msg_box)
            if self._logger:
                self._logger.info("Removed close event from list success.")
