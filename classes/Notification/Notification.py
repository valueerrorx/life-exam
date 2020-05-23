#!/usr/bin/env python3
from pathlib import Path
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
import time
import random
from enum import Enum
from PyQt5.Qt import QObject
import threading


class Notification_Type(Enum):
    Information = 1
    Success = 2
    Error = 3
    Warning = 4


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

        # position right middle of screen
        self.moveToDefaultPosition()

        iconfile = self.rootDir.joinpath('pixmaps/success.png').as_posix()
        self.ui.icon.setPixmap(QPixmap(iconfile))

        self.ui.exit.clicked.connect(self._onAbbrechen)
        self._timeout = 4  # sec
        self._typ = Notification_Type.Information

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

    def setType(self, typ):
        """ set the type of the notification """
        self._typ = typ

    def getType(self):
        """ get the type of the notification """
        return self._typ

    def moveToDefaultPosition(self):
        """ the default position right middle of screen """
        self.ui.adjustSize()
        screen = QApplication.instance().desktop().screen().rect()
        self.ui.move(screen.width(), (screen.height() - self.ui.height()) // 2)


class Notification(QObject):
    done_signal = pyqtSignal()
    startNotification_Signal = pyqtSignal(Notification_Core)
    stopNotification_Signal = pyqtSignal(Notification_Core)

    def __init__(self, notification, parent=None):
        super(Notification, self).__init__(parent)
        self._notification = notification
        # random position on screen just for demonstration
        self.demo = False
        self.parent = parent

    def __del__(self):
        pass

    def setDemo(self):
        """ activates random positioning """
        self.demo = True

    def _showNotification(self, n):
        """ shows the notification n """
        n.show()

    def _hideNotification(self, n):
        """ hides the notification n """
        n.hide()
        self.done_signal.emit()

    def _createNotification(self):
        """ shows the Notification as thread"""
        typ = self._notification.getType()
        if typ == Notification_Type.Information:
            self._notification.setHeader("Information")
            self._notification.setIcon('pixmaps/notice.png')
            self._notification.setBarColor("#2C54AB")
        elif typ == Notification_Type.Success:
            self._notification.setHeader("Done")
            self._notification.setIcon('pixmaps/success.png')
            self._notification.setBarColor("#009961")
        elif typ == Notification_Type.Error:
            self._notification.setHeader("Error")
            self._notification.setIcon('pixmaps/error.png')
            self._notification.setBarColor("#CC0033")
        elif typ == Notification_Type.Warning:
            self._notification.setHeader("Warning")
            self._notification.setIcon('pixmaps/warning.png')
            self._notification.setBarColor("#E23E0A")

        if self.demo:
            x = random.randrange(100, 800)
            y = random.randrange(100, 800)
            self._notification.moveTo(x, y)
        else:
            self._notification.moveToDefaultPosition()

        self.startNotification_Signal.connect(self._showNotification)
        self.stopNotification_Signal.connect(self._hideNotification)

        self.startNotification_Signal.emit(self._notification)
        time.sleep(self._notification.getTimeout())
        self.stopNotification_Signal.emit(self._notification)

    def showInformation(self, msg):
        self._notification.setType(Notification_Type.Information)
        self._notification.setMessage(msg)
        t = threading.Thread(target=self._createNotification)
        t.daemon = True
        t.start()

    def showSuccess(self, msg):
        self._notification.setType(Notification_Type.Success)
        self._notification.setMessage(msg)
        t = threading.Thread(target=self._createNotification)
        t.daemon = True
        t.start()

    def showError(self, msg):
        self._notification.setType(Notification_Type.Error)
        self._notification.setMessage(msg)
        t = threading.Thread(target=self._createNotification)
        t.daemon = True
        t.start()

    def showWarning(self, msg):
        self._notification.setType(Notification_Type.Warning)
        self._notification.setMessage(msg)
        t = threading.Thread(target=self._createNotification)
        t.daemon = True
        t.start()
