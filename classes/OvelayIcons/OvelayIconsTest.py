#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann
import sys
import cv2
from pathlib import Path
import PyQt5
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from Qt.OvelayIcons.OpenCVLib import OpenCVLib
from Qt.OvelayIcons.IconStack import IconStack


class MAIN_UI(PyQt5.QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MAIN_UI, self).__init__(parent)
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('main.ui')
        self.ui = uic.loadUi(uifile, self)        # load UI inside QMainWindow
        self.ui.btn_add.clicked.connect(lambda: self.addIcon())
        self.ui.btn_remove.clicked.connect(lambda: self.removeIcon())

        self.cv = OpenCVLib()
        self.CVTest(self.ui.image.pixmap())

        # IconStack
        self.stack = IconStack(self.ui.image, "test/")

    def closeEvent(self, event):
        ''' window tries to close '''
        # event.ignore()
        pass

    def addIcon(self):
        self.stack.setExamIconON()
        self.stack.setExamIconOFF()
        self.stack.setFileReceivedOK()
        self.stack.setFileReceivedERROR()

    def removeIcon(self):
        pass

    def CVTest(self, pixmap):
        # TEST 1 ------------------------------------------------
        Qimg = pixmap.toImage()
        img = self.cv.QImage2MAT(Qimg)
        # or load from file
        # image = cv2.imread("mexico.jpg")
        overlay = img.copy()
        output = img.copy()
        # red rectangle for demo
        cv2.rectangle(overlay, (420, 205), (595, 385), (0, 0, 255), -1)
        # apply the overlay
        # img, alpha, original, beta, gamma, output
        alpha = 0.5
        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 1.0, output)
        # write back
        self.ui.image.setPixmap(self.cv.MAT2QPixmap(output))

        # TEST 2 ------------------------------------------------
        # Icon Test
        icon = self.cv.readPNG("test/file_ok.png")
        icon = self.cv.resizeTo(icon, 64, 64)
        pixmap = self.cv.overlayIcon(self.ui.image.pixmap(), icon, 100, 10)
        # write back
        self.ui.image.setPixmap(pixmap)


def main():
    app = QApplication(sys.argv)

    # show main Window
    gui = MAIN_UI()  #noqa
    gui.show()
    app.exec_()


if __name__ == '__main__':
    main()
