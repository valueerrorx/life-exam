#!/usr/bin/env python3
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap, QImage, QBrush, QCursor


class Notification(QLabel):
    """ Display a Notififation for some reasons """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__press_pos = None
        self.initUI()

    def initUI(self):
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('Notification.ui')
        self.ui = uic.loadUi(uifile)        # load UI

        self.ui.setWindowFlags(Qt.FramelessWindowHint)

        # center widget on the screen
        self.ui.adjustSize()  # update self.rect() now
        # position right middle of screen
        screen = QApplication.instance().desktop().screen().rect()
        self.ui.move(screen.width() - self.ui.width(), (screen.height() - self.ui.height()) // 2)
        iconfile = self.rootDir.joinpath('pixmaps/success.png').as_posix()
        self.ui.icon.setPixmap(QPixmap(iconfile))

        self.ui.exit.clicked.connect(self._onAbbrechen)

    def show(self):
        """ show it """
        self.ui.show()

    def hide(self):
        """ show it """
        self.ui.hide()

    def _onAbbrechen(self):
        """ hide it"""
        self.hide()


def main():
    app = QApplication(sys.argv)
    notification = Notification()
    notification.show()
    # w.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
