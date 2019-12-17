#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import time

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal


class Thread_Wait(QtCore.QThread):
    
    client_finished = pyqtSignal(str)
    client_received_file = pyqtSignal(str)
    running = False
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        
    def __del__(self):
        self.wait()
        
    def fireEvent_Abgabe_finished(self, who):
        self.client_finished.emit(who)
    
    def fireEvent_File_received(self, who):
        self.client_received_file.emit(who)
        
    def isAlive(self):
        if self.running:
            return True
        else:
            return False
        
    def stop(self):
        self.running = False
        self.quit()
    
    def setClients(self, clients):
        """ a list within all clients to actually work with """
        self.clients = clients
     
    def run(self):    
        """
        on exit Exam, this thread waits for all Clients to sent their files,
        the fireEvent() will be fired
        """
        self.running = True
        while(self.running):
            time.sleep(0.01)
    
        return 0
    