#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from config.config import APP_DIRECTORY, SHARE_DIRECTORY

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QImage, QPalette, QBrush
from PyQt5.QtCore import QSize

class ScreenshotWindow(QtWidgets.QDialog):
    def __init__(self, serverui, screenshot, clientname, screenshot_file_path, client_connection_id):
        QtWidgets.QDialog.__init__(self)
        self.setWindowIcon(QIcon(os.path.join(APP_DIRECTORY,'pixmaps/windowicon.png')))  # definiere icon für taskleiste
        self.screenshot = screenshot
        self.serverui = serverui
        self.screenshot_file_path = screenshot_file_path
        self.client_connection_id = client_connection_id
        text =  "Screenshot - %s - %s" %(screenshot, clientname)
        self.setWindowTitle(text)
        self.setGeometry(100,100,1200,675)
        self.setFixedSize(1200, 675)
        oImage = QImage(screenshot_file_path)
        sImage = oImage.scaled(QSize(1200,675))                   # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))                     # 10 = Windowrole
        self.setPalette(palette)

        button1 = QtWidgets.QPushButton('Screenshot archivieren', self)
        button1.move(1020, 580)
        button1.resize(180,40)
        button1.clicked.connect(self._archivescreenshot)

        button2 = QtWidgets.QPushButton('Abgabe holen', self)
        button2.move(1020, 480)
        button2.resize(180,40)
        button2.clicked.connect(lambda: serverui._onAbgabe(client_connection_id))

        button3 = QtWidgets.QPushButton('Screenshot updaten', self)
        button3.move(1020, 530)
        button3.resize(180,40)
        button3.clicked.connect(lambda: serverui._onScreenshots(client_connection_id))

        button4 = QtWidgets.QPushButton('Fenster schließen', self)
        button4.move(1020, 430)
        button4.resize(180,40)
        button4.clicked.connect(self._onClose)


    def _onClose(self):  # Exit button
        self.close()

    def _archivescreenshot(self):
        filedialog = QtWidgets.QFileDialog()
        filedialog.setDirectory(SHARE_DIRECTORY)  # set default directory
        file_path = filedialog.getSaveFileName()  # get filename
        file_path = file_path[0]

        if file_path:
            #os.rename(self.screenshot_file_path, file_path)  #moves the file (its not available in src anymore)
            shutil.copyfile(self.screenshot_file_path,file_path)
            print("screensshot archived")
