#! /usr/bin/env python
# -*- coding: utf-8 -*-
# LOCKSCREEN 
# pkill -9 -f lockscreen.py

import sys, os, subprocess
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QIcon
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

        self.setWindowModality(Qt.NonModal)

        
        
    def keyPressEvent(self, event):
        return
    
    def mouseReleaseEvent(self, event):
        return

    def mouseMoveEvent(self, event):
        return


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = ScreenlockWindow()
    myapp.setGeometry(app.desktop().screenGeometry())
    myapp.setFixedSize(6000, 6000)
    myapp.show()
    sys.exit(app.exec_())
