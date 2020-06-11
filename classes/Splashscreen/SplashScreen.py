#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from pathlib import Path
from PyQt5.Qt import QProgressBar, QFont, QColor
from PyQt5.QtWidgets import QSplashScreen
from PyQt5 import QtGui, QtCore


class SplashScreen(QSplashScreen):
    """ Display a Splashscreen """

    signal_done = QtCore.pyqtSignal()

    def __init__(self):
        QSplashScreen.__init__(self, QtGui.QPixmap(), QtCore.Qt.WindowStaysOnTopHint)

        self.rootDir = Path(__file__).parent
        image = self.rootDir.joinpath("img/abstract_wave.jpg").as_posix()
        self.version = "3.4"

        splash_pix = QtGui.QPixmap(image)
        # Add version
        painter = QtGui.QPainter()
        painter.begin(splash_pix)

        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.setPen(QColor("#000000"))
        painter.drawText(0, 0, splash_pix.size().width() - 3,
                         splash_pix.size().height() - 1,
                         QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight, self.version)
        painter.end()
        self.setPixmap(splash_pix)

        self.progressBar = QProgressBar(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(100)
        # center on screen
        margin = 10
        # x, y, w, h
        self.progressBar.setGeometry(margin, self.pixmap().height() - 50,
                                     self.pixmap().width() - 2 * margin, 20)
        self.progressBar.setTextVisible(False)

        # CSS Styling
        self.setStyleSheet("""
            QProgressBar:horizontal {
                border: 1px solid gray;
                background: white;
                padding: 0;
                text-align: right;
                margin-top: 10px;
            }
            """)

    def _incProgressbar(self):
        self.progressBar.setValue(self.progressBar.value() + 1)

    def step(self):
        """ a preloading step is done """
        # check if maximum is reached
        self._incProgressbar()
        self.progressBar.repaint()

        if(self.progressBar.value() >= (self.progressBar.maximum() - 1)):
            self.signal_done.emit()

    def setProgressMax(self, maxval):
        self.progressBar.setMaximum(maxval)
