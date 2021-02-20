#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
from config.config import SHARE_DIRECTORY
from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush
from PyQt5.QtCore import Qt


class ScreenshotWindow(QtWidgets.QDialog):

    def __init__(self, serverui):
        # QtWidgets.QDialog.__init__(self)
        super(ScreenshotWindow, self).__init__()

        # rootDir of Application
        self.rootDir = Path(__file__).parent.parent.parent

        icon = self.rootDir.joinpath("pixmaps/windowicon.png").as_posix()
        self.setWindowIcon(QIcon(icon))  # definiere icon für taskleiste

        self.screenshot = None
        self.serverui = serverui
        self.screenshot_file_path = None
        self.client_connection_id = -1
        self.setGeometry(100, 100, 1200, 675)
        self.setFixedSize(1200, 675)

        self.button1 = QtWidgets.QPushButton('Screenshot archivieren', self)
        self.button1.move(1020, 580)
        self.button1.resize(180, 40)
        self.button1.clicked.connect(self._archivescreenshot)

        self.button2 = QtWidgets.QPushButton('Abgabe holen', self)
        self.button2.move(1020, 480)
        self.button2.resize(180, 40)

        self.button3 = QtWidgets.QPushButton('Screenshot updaten', self)
        self.button3.move(1020, 530)
        self.button3.resize(180, 40)

        self.button4 = QtWidgets.QPushButton('Fenster schließen', self)
        self.button4.move(1020, 430)
        self.button4.resize(180, 40)
        self.button4.clicked.connect(self._onClose)

    # Update stuff for new Data
    def updateUI(self):
        text = "Screenshot - %s - %s" % (self.screenshot, self.clientname)
        self.setWindowTitle(text)
        oImage = QImage(self.screenshot_file_path)
        # resize Image to widgets size
        sImage = oImage.scaled(1200, 675, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        # 10 = Windowrole
        palette.setBrush(10, QBrush(sImage))
        self.setPalette(palette)
        self.button2.clicked.connect(lambda: self.serverui.onAbgabe(self.getClientConnectionID()))
        self.button3.clicked.connect(lambda: self.serverui.onScreenshots(self.getClientConnectionID()))

    def setScreenshot(self):
        self.screenshot = "%s.jpg" % self.getClientConnectionID()

    def setClientname(self, clientname):
        self.clientname = clientname
        self.setScreenshot()

    def setScreenshotFilePath(self, screenshot_file_path):
        self.screenshot_file_path = screenshot_file_path

    def setClientConnectionID(self, client_connection_id):
        self.client_connection_id = client_connection_id

    def getClientConnectionID(self):
        return self.client_connection_id

    def _onClose(self):  # Exit button
        self.close()

    def _archivescreenshot(self):
        filedialog = QtWidgets.QFileDialog()
        filedialog.setDirectory(SHARE_DIRECTORY)  # set default directory
        file_path = filedialog.getSaveFileName()  # get filename
        file_path = file_path[0]

        if file_path:
            # os.rename(self.screenshot_file_path, file_path)  #moves the file (its not available in src anymore)
            shutil.copyfile(self.screenshot_file_path, file_path)
            print("Screenshot archived")
