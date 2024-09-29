from PySide6.QtCore import Signal, QThread, Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QApplication, QPushButton, QHBoxLayout
from PySide6.QtGui import QFont
import sys
import time


class WorkThread(QThread):
    """
    A worker thread that counts continuously and emits the count value.

    This class extends QThread and is designed to run in the background,
    incrementing a counter and emitting the current count value at regular intervals.

    Signals:
        countSignal (int): Emitted every second with the current count value.
    """
    count = int(0)
    countSignal = Signal(int)

    def __init__(self):
        super(WorkThread, self).__init__()
        self.flag = True

    def run(self):
        """
        The main method that runs in the thread.

        This method increments the count every second and emits the countSignal
        with the current count value as long as the flag is set to True.
        """
        while self.flag:
            self.count += 1
            self.countSignal.emit(self.count)
            time.sleep(1)

    def stop(self):
        """
        Stops the counting thread gracefully.

        Sets the flag to False, allowing the run method to exit its loop
        and the thread to finish execution.
        """
        self.flag = False


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('QThread demo')
        self.resize(515, 208)
        self.widget = QWidget()
        self.buttonStart = QPushButton('开始')
        self.buttonStop = QPushButton('结束')
        self.label = QLabel('0')
        self.label.setFont(QFont("Adobe Arabic", 28))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.buttonStart)
        layout.addWidget(self.buttonStop)
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)

        self.buttonStart.clicked.connect(self.on_start)
        self.buttonStop.clicked.connect(self.on_stop)

        self.thread = WorkThread()
        self.thread.countSignal.connect(self.flush)

        self.thread.started.connect(lambda: self.statusBar().showMessage('多线程started信号'))
        self.thread.finished.connect(self.finished)

    def flush(self, count):
        self.label.setText(str(count))

    def on_start(self):
        self.statusBar().showMessage('button start.')
        print('button start.')
        self.buttonStart.setEnabled(False)
        self.thread.start()

    def on_stop(self):
        self.statusBar().showMessage('button stop.')
        self.thread.flag = False
        self.thread.quit()

    def finished(self):
        self.statusBar().showMessage('多线程finish信号')
        self.buttonStart.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec())
