#!/usr/bin/env python3
"""Drag invisible window."""
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLabel


class Invisible(QLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__press_pos = None
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setText("Drag me...")
        self.setFont(QFont("Times", 50, QFont.Bold))
        # center widget on the screen
        self.adjustSize()  # update self.rect() now
        self.move(QApplication.instance().desktop().screen().rect().center()
                  - self.rect().center())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__press_pos = event.pos()  # remember starting position

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.__press_pos = None

    def mouseMoveEvent(self, event):
        if self.__press_pos:  # follow the mouse
            self.move(self.pos() + (event.pos() - self.__press_pos))


def main():
    app = QApplication(sys.argv)
    w = Invisible()
    w.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
