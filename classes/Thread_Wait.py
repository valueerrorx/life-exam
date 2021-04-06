#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import time
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class Thread_Wait(QtCore.QThread):
    """ a Thread that waits for some reason """
    finished_signal = pyqtSignal()

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        self.running = False
        self.setObjectName("Wait Thread")

        # count the seconds
        self.count = 0

    #def __del__(self):
        #self.wait()

    def stop(self):
        """ stop the running thread """
        self.running = False

    def fireEvent_Done(self):
        self.finished_signal.emit()

    def getSeconds(self):
        """ how many seconds are we running? """
        return self.count

    def run(self):
        self.running = True
        while(self.running):
            time.sleep(1)
            self.count += 1

        return
