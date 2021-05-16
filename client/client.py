#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.

import sys
from pathlib import Path
from classes.psUtil import PsUtil
import logging
from config.config import HEARTBEAT_PORT
from classes.Heartbeats.HeartbeatClient import HeartbeatClient

# add application root to python path for imports at position 0
rootPath = Path(__file__).parent.parent.as_posix()
sys.path.insert(0, rootPath)

from client.ui.ClientUI import ClientDialog
from client.resources.MulticastLifeClient import MulticastLifeClient
from config.logger import configure_logging

import os
import fcntl
import atexit
from PyQt5 import QtWidgets
import qt5reactor


def lockFile(lockfile):
    """ prevent to start client twice """
    fp = open(lockfile, 'w')  # create a new one
    try:
        fp.write("%s" % os.getpid())
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # the file has been locked
        success = True
    except IOError:
        success = False
    fp.close()
    return success


def cleanUpLockFile(file):
    """ at client shutdown, delete the lock File """
    if os.path.exists(file):
        os.remove(file)


def killRunningTwistd(logger):
    """ if a running twistd client is found > kill it """
    processUtil = PsUtil()
    pid = processUtil.GetProcessByName("twistd3")
    if len(pid) > 0:
        logger.info("Found a running twistd, killing that process ...")
        # found a twistd process, kill all pids
        for p in pid:
            cmd = "sudo -E kill -9 %s" % int(p[0])
            os.system(cmd)


def checkRunningPID():
    """ check id the PID from Lock File is still active, if not then del LockFile """
    f = open(FILE_NAME, "r")
    pid = f.read()
    ps = PsUtil()
    if ps.isRunning(pid) is False:
        # old Process is dead
        cleanUpLockFile(FILE_NAME)
        print("Deleted Client Zombie Process Lock File ...")
        return False
    return True


if __name__ == '__main__':
    rootDir = Path(__file__).parent.parent
    FILE_NAME = uifile = rootDir.joinpath("client/started_client.lock")

    logger = logging.getLogger(__name__)
    configure_logging(False)       # True is Server

    # do not start twice
    if os.path.exists(FILE_NAME):
        if checkRunningPID() is True:
            print("Client Process found, exiting now ...")
            sys.exit(0)

    print('Lock File created: Preventing starting twice ...', lockFile(FILE_NAME))
    atexit.register(cleanUpLockFile, FILE_NAME)

    app = QtWidgets.QApplication(sys.argv)
    dialog = ClientDialog()
    dialog.ui.show()

    HBClient = HeartbeatClient()
    dialog.setHeartbeatClient(HBClient)

    # test if twistd is running (show information and disable connect button ? or allow to kill current connection ??
    # testRunningTwistd(logger,dialog)

    qt5reactor.install()  # imported from file and needed for Qt to function properly in combination with twisted reactor

    from twisted.internet import reactor
    reactor.listenMulticast(8005, MulticastLifeClient(), listenMultiple=True)  #noqa
    reactor.listenUDP(HEARTBEAT_PORT, HBClient)  #noqa
    sys.exit(app.exec_())
