#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from PyQt5 import QtCore
from threading import Timer

class Thread_Countdown(QtCore.QThread):
    """ 
    a Thread that counts down some time
    you had to manually stop this thread! 
    :time: in Seconds after that the Timer is fireing event func
    """
    def __init__(self, parent, time, func, *args, **kwargs):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        self.timer = None
        self.func = func
        self.running = False
        self.args = args
        self.kwargs = kwargs
        
        self.setObjectName("Countdown Thread")
        self.time = time

    def __del__(self):
        self.wait()
        
    def start(self):
        self.timer = Timer(self.time, self.run)
        self.running = True
        self.timer.start()
        
    def stop(self):
        """
        cancel current timer in case failed it's still OK
        if already stopped doesn't matter to stop again
        """
        if self.timer:
            self.timer.cancel()
        self.running = False
    
    def setTime(self, t):
        """ set Time in seconds """
        self.time = t       
        
    def getSeconds(self):
        """ how many seconds are we running? """
        return self.count
    
    def run(self):
        self.func(*self.args, **self.kwargs)
