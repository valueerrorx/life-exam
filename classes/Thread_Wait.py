#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import time
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

def tick():
    print("tick")


class Thread_Wait(QtCore.QThread):
    """ a Thread that waits for some reason """
    finished_signal = pyqtSignal()
    wait_ticker_signal = pyqtSignal(QtCore.QThread)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        self.running = False
        self.wait_ticker_signal.connect(tick)

    def __del__(self):
        self.wait()
        
    def fireEvent_Done(self):
        self.finished_signal.emit()

    def run(self):
        self.running = True
        while(self.running):
            time.sleep(1)
            self.wait_ticker_signal.emit(self)

        return 0
