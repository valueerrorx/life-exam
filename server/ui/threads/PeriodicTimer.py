#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from threading import Timer
from PyQt5 import QtCore


# https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds
class PeriodicTimer(QtCore.QThread):
    def __init__(self, parent, first_interval, interval, func, *args, **kwargs):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        self.timer = None
        self.first_interval = first_interval
        self.interval = interval
        self.func = func
        self.running = False
        self.is_started = False
        self.args = args
        self.kwargs = kwargs
        self.setObjectName("PeriodicTimer")

    def __del__(self):
        self.wait()

    def first_start(self):
        try:
            # if already started will not start again
            if not self.is_started:
                self.is_started = True
                self.timer = Timer(self.first_interval, self.run)
                self.running = True
                self.timer.start()
        except Exception as e:
            print("PeriodicTimer first_start failed %s" % e)
            raise
    
    def run(self):
        # if not stopped start again
        if self.running:
            self.timer = Timer(self.interval, self.run)
            self.timer.start()
        self.func(*self.args, **self.kwargs)

    def stop(self):
        """
        cancel current timer in case failed it's still OK
        if already stopped doesn't matter to stop again
        """
        if self.timer:
            self.timer.cancel()
        self.running = False
        self.is_started = False
