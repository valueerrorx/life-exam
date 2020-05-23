#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from Qt.Notification.Notification import Notification, Notification_Core,\
    Notification_Type


def close_app():
    QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(sys.argv)

    # creates the Notification Dialog
    n = Notification_Core()
    n.setMessage("Meldung")
    n.setType(Notification_Type.Error)

    notification = Notification(n)
    notification.done_signal.connect(close_app)
    notification.start()
    app.exec_()
