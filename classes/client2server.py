 #! /usr/bin/env python3
#
# Copyright (C) 2018 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.

#! /usr/bin/env python
# -*- coding: utf-8 -*-


import time
import os
import subprocess
import shutil
import zipfile


from config.shell_scripts import SHOT
import classes.mutual_functions as mutual_functions
from config.enums import Command, DataType
from config.config import *
import classes.system_commander as system_commander



class ClientToServer:
    """
    Contains functions for Lines sent from the server to the client. 
    call the proper function for the client to react to the servers orders.
    """

    
    def __init__(self):
        self.client = ""

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
        Shoes Desktopmessage for connection refused
        :param client: clientprotocol
        :return:
        """
        mutual_functions.showDesktopMessage('Connection refused!\n Client ID already taken or wrong PIN!')
        client.factory.failcount = 100


    def connection_removed(self,client):
        """
        Shoes Desktopmessage for connection refused
        :param client: clientprotocol
        :return:
        """
        mutual_functions.showDesktopMessage('Connection aborted by the Teacher!')
        client.factory.failcount = 100

    def lock_screen(self, client):
        """Just locks the client screens
        :param client: ClientProtocol
        :return:
        """

        if client.line_data_list[0] == "LKS":
            print("locking screen")

            # check if a serverprocess is running and do not lock screen if any 
            # dirty hack to prevent locking yourself as a teacher when connected at the same time
            answer = subprocess.Popen(["ps aux|grep python3|grep server.py|wc -l"],shell=True, stdout=subprocess.PIPE)
            answer = answer.communicate()[0].strip().decode()
            if not answer <= "1":
                print("prevented locking of the teachers screen")
                return
            
            startcommand = "exec %s/client/lockscreen.py &" %(APP_DIRECTORY) #kill it if it already exists
            os.system(startcommand)
        else:
            print("closing lockscreen")
            startcommand = "exec pkill -9 -f lockscreen.py &"
            os.system(startcommand)
        return



    def exitExam(self, client):
        """start stopexam.sh
        :param client: ClientProtocol
        :return:
        """
        exitcleanup_abgabe = client.line_data_list[1]
        print(exitcleanup_abgabe)
        print("stopping exam")
        startcommand = "%s/scripts/stopexam.sh %s &" %(WORK_DIRECTORY, exitcleanup_abgabe) # start as user even if the twistd daemon is run by root
        os.system(startcommand)  # start script

        return



    def file_transfer_request(self, client):
        """
        Decides if a GET or a SEND operation needs to be dispatched and unboxes relevant attributes to be used in the actual sending/receiving functions
        :param client: ClientProtocol
        :param line: Line received from server
        :return:
        """

        trigger = client.line_data_list[0]
        task = client.line_data_list[1]
        filetype = client.line_data_list[2]
        filename = client.line_data_list[3]
        file_hash = client.line_data_list[4]
        cleanup_abgabe = client.line_data_list[5]
        
        if task == Command.SEND.value:
            if filetype == DataType.SCREENSHOT.value:
                finalfilename = self.prepare_screenshot(client, filename)
            elif filetype == DataType.ABGABE.value:
                finalfilename = self.prepare_abgabe(client, filename)
            client._sendFile(finalfilename, filetype)
        else:   # this is a GET file request - switch to RAW Mode
            client.setRawMode()
            
            
        



    """
    prepare filetype
    """
    def prepare_screenshot(self, client, filename):
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

    def prepare_abgabe(self, client, filename):
        """
        Prepares Abgabe to be sent as zip archive
        :param client: clientprotocol
        :param filename: filename of abgabe archive
        :return: filename
        """
        print("ABGABE IS PREPARED")
        client._triggerAutosave()
        time.sleep(2)  # TODO: make autosave return that it is finished!
        target_folder = SHARE_DIRECTORY
        output_filename = os.path.join(CLIENTZIP_DIRECTORY, filename )
        shutil.make_archive(output_filename, 'zip', target_folder)  # create zip of folder
        return "%s.zip" % filename  # this is the filename of the zip file



