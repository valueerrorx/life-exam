#! /usr/bin/env python
# -*- coding: utf-8 -*-
# LOCKSCREEN 
# pkill -9 -f lockscreen.py

import sys, os, subprocess
from PyQt5 import QtCore, QtGui, QtWidgets

class ScreenlockWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(ScreenlockWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint )
        self.setStyleSheet("ScreenlockWindow {background-color: black;}")
        self.label = QtWidgets.QLabel("")
        self.pixmap = QtGui.QPixmap("pixmaps/windowicon.png")
        self.label.setPixmap(self.pixmap)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout().addWidget(self.label)
        self.label.move(QtWidgets.QApplication.desktop().screen().rect().center()- self.rect().center())
        self.grabMouse()
        self.grabKeyboard()
        
        USER = str(subprocess.check_output("logname", shell=True).rstrip())
        command = "exec sudo -u %s -H qdbus org.kde.kglobalaccel /kglobalaccel blockGlobalShortcuts true" % USER
        os.system(command)
        
        
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
