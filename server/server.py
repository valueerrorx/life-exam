#! /usr/bin/env python3
# TEACHER - SERVER #
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.
#
# sudo -H pip3 install twisted  # we need twisted for python3

import os
import sys
import logging
from pathlib import Path

# add application root to python path for imports at position 0 
sys.path.insert(0, Path(__file__).parent.parent.as_posix())
#print(sys.path)

#Logging System
from config.logger import configure_logging

import qt5reactor
import ipaddress
import datetime
import time
import sip
import zipfile
import ntpath
import shutil

from config.config import *
from config.enums import *

import classes.mutual_functions as mutual_functions
import classes.system_commander as system_commander

from server.resources.MyServerFactory import *
from server.resources.ScreenshotWindow import *
from server.resources.Applist import * 

#from PyQt5 import uic, QtWidgets, QtCore
#from PyQt5.QtGui import *
#from PyQt5.QtCore import QRegExp


if __name__ == '__main__':
    #Set the Logging
    rootdir = Path(__file__).parent.parent.as_posix()
    configure_logging('%s' % (rootdir))
        
    mutual_functions.prepareDirectories()  # cleans everything and copies some scripts
    killscript = os.path.join(SCRIPTS_DIRECTORY, "terminate-exam-process.sh")
    os.system("%s %s" % (killscript, 'server'))  # make sure only one client instance is running per client
    # time.sleep(1)
    mutual_functions.writePidFile()

    app = QtWidgets.QApplication(sys.argv)
    qt5reactor.install()  # imported from file and needed for Qt to function properly in combination with twisted reactor

    from twisted.internet import reactor

    reactor.listenTCP(SERVER_PORT, MyServerFactory(SERVERFILES_DIRECTORY, reactor ))  # start the server on SERVER_PORT
    
    logger = logging.getLogger('server')
    logger.info ('Listening on port %d' % (SERVER_PORT))
    
    reactor.run()
