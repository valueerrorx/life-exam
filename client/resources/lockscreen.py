#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# LOCKSCREEN 
# pkill -9 -f lockscreen.py
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.


import sys

from PyQt5.QtCore import Qt
from pathlib import Path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon, QPixmap



# add application root to python path for imports at position 0 
sys.path.insert(0, Path(__file__).parent.parent.as_posix())

class ScreenlockWindow(QtWidgets.QMainWindow):
    def __init__(self):
        #super(ScreenlockWindow, self).__init__(parent)
        QtWidgets.QMainWindow.__init__(self)
        #rootDir of Application
        self.rootDir = Path(__file__).parent.parent
        
        icon = self.rootDir.joinpath("pixmaps/windowicon.png").as_posix()
        self.setWindowIcon(QIcon(icon))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint )
        self.setStyleSheet("ScreenlockWindow {background-color: black;}")
        self.label = QtWidgets.QLabel("")
        
        icon = self.rootDir.joinpath("pixmaps/windowicon.png").as_posix()
        self.pixmap = QPixmap(icon)
        self.label.setPixmap(self.pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.label)
        self.label.move(QtWidgets.QApplication.desktop().screen().rect().center()- self.rect().center())
        self.grabMouse()
        self.grabKeyboard()
        self.grabShortcut(QtGui.QKeySequence(Qt.AltModifier))
        self.setWindowModality(Qt.NonModal)
        
         
        #set Fullscreen
        geometry = app.desktop().availableGeometry()
        geometry.setHeight(geometry.height() - (2))

        self.setGeometry(geometry)

    def clickedEvent(self,event):
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
    
    def closeEvent(self, event):
        ''' window tries to close '''
        #now stay active unless client kills the process
        event.ignore()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # @UndefinedVariable
    myapp = ScreenlockWindow()
    myapp.setGeometry(app.desktop().screenGeometry())
    myapp.setFixedSize(6000, 6000)
    myapp.show()
    sys.exit(app.exec_())
