#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from classes.Notification.Notification import Notification


def close_app():
    QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(sys.argv)

    notification = Notification()
    # notification.moveToThread(_MainThread)
    notification.done_signal.connect(close_app)
    notification.start()
    app.exec_()
