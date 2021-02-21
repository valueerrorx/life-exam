#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.

import sys
from pathlib import Path
import os
from config.config import SCRIPTS_DIRECTORY,\
    CLIENTSCREENSHOT_DIRECTORY, SHARE_DIRECTORY, EXAMCONFIG_DIRECTORY
from time import sleep
from classes.Thread_Wait import Thread_Wait


# add application root to python path for imports at position 0
sys.path.insert(0, Path(__file__).parent.parent.as_posix())

from config.shell_scripts import SHOT
import classes.mutual_functions as mutual_functions
from config.enums import Command, DataType


class ClientToServer:
    """
    Contains functions for Lines sent from the server to the client.
    call the proper function for the client to react to the servers orders.
    """

    def __init__(self):
        self.client = ""
        # rootDir of Application
        self.rootDir = Path(__file__).parent.parent
        self.zipFileName = None

    def _getIndex(self, index, data):
        """ try except Index from Array """
        try:
            return data[index]
        except IndexError:
            return None

    def end_msg(self, client):
        """
        Shows Desktop popup of received message
        :param client: clientprotocol
        :return:
        """
        message = '%s' % ' '.join(map(str, client.buffer))
        mutual_functions.showDesktopMessage(message)
        client.buffer = []

    def connection_refused(self, client):
        """
        Shows Desktopmessage for connection refused
        :param client: clientprotocol
        :return:
        """
        mutual_functions.showDesktopMessage('Connection refused!\n Client ID already taken or wrong PIN!')
        client.factory.failcount = 100

    def connection_removed(self, client):
        """
        Shows Desktopmessage for connection refused
        :param client: clientprotocol
        :return:
        """
        mutual_functions.showDesktopMessage('Connection aborted by the Teacher!')
        client.factory.failcount = 100

    def heartbeat(self, client):
        """send Heartbeat to Server"""
        cID = client.line_data_list[1]
        line = '%s %s' % (Command.HEARTBEAT_BEAT.value, cID)
        client.sendEncodedLine(line)

    def un_lock_screen(self, client):
        """
        Just UNlock the client screen and send OK
        :param client: ClientProtocol
        """
        cID = client.line_data_list[1]
        # prevent locking yourself as a teacher when connected at the same time
        if mutual_functions.checkPidFile("server"):
            # True > I'm the Teacher nothing to do
            return
        startcommand = "exec pkill -9 -f lockscreen.py &"
        os.system(startcommand)

        # create an Screenshot
        self.prepare_screenshot("%s.jpg" % cID)

        # Send OK i'm UNlocked to Server
        line = '%s %s' % (Command.UNLOCKSCREEN_OK.value, cID)
        print("Sending UN-Lock Screen OK")
        client.sendEncodedLine(line)
        return

    def lock_screen(self, client):
        """
        Just lock the client screen and send OK
        :param client: ClientProtocol
        """
        cID = client.line_data_list[1]
        # prevent locking yourself as a teacher when connected at the same time
        if mutual_functions.checkPidFile("server"):
            # True > I'm the Teacher nothing to do
            return

        startcommand = "exec %s/client/resources/lockscreen.py &" % (self.rootDir)  # kill it if it already exists
        os.system(startcommand)

        # wait a bit
        sleep(1)

        # create an Screenshot
        self.prepare_screenshot("%s.jpg" % cID)

        # Send OK i'm locked to Server
        line = '%s %s' % (Command.LOCKSCREEN_OK.value, cID)
        print("Sending Lock Screen OK")
        client.sendEncodedLine(line)

        return

    def exitExam(self, client):
        """
        start stopexam.sh
        :param client: ClientProtocol
        :return:
        """
        exitcleanup_abgabe = self._getIndex(1, client.line_data_list)
        spellcheck = self._getIndex(2, client.line_data_list)
        print("=========================== Stopping EXAM ===========================")
        # start as user even if the twistd daemon is run by root
        startcommand = "%s/lockdown/stopexam.sh %s %s &" % (EXAMCONFIG_DIRECTORY, exitcleanup_abgabe, spellcheck)
        print(startcommand)
        os.system(startcommand)

    def file_transfer_request(self, client):
        """
        Decides if a GET or a SEND operation needs to be dispatched and unboxes relevant attributes to be used in the actual sending/receiving functions
        :param client: ClientProtocol
        :param line: Line received from server
        :return:
        """
        trigger = client.line_data_list[0]  # noqa
        task = client.line_data_list[1]
        filetype = client.line_data_list[2]
        filename = client.line_data_list[3]
        file_hash = client.line_data_list[4]  # noqa
        cleanup_abgabe = client.line_data_list[5]  # noqa

        if task == Command.SEND.value:
            if filetype == DataType.SCREENSHOT.value:
                finalfilename = self.prepare_screenshot(filename)
                client.sendFile(finalfilename, filetype)

            elif filetype == DataType.ABGABE.value:
                wait_thread = Thread_Wait()
                wait_thread.finished_signal.connect(lambda: self._sendZipFile(client, filetype))
                wait_thread.start()

                # zip Files send signal when done to _sendZipFile
                self.prepare_abgabe(client, filename, wait_thread)
        else:   # this is a GET file request - switch to RAW Mode
            client.setRawMode()

    def _sendZipFile(self, client, filetype):
        """ signal received send the file """
        try:
            if "-Empty".lower() not in self.zipFileName.lower():
                print("Abgabe ZipFile: %s" % self.zipFileName)                
            else:
                print("Abgabe: No Data to send, because nothing in %s!" % (SHARE_DIRECTORY))
                print("We send an empty Zip File to Server ...")
                # to inform Server, we send a empty File
                # client.setLineMode()
                # print("Filetransfer finished, switched back to LineMode")
            client.sendFile(self.zipFileName, filetype)
        except Exception:
            # maybe a triggered stop from Server, do nothing
            print("Exception in _sendZipFile: %s" % self.zipFileName)

    def setZipFileName(self, name):
        """ the name of the Zip File to send """
        self.zipFileName = name

    """ prepare filetype """
    def prepare_screenshot(self, filename):
        """
        Prepares a screenshot to be sent
        :param client: clientprotocol
        :param filename: screenshot filename
        :return: filename
        """
        scriptfile = os.path.join(SCRIPTS_DIRECTORY, SHOT)
        screenshotfile = os.path.join(CLIENTSCREENSHOT_DIRECTORY, filename)
        command = "%s %s" % (scriptfile, screenshotfile)
        print(command)
        os.system(command)
        print("SCREENSHOT IS PREPARED")
        return filename

    def prepare_abgabe(self, client, filename, wait_thread):
        """
        Prepares Files to be send as zip archive if there a files
        :param client: clientprotocol
        :param filename: filename of abgabe archive
        :return: filename or None
        """
        self.zipFileName = None  # be sure
        client.triggerAutosave(filename, wait_thread)
