#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.

import time
import shutil
import sys
from pathlib import Path
import os
from config.config import WORK_DIRECTORY, SCRIPTS_DIRECTORY,\
    CLIENTSCREENSHOT_DIRECTORY, SHARE_DIRECTORY, CLIENTZIP_DIRECTORY

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

    """
    student actions
    """

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

    def lock_screen(self, client):
        """
        Just locks the client screen
        :param client: ClientProtocol
        """
        if client.line_data_list[0] == Command.LOCK.value:
            cID = client.line_data_list[1]
            # check if a serverprocess is running and do not lock screen if any
            # check for server.pid in ~/.life/EXAM
            # dirty hack to prevent locking yourself as a teacher when connected at the same time

            if mutual_functions.checkPidFile("server"):
                # True > Im the Teacher
                print("client2server: Prevented locking of the teachers screen [server.pid found]")
                return
            # answer = subprocess.Popen(["ps aux|grep python3|grep server.py|wc -l"], shell=True, stdout=subprocess.PIPE)
            # answer = answer.communicate()[0].strip().decode()

            # Send OK i'm locked to Server
            line = '%s %s' % (Command.LOCKSCREEN_OK.value, cID)
            print("Sending Lock Screen OK")
            client.sendEncodedLine(line)

            startcommand = "exec %s/client/resources/lockscreen.py &" % (self.rootDir)  # kill it if it already exists
            os.system(startcommand)
        else:
            startcommand = "exec pkill -9 -f lockscreen.py &"
            os.system(startcommand)

            # Send OK i'm UNlocked to Server
            line = '%s %s' % (Command.UNLOCKSCREEN_OK.value, cID)
            print("Sending UN-Lock Screen OK")
            client.sendEncodedLine(line)
        return

    def exitExam(self, client):
        """start stopexam.sh
        :param client: ClientProtocol
        :return:
        """
        exitcleanup_abgabe = client.line_data_list[1]
        print(exitcleanup_abgabe)
        print("Stopping EXAM")
        startcommand = "%s/scripts/stopexam.sh %s &" % (WORK_DIRECTORY, exitcleanup_abgabe)  # start as user even if the twistd daemon is run by root
        os.system(startcommand)  # start script

        return

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
                client._sendFile(finalfilename, filetype)

            elif filetype == DataType.ABGABE.value:
                # Abgabe nur senden, wenn ein EXAM gestartet wurde ansonsten Fake.zip File
                # teste ob lock file exists

                fakeit = not mutual_functions.lockFileExists()
                finalfilename = self.prepare_abgabe(client, filename, fakeit)
                print("Abgabe-File: %s" % finalfilename)
                client._sendFile(finalfilename, filetype)
        else:   # this is a GET file request - switch to RAW Mode
            client.setRawMode()

    """ prepare filetype """
    def prepare_screenshot(self, filename):
        """
        Prepares a screenshot to be sent
        :param client: clientprotocol
        :param filename: screenshot filename
        :return: filename
        """
        print("SCREENSHOT IS PREPARED")
        scriptfile = os.path.join(SCRIPTS_DIRECTORY, SHOT)
        screenshotfile = os.path.join(CLIENTSCREENSHOT_DIRECTORY, filename)
        command = "%s %s" % (scriptfile, screenshotfile)
        os.system(command)
        return filename

    def prepare_abgabe(self, client, filename, fake):
        """
        Prepares Abgabe to be sent as zip archive
        :param client: clientprotocol
        :param filename: filename of abgabe archive
        :param fake: if no EXAM Mode was started, then create dummy zip File
        :return: filename
        """
        if fake is False:
            print("Abgabe IS Prepared ...")
            client._triggerAutosave()
            time.sleep(2)  # TODO: make autosave return that it is finished!
            target_folder = SHARE_DIRECTORY
            output_filename = os.path.join(CLIENTZIP_DIRECTORY, filename)
            shutil.make_archive(output_filename, 'zip', target_folder)  # create zip of folder
        else:
            print("No EXAM, Fake Abgabe IS Prepared ...")
            mutual_functions.createFakeZipFile()
            filename = "dummy"

        return "%s.zip" % filename  # this is the filename of the zip file
