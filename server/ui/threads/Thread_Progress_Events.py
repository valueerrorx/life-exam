#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import os
from config.config import SHARE_DIRECTORY
import classes.mutual_functions as mutual_functions
import logging

logger = logging.getLogger(__name__)


def client_abgabe_done(parent, who):
    """
    will fired when Client has sent his Abgabe File
    :autoAbgabe: 1/0 is that a AutoAbgabe event?
    """
    # event fired in MyServerProtocol
    item = parent.get_list_widget_by_client_name(who)
    logger.info("Client %s has finished sending Files ..." % item.getID())

    # set the status Icon
    item.setExamIconOFF()

    parent.networkProgress.decrement()
    if parent.networkProgress.value() <= 1:
       
        # if there is an animation showing
        parent.workinganimation.stop()
    # resume Heartbeats again
    parent.resumeHeartbeats()


def client_received_file_done(parent, clientWidget):
    """ will be fired, if a client has received a file that was sent by server """
    # event fired in MyServerProtocol
    logger.info("Client %s has received a file ..." % clientWidget.getName())
    # set the status Icon
    clientWidget.setFileReceivedOK()
    parent.networkProgress.decrement()
    if parent.networkProgress.value() <= 1:
        # if there is an animation showing
        parent.workinganimation.stop()
    # resume Heartbeats again
    parent.resumeHeartbeats()


def client_abgabe_done_exit_exam(parent, who, autoAbgabe):
    """ 
    will fired when Client has sent his Abgabe File
    :autoAbgabe: 1/0 is that a AutoAbgabe event?
    """
    # Checkbox
    onexit_cleanup_abgabe = parent.ui.exitcleanabgabe.checkState()
    spellcheck = parent.ui.spellcheck.checkState()

   
    # then send the exam exit signal
    parent.factory.server_to_client.exit_exam(who, onexit_cleanup_abgabe, spellcheck)

    parent.networkProgress.decrement()
    if parent.networkProgress.value() <= 1:
         # show in Filemanager only if we manually trigger Abgabe
        if autoAbgabe == '0':
            logger.info("Opening FileManager..")
            mutual_functions.openFileManager(os.path.join(SHARE_DIRECTORY))
        # if there is an animation showing
        parent.workinganimation.stop()
    # resume Heartbeats again
    parent.resumeHeartbeats()


def client_lock_screen(parent):
    """ will be fired when client locks the screen """
    parent.networkProgress.decrement()
    # print("ProgressBar: %s" % parent.networkProgress.value() )
    if parent.networkProgress.value() <= 1:
        # if there is an animation showing
        parent.workinganimation.stop()
        parent.onScreenshots("all")


def client_unlock_screen(parent):
    """ will be fired when client unlocks the screen """
    parent.networkProgress.decrement()
    if parent.networkProgress.value() <= 1:
        # if there is an animation showing
        parent.workinganimation.stop()
        parent.onScreenshots("all")
