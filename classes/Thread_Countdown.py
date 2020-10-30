#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import time
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class Thread_Countdown(QtCore.QThread):
    """ a Thread that counts down some time """
    finished_signal = pyqtSignal()

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        self.running = False
        self.time = 5
        self.setObjectName("Countdown Thread")
        
        # count the seconds
        self.count = 0

    def __del__(self):
        self.wait()
        
    def stop(self):
        """ stop the running thread """
        self.running = False
    
    def setTime(self, t):
        """ set Time in seconds """
        self.time = t       
        
    def getSeconds(self):
        """ how many seconds are we running? """
        return self.count
    
    def fireEvent(self):
        self.finished_signal.emit()

    def run(self):
        self.running = True
        while(self.running):
            time.sleep(1)
            self.count += 1
            if(self.count == self.time):
                self.fireEvent()
                self.running = False  
        return
