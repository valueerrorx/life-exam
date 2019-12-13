#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import time

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class Thread_Wait(QtCore.QThread):
    
    client_finished = pyqtSignal(str)
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        
    def __del__(self):
        self.wait()
        
    def fireEvent(self, who):
        self.client_finished.emit(who)
     
    def run(self):    
        """
        on exit Exam, this thread waits for all Clients to sent their files,
        the fireEvent() will be fired
        """
        self.running = True
        while(self.running):
            time.sleep(0.01)
    
        return 0
    