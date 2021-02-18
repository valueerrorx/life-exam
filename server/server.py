#!/usr/bin/env python3
# TEACHER - SERVER #
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details...


import sys
from pathlib import Path

import logging
import qt5reactor
from PyQt5 import QtWidgets
from classes.PlasmaRCTool import PlasmaRCTool

# add application root to python path for imports at position 0
sys.path.insert(0, Path(__file__).parent.parent.as_posix())

from classes import mutual_functions
from classes.Splashscreen.SplashScreen import SplashScreen
from config.logger import configure_logging
from config.config import SERVER_PORT, SERVERFILES_DIRECTORY

from time import time, sleep
from version import __version__

from server.resources.MyServerFactory import MyServerFactory


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # testing
    plasma = PlasmaRCTool()
    plasma.addStarter()
    # testing

    start = time()
    # Create and display the splash screen
    splash = SplashScreen()
    # set version first
    splash.setVersion(__version__)
    splash.setImage("img/LIFE.jpg")
    # splash.show()
    splash.update()
    app.processEvents()
    while time() - start < 2:
        sleep(0.1)
        app.processEvents()

    # Set the Logging
    rootdir = Path(__file__).parent.parent.as_posix()
    # True is Server
    configure_logging(True)
    app.processEvents()

    mutual_functions.prepareDirectories()
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
