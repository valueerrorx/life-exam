#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann
import sys
from PyQt5.QtWidgets import QApplication
from classes.Notification.Notification import Notification_Core, Notification


def close_app():
    QApplication.quit()


def printhelp():
    msg = '''
python3 NotificationDispatcher.py "Type" "Message"
    Type ... Error, Information, Success, Warning

example:
python3 NotificationDispatcher.py "Information" "Linux is great!"
'''
    print(msg)
    sys.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if len(sys.argv) != 3:
        print("Argument mismatch...")
        printhelp()

    typ = sys.argv[1]
    msg = sys.argv[2]

    # maybe create a invisible main window?
    # creates the Notification Dialog
    n = Notification_Core()
    notification = Notification(n)
    notification.done_signal.connect(close_app)
    if typ.lower() == "information":
        notification.showInformation(msg)
    elif typ.lower() == "error":
        notification.showError(msg)
    elif typ.lower() == "warning":
        notification.showWarning(msg)
    elif typ.lower() == "success":
        notification.showSuccess(msg)
    else:
        print("Wrong Type ...")
        printhelp()

    app.exec_()
