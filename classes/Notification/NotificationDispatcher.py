#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from classes.Notification.Notification import Notification_Type,\
    Notification_Core, Notification


def close_app():
    print("exit")
    QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(sys.argv)

    # creates the Notification Dialog
    n = Notification_Core()
    notification = Notification(n)
    notification.done_signal.connect(close_app)
    notification.showInformation("This is a test for showing one Notification")

    app.exec_()
