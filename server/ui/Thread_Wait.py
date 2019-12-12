#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import logging
import time
from PyQt5 import QtCore


class Thread_Wait(QtCore.QThread):
    
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        
    def fireEvent(self, who):
        print(who)
     
    def run(self):    
        """
        on exit Exam, this thread waits for all Clients to send their files
        """
        self.running = True
        while(self.running):
            time.sleep(0.01)
            
            
            
     
            self.emit( QtCore.SIGNAL('update(QString)'), "from work thread " )
            
            #Get Event from MyServerProtocol
            logging.debug('Client finished transferring Abgabe')
            #remove from list
            #who = getConnectionStr(clients, e.param)
            #clients = delClient(clients, e.param)
            
            #self.sig1.emit(who)
            # then send the exam exit signal
            #if not factory.server_to_client.exit_exam(who, onexit_cleanup_abgabe):
            #    pass
    
        return 0
    