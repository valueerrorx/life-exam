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
from config.config import WORK_DIRECTORY, DEBUG_PIN

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
import argparse


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


def cleanUp(file):
    """ at client shutdown, delete the lock File """
    if os.path.exists(file):
        os.remove(file)


def readExtraPIDFile(fname):
    """ any other started processes? """
    pids = []
    filename = os.path.join(WORK_DIRECTORY, fname)
    try:
        with open(filename, 'r') as fh:
            for line in fh:
                pids.append(int(line))
        return pids
    except IOError:
        return []


def killRunningClientProcesses():
    """ kills all started Programms like Heartbeatclient , Pid is readed from PID File """
    pFName = "client_extras.pid"
    pids = readExtraPIDFile(pFName)
    psutil = PsUtil()
    for p in pids:
        if DEBUG_PIN != "":
            logger.info("Killing process %s" % p)
        # Try to kill Processes
        psutil.killProcess(p)
    # delete PIDFile
    filename = os.path.join(WORK_DIRECTORY, pFName)
    if os.path.exists(filename):
        os.remove(filename)


def checkRunningPID():
    """ check id the PID from Lock File is still active, if not then delete LockFile """
    f = open(FILE_NAME, "r")
    pid = f.read()
    ps = PsUtil()
    if ps.isRunning(pid) is False:
        # old Process is dead
        cleanUp(FILE_NAME)
        logger.info("Deleted Client Zombie Process Lock File ...")
        return False
    return True


def read_cli_args():
    """ Read the command line args passed to the script """
    # see https://www.golinuxcloud.com/python-argparse/
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--restart',
                        default=False,
                        action='store_true',
                        dest="restarted",
                        help='is the Client Restarted?'
                        )
    args = parser.parse_args()

    if args.restarted is True:
        # if client is started from examclient_plugin, than delete running PID's
        killRunningClientProcesses()


if __name__ == '__main__':
    rootDir = Path(__file__).parent.parent
    FILE_NAME = rootDir.joinpath("client/started_client.lock")

    logger = logging.getLogger(__name__)
    configure_logging(False)       # True is Server

    # do not start twice
    if os.path.exists(FILE_NAME):
        if checkRunningPID() is True:
            logger.info("Client Process found, exiting now ...")
            sys.exit(0)
    else:
        logger.info('Lock File created: Preventing starting twice ...')
        lockFile(FILE_NAME)

    atexit.register(cleanUp, FILE_NAME)

    read_cli_args()

    app = QtWidgets.QApplication(sys.argv)
    dialog = ClientDialog()
    dialog.ui.show()

    # test if twistd is running (show information and disable connect button ? or allow to kill current connection ??
    # testRunningTwistd(logger,dialog)

    qt5reactor.install()  # imported from file and needed for Qt to function properly in combination with twisted reactor

    from twisted.internet import reactor
    reactor.listenMulticast(8005, MulticastLifeClient(), listenMultiple=True)  #noqa

    sys.exit(app.exec_())
