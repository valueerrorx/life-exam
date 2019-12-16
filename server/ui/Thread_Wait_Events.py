#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import os
from config.config import SHARE_DIRECTORY


def client_abgabe_done_exit_exam(serverui, who):
    """ will fired when Client has sent his Abgabe File """
    #event fired in MyServerProtocol
    serverui.log("Client %s has finished sending Abgabe-File ..." % who)
    #anzeigen im Dateimanager
    openFileManager(os.path.join(SHARE_DIRECTORY, who))
        
def client_recieved_file_done(self):
    """ will be fired, if a client has received a file that was sent by server """    