#!/usr/bin/env python3
from pathlib import Path
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
import time
import threading
import random
from enum import Enum
from PyQt5.Qt import QThread


class Notification_Core(QtWidgets.QDialog):
    """ Display a Notification for some reasons """
    def __init__(self, parent=None):
        super(Notification_Core, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('Notification.ui')
        self.ui = uic.loadUi(uifile)        # load UI
        self.ui.setWindowFlags(Qt.FramelessWindowHint)

        self.ui.adjustSize()
        # position right middle of screen
        screen = QApplication.instance().desktop().screen().rect()
        self.ui.move(screen.width() - self.ui.width(), (screen.height() - self.ui.height()) // 2)
        iconfile = self.rootDir.joinpath('pixmaps/success.png').as_posix()
        self.ui.icon.setPixmap(QPixmap(iconfile))

        self.ui.exit.clicked.connect(self._onAbbrechen)
        self._timeout = 4  # sec

    def moveTo(self, x, y):
        """ move the dialog on the screen """
        self.ui.move(x, y)

    def show(self):
        """ show it """
        # self.ticker.start()
        self.ui.show()

    def hide(self):
        """ show it """
        self.ui.hide()

    def _onAbbrechen(self):
        """ click event, hide it"""
        self.close()

    def setHeader(self, txt):
        """ set the Header of the notification """
        self.ui.header.setText(txt)

    def setMessage(self, txt):
        """ set the Message of the notification """
        self.ui.text.setText(txt)

    def setTimeout(self, time):
        """ how long should the notification be displayed in sec """
        self._timeout = time

    def getTimeout(self):
        return self._timeout

    def setIcon(self, icon):
        iconfile = self.rootDir.joinpath(icon).as_posix()
        self.ui.icon.setPixmap(QPixmap(iconfile))

    def setBarColor(self, color):
        self.ui.colorbar.setStyleSheet("background-color: %s;" % color)


class Notification_Type(Enum):
    Information = 1
    Success = 2
    Error = 3
    Warning = 4


class Notification(QtCore.QThread):
    done_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(Notification, self).__init__(parent)
        # random position on screen just for demonstration
        self.demo = False
        self.parent = parent

    def __del__(self):
        pass

    def _createNotification(self, msg, typ):
        """ shows a Information Notification """
        n = Notification_Core(self.parent)
        if typ == Notification_Type.Information:
            n.setHeader("Information")
            n.setIcon('pixmaps/notice.png')
            n.setBarColor("#2C54AB")
        elif typ == Notification_Type.Success:
            n.setHeader("Done")
            n.setIcon('pixmaps/success.png')
            n.setBarColor("#009961")
        elif typ == Notification_Type.Error:
            n.setHeader("Error")
            n.setIcon('pixmaps/error.png')
            n.setBarColor("#CC0033")
        elif typ == Notification_Type.Warning:
            n.setHeader("Warning")
            n.setIcon('pixmaps/warning.png')
            n.setBarColor("#E23E0A")

        n.setMessage(msg)

        if self.demo:
            x = random.randrange(100, 800)
            y = random.randrange(100, 800)
            n.moveTo(x, y)

        n.show()
        time.sleep(n.getTimeout())
        n.hide()

    def run(self):
        notification = Notification()
        notification._createNotification("sdxfdf", Notification_Type.Success)
        self.done_signal.emit()

    def showInformation(self, msg):
        t = threading.Thread(target=self._createNotification, args=[msg, Notification_Type.Information])
        t.daemon = True
        t.start()

    def showSuccess(self, msg):
        t = threading.Thread(target=self._createNotification, args=[msg, Notification_Type.Success])
        t.daemon = True
        t.start()

    def showError(self, msg):
        self.t = threading.Thread(target=self._createNotification, args=[msg, Notification_Type.Error])
        self.t.daemon = True
        self.t.start()

    def showWarning(self, msg):
        t = threading.Thread(target=self._createNotification, args=[msg, Notification_Type.Warning])
        t.daemon = True
        t.start()

