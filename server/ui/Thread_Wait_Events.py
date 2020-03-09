#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import os
from config.config import SHARE_DIRECTORY
import classes.mutual_functions as mutual_functions
import logging

logger = logging.getLogger(__name__)


def client_abgabe_done_exit_exam(who):
    """ will fired when Client has sent his Abgabe File """
    #event fired in MyServerProtocol
    logger.info("Client %s has finished sending Abgabe-File ..." % who)
    #shoe in Filemanager
    mutual_functions.openFileManager(os.path.join(SHARE_DIRECTORY, who))

        
def client_received_file_done(parent, clientWidget):
    """ will be fired, if a client has received a file that was sent by server """
    #event fired in MyServerProtocol
    logger.info("Client %s has received a file ..." % clientWidget.getName())
    #set the status Icon
    clientWidget.setFileReceivedOK()
    parent.networkProgress.decrement()
    if parent.networkProgress.value()==0:
        #if there is an animation showing
        parent.workinganimation.stop()

    
def client_abgabe_done(self, who):
        """ will fired when Client has sent his Abgabe File """
        
        self.log("Client %s has finished sending Abgabe-File, now exiting ..." % who)
        onexit_cleanup_abgabe = self.ui.exitcleanabgabe.checkState()   
        #get from who the connectionID        
        item = self.get_list_widget_by_client_name(who)
        # then send the exam exit signal
        if not self.factory.server_to_client.exit_exam(item.pID, onexit_cleanup_abgabe):
            pass

  
def client_lock_screen(parent, who):
    """ will be fired when client locks the screen """
    parent.networkProgress.decrement()
    if parent.networkProgress.value()==0:
        #if there is an animation showing
        parent.workinganimation.stop()

    
def client_unlock_screen(parent, who):
    """ will be fired when client unlocks the screen """
    parent.networkProgress.decrement()
    if parent.networkProgress.value()==0:
        #if there is an animation showing
        parent.workinganimation.stop()  

    
