#!/usr/bin/env python3
# TEACHER - SERVER #
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details..

import sys
import os
import logging
from pathlib import Path
from time import time, sleep

# add application root to python path for imports at position 0
sys.path.insert(0, Path(__file__).parent.parent.as_posix())
# print(sys.path)
from version import __version__

from config.logger import configure_logging
from config.config import SCRIPTS_DIRECTORY, SERVER_PORT, SERVERFILES_DIRECTORY

import classes.mutual_functions as mutual_functions
from server.resources.MyServerFactory import MyServerFactory
from classes.Splashscreen.SplashScreen import SplashScreen

from PyQt5 import QtWidgets
import qt5reactor

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    start = time()
    # Create and display the splash screen
    splash = SplashScreen()
    # set version first
    splash.setVersion(__version__)
    splash.setImage("img/LIFE.jpg")
    splash.show()
    splash.update()
    while time() - start < 1:
        sleep(0.001)
        app.processEvents()

    # Set the Logging
    rootdir = Path(__file__).parent.parent.as_posix()
    # True is Server
    configure_logging(True)
    app.processEvents()

    mutual_functions.prepareDirectories()  # cleans everything and copies some scripts
    # killscript = os.path.join(SCRIPTS_DIRECTORY, "terminate-exam-process.sh")
    # os.system("%s %s" % (killscript, 'server'))  # make sure only one client instance is running per client
    # time.sleep(1)
    mutual_functions.writePidFile()
    app.processEvents()

    qt5reactor.install()  # imported from file and needed for Qt to function properly in combination with twisted reactor

    from twisted.internet import reactor
    # start the server on SERVER_PORT
    reactor.listenTCP(SERVER_PORT, MyServerFactory(SERVERFILES_DIRECTORY, reactor, splash, app))  #noqa

    logger = logging.getLogger('server')
    logger.info('Listening on port %d' % (SERVER_PORT))

    reactor.run()  #noqa
