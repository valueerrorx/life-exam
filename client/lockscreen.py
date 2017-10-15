#! /usr/bin/env python
# -*- coding: utf-8 -*-
# LOCKSCREEN 
# pkill -9 -f lockscreen.py

import sys, os, subprocess
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
from PyQt5.QtCore import Qt


class ScreenlockWindow(QtWidgets.QMainWindow):
    def __init__(self):
        #super(ScreenlockWindow, self).__init__(parent)
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowIcon(QIcon("pixmaps/windowicon.png"))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint )
        self.setStyleSheet("ScreenlockWindow {background-color: black;}")
        self.label = QtWidgets.QLabel("")
        self.pixmap = QPixmap("pixmaps/windowicon.png")
        self.label.setPixmap(self.pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.label)
        self.label.move(QtWidgets.QApplication.desktop().screen().rect().center()- self.rect().center())
        self.grabMouse()
        self.grabKeyboard()
        self.grabShortcut(QKeySequence(Qt.AltModifier))
        self.setWindowModality(Qt.NonModal)


    def clickedEvent(self.event):
        event.ignore()
        return

    def mousePressEvent(self,event):
        event.ignore()
        return

    def dragEnterEvent(self, event):
        event.ignore()
        pass

    def dragMoveEvent(self, event):
        event.ignore()
        pass

    def mouseReleaseEvent(self, event):
        event.ignore()
        pass

    def mouseMoveEvent(self, event):
        event.ignore()
        pass

    def moveEvent(self,event):
        self.move(0,0)
        event.ignore()
        pass




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = ScreenlockWindow()
    myapp.setGeometry(app.desktop().screenGeometry())
    myapp.setFixedSize(6000, 6000)
    myapp.show()
    sys.exit(app.exec_())

