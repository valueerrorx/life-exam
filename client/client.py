#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.

import sys
import os
from pathlib import Path
import fcntl
import atexit

# add application root to python path for imports at position 0
sys.path.insert(0, Path(__file__).parent.parent.as_posix())
# Logging System 
from config.logger import configure_logging

from client.ui.ClientUI import ClientDialog
from client.resources.MulticastLifeClient import MulticastLifeClient

application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, application_path)

import qt5reactor
from PyQt5 import QtWidgets

""" prevent to start client twice """
def lockFile(lockfile):
    fp = open(lockfile, 'w')  # create a new one
    try:
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # the file has been locked
        success = True 
    except IOError:
        success = False
    fp.close() 
    return success

""" at client shutdown, delete the lock File """
def cleanUpLockFile(file):
    if os.path.exists(file):
        os.remove(file)


if __name__ == '__main__':
    # Set the Logging
    rootdir = Path(__file__).parent.parent.as_posix()
    
    FILE_NAME = "started_client.lock"
    # do not start twice
    if os.path.exists(FILE_NAME):
        print("Don't start the Client twice ... exit") 
        sys.exit(0)
    print('Lock File created: Preventing starting twice ...', lockFile(FILE_NAME))
    atexit.register(cleanUpLockFile, FILE_NAME)
    
    configure_logging(False)       # True is Server

    app = QtWidgets.QApplication(sys.argv)
    dialog = ClientDialog()
    dialog.ui.show()
    qt5reactor.install()  # imported from file and needed for Qt to function properly in combination with twisted reactor

    from twisted.internet import reactor
    reactor.listenMulticast(8005, MulticastLifeClient(), listenMultiple=True)  #noqa
    sys.exit(app.exec_())
