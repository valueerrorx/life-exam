#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann
import sys
import time
from pathlib import Path
import PyQt5
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QCoreApplication
from Qt.Splashscreen.SplashScreen import SplashScreen


class MAIN_UI(PyQt5.QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MAIN_UI, self).__init__(parent)
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('main.ui')
        self.ui = uic.loadUi(uifile, self)        # load UI inside QMainWindow
        self.ui.close.clicked.connect(lambda: self.close())

    def updateProgressBar(self):
        self.ui.progressBar.setValue(self.progress)

    def close(self):
        QCoreApplication.quit()

    def closeEvent(self, event):
        ''' window tries to close '''
        # event.ignore()
        pass

    def setData(self, data):
        """ do something with preloaded data """
        pass


def preload(splash, app):
    """ here we are loading all data that we need """
    splash.setProgressMax(4)
    for i in range(4):
        time.sleep(1)
        app.processEvents()
        splash.step()

    app.processEvents()
    return 0


def main():
    app = QApplication(sys.argv)

    # Create and display the splash screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    gui = MAIN_UI()  #noqa
    data = preload(splash, app)
    gui.setData(data)
    gui.show()

    time.sleep(1)
    splash.finish(gui)

    app.exec_()


if __name__ == '__main__':
    main()
