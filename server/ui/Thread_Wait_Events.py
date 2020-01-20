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
    #anzeigen im Dateimanager
    mutual_functions.openFileManager(os.path.join(SHARE_DIRECTORY, who))

        
def client_received_file_done(clientWidget):
    """ will be fired, if a client has received a file that was sent by server """
    #event fired in MyServerProtocol
    logger.info("Client %s has received a file ..." % clientWidget.getName())
    #set the status Icon
    clientWidget.setFileReceivedOK()
    
