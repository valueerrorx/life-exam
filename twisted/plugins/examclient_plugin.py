#! /usr/bin/env python3
# STUDENT - CLIENT #
#
# Copyright (C) 2018 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.

# for debugging run plugin from terminal - only if env_keep += PYTHONPATH is set in "sudoers" file
# export PYTHONPATH="/home/student/.life/applications/life-exam"
# sudo twistd -n --pidfile client.pid examclient -p 11411 -h 10.2.1.251 -i testuser -c 1234

# Log messages only with print(), they are handled by twisted

import os
import shutil
import subprocess
import zipfile
import datetime

from classes import mutual_functions
from config.config import SHARE_DIRECTORY, SAVEAPPS, \
    PRINTERCONFIG_DIRECTORY, WORK_DIRECTORY, EXAMCONFIG_DIRECTORY,\
    CLIENTFILES_DIRECTORY, CLIENTZIP_DIRECTORY
from config.enums import Command, DataType


from classes.client2server import ClientToServer
import time
from classes.Notification.Notification import Notification_Type

from twisted.internet import protocol, defer
from twisted.protocols import basic
from zope.interface import implementer
from twisted.application import internet

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from pathlib import Path
from twisted.internet.task import LoopingCall
from classes.Thread_Countdown import Thread_Countdown
from classes.psUtil import PsUtil
import sys


class MyClientProtocol(basic.LineReceiver):
    def __init__(self, factory, appDir):
        self.factory = factory
        self.client_to_server = self.factory.client_to_server
        self.file_handler = None
        self.buffer = []
        self.line_data_list = ()
        # Path Stuff
        self.rootDir = Path(__file__).parent.parent.parent

        self.notification_path = Path(appDir)
        self.notification_path = self.notification_path.joinpath('classes/Notification')
        # cleans everything and copies script files
        mutual_functions.prepareDirectories()

        # AutoSave open Apps Part ---------------------------------------------
        # which Apps are allready triggered a autosave via xdotool
        self.trigerdAutoSavedIDs = []
        self.detectLoop = None
        self.allSaved = False

    # twisted-Event: Client connects to server
    def connectionMade(self):
        self.buffer = []
        self.file_handler = None
        self.line_data_list = ()
        line = '%s %s %s' % (Command.AUTH.value, self.factory.options['id'], self.factory.options['pincode'])
        self.sendEncodedLine(line)
        self.inform('Authenticated with server ...')

        self.hideConnectedInformation()

    # twisted-Event:
    def connectionLost(self, reason):  #noqa
        self.factory.failcount += 1
        self.file_handler = None
        self.line_data_list = ()
        self.inform("Connection to the server has been lost")

        print("Server Fail #%s" % self.factory.failcount)
        if self.factory.failcount > 2:  # failcount is set to 100 if server refused connection otherwise its slowly incremented
            command = "%s/client/client.py &" % (self.rootDir)
            os.system(command)
            sys.exit(1)

    def _getIndex(self, index, data):
        """ try except Index from Array """
        try:
            return data[index]
        except IndexError:
            return None

    def rawDataReceived(self, data):
        """ twisted-Event: Data received > what should i do? """
        filename = self._getIndex(3, self.line_data_list)
        cleanup_abgabe = self._getIndex(5, self.line_data_list)
        spellcheck = self._getIndex(6, self.line_data_list)

        file_path = os.path.join(self.factory.files_path, filename)
        print('Receiving file chunk (%d KB)' % (len(data)))

        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')

        if data.endswith(b'\r\n'):
            data = data[:-2]
            self.file_handler.write(data)
            self.file_handler.close()
            self.file_handler = None
            self.setLineMode()

            if mutual_functions.validate_file_md5_hash(file_path, self.line_data_list[4]):

                # initialize exam mode.. unzip and start exam
                if self.line_data_list[2] == DataType.EXAM.value:
                    self.inform('Initializing Exam Mode ...')
                    self._startExam(filename, file_path, cleanup_abgabe, spellcheck)

                elif self.line_data_list[2] == DataType.FILE.value:
                    if os.path.isfile(os.path.join(SHARE_DIRECTORY, filename)):
                        filename = "%s-%s" % (filename, datetime.datetime.now().strftime("%H-%M-%S"))  # save with timecode
                        targetpath = os.path.join(SHARE_DIRECTORY, filename)
                        shutil.move(file_path, targetpath)
                    else:
                        shutil.move(file_path, SHARE_DIRECTORY)

                    self.inform('File %s received!' % (filename))

                    mutual_functions.fixFilePermissions(SHARE_DIRECTORY)

                    line = '%s %s' % (Command.FILE_OK.value, self.factory.options['id'])
                    print("Sending File OK: %s" % line)
                    self.sendEncodedLine(line)

                elif self.line_data_list[2] == DataType.PRINTER.value:
                    self.inform('Receiving Printer Configuration')

                    self._activatePrinterconfig(file_path)

            else:
                os.unlink(file_path)
                print('File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename))
        else:
            self.file_handler.write(data)

    # twisted-Event:
    def sendEncodedLine(self, line):
        self.sendLine(line.encode())

    # twisted-Event: A data line has been received
    def lineReceived(self, line):
        """whenever the SERVER sent something """
        # decode the moment you receive a line and encode it right before you send
        line = line.decode()
        self.line_data_list = mutual_functions.clean_and_split_input(line)
        self.line_dispatcher(line)

    def line_dispatcher(self, line):
        print("DEBUG: line received and decoded: %s" % line)
        if len(self.line_data_list) == 0 or self.line_data_list == '':
            return
        """
        FILETRANSFER  (send oder get files)
        command = self.line_data_list[0]
        task = self.line_data_list[1]     (SEND, GET)  (SCREENSHOT, ABGABE, EXAM, FILE, PRINTER)
        filetype= self.line_data_list[2]
        filename = self.line_data_list[3]
        filehash = self.line_data_list[4]
        cleanup_abgabe = client.file_data[5]
        """
        command = {
            Command.ENDMSG.value: self.client_to_server.end_msg,
            Command.REFUSED.value: self.client_to_server.connection_refused,
            Command.REMOVED.value: self.client_to_server.connection_removed,
            Command.FILETRANSFER.value: self.client_to_server.file_transfer_request,
            Command.LOCK.value: self.client_to_server.lock_screen,
            Command.UNLOCK.value: self.client_to_server.un_lock_screen,
            Command.EXITEXAM.value: self.client_to_server.exitExam,
            Command.HEARTBEAT.value: self.client_to_server.heartbeat,
        }

        line_handler = command.get(self.line_data_list[0], None)
        """
        attach "self" (client)
        triggert entweder einen command oder (falls es einfach nur text ist) füllt einen buffer..
        ENDMSG macht diesen dann als deskotp message sichtbar
        """
        line_handler(self) if line_handler is not None else self.buffer.append(line)  # noqa

    def runAndWaittoFinish(self, cmd):
        """Runs a subprocess, and waits for it to finish"""
        stderr = ""
        stdout = ""
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                )
        for line in iter(proc.stderr.readline, b''):
            stderr += line.decode()

        for line in iter(proc.stdout.readline, b''):
            stdout += line.decode()
        # Wait for process to terminate and set the return code attribute
        proc.communicate()

        return [proc.returncode, stderr, stdout]

# Autotrigger Save Part -------------------------------------------------------------------
    def _getArrayAsString(self, arr):
        string = ""
        for val in arr:
            string += val + " "
        return string

    def _isTriggered(self, application_id):
        """ is this ID allready autosav fired? """
        found = False
        for theid in self.trigerdAutoSavedIDs:
            if(theid == application_id):
                found = True
                break
        return found

    def _fireSaveApps(self, pids, app_id_list):
        """
        trigger dbus and xdotool to open apps
        :pids: PIDs from DBus
        :app_id_list: IDs from xdotool
        """
        for app in SAVEAPPS:
            if len(pids) > 0:
                if app == "kate":
                    savetrigger = "file_save_all"
                else:
                    savetrigger = "file_save"
                try:
                    print("dbus Pids: %s" % (self._getArrayAsString(pids)))
                    for pid in pids:
                        prefix = "sudo -E -u student -H"
                        qdbus_command = "%s qdbus org.kde.%s-%s /%s/MainWindow_1/actions/%s trigger" % (prefix, app, pid, app, savetrigger)
                        data = self.runAndWaittoFinish(qdbus_command)  # noqa
                except Exception as error:  # noqa
                    print(error)

        # trigger Auto Save via xdotool but only ONE Time
        if(len(app_id_list) > 0):
            for application_id in app_id_list:  # try to invoke ctrl+s on the running apps
                if(self._isTriggered(application_id) is False):
                    command = "xdotool windowactivate %s && xdotool key ctrl+s &" % (application_id)
                    os.system(command)
                    print("ctrl+s sent to %s" % (application_id))

                    # remember this id
                    self.trigerdAutoSavedIDs.append(application_id)
                else:
                    print("ID %s allready in save State -waiting-" % application_id)

    def _countOpenApps(self):
        """ counts how much apps are open """
        open_apps = 0
        app_id_list = []
        finalPids = []
        for app in SAVEAPPS:
            # these programs are qdbus enabled therefore we can trigger "save" directly from commandline
            found = False
            # DBus -------------------------------------
            command = "pidof %s" % (app)
            data = self.runAndWaittoFinish(command)
            # clean
            p = data[2].replace('\n', '')
            pids = p.split(' ')
            # check for empty data
            for item in pids:
                if(len(item) > 0):
                    finalPids.append(item)
                    open_apps += 1
                    found = True
                    # print("> %s" % app)

            # i dont find it on DBus
            if found is False:
                # xdotool -----------------------------------
                command = "xdotool search --name %s &" % (app)
                app_ids = subprocess.check_output(command, shell=True).decode().rstrip()
                if app_ids:
                    app_ids = app_ids.split('\n')
                    for app_id in app_ids:
                        app_id_list.append(app_id)
                    open_apps += 1
                    # print("xdo > %s" % app)
        return [open_apps, finalPids, app_id_list]

    def _detectOpenApps(self, filename, wait_thread):
        """ counts the open Apps is called periodically by self.detectLoop """
        # [open_apps, pids, app_ids]
        data = self._countOpenApps()
        count = int(data[0])

        print("Offene Apps: %s" % count)
        self._fireSaveApps(data[1], data[2])

        # Fallback abort if user isn't closing apps
        fallback_time = 5 * 60  # 5 min

        # alle 10 sec repeat Message
        if wait_thread.getSeconds() % 10 == 0:
            self.inform("Bitte alle Dateien speichern und die laufenden Programme schließen!", Notification_Type.Warning)

        if((count == 0) or (wait_thread.getSeconds() >= fallback_time)):
            # if there are no more open Apps
            self.detectLoop.stop()
            self.allSaved = True
            finalname = self.create_abgabe_zip(filename)
            self.client_to_server.setZipFileName(finalname)
            # fire Event "We are ready to send the file"
            wait_thread.fireEvent_Done()
            wait_thread.stop()

    def triggerAutosave(self, filename, wait_thread):
        """
        this function uses xdotool to find windows and trigger ctrl + s shortcut on them
        which will show the save dialog the first time and silently save the document the next time
        """
        self.allSaved = False
        # clear Array
        del self.trigerdAutoSavedIDs[:]
        self.trigerdAutoSavedIDs = []
        self.detectLoop = LoopingCall(lambda: self._detectOpenApps(filename, wait_thread))
        self.detectLoop.start(2)
        self.inform("Bitte alle Dateien speichern und die laufenden Programme schließen!", Notification_Type.Warning)

    def create_abgabe_zip(self, filename):
        """Event Save done is ready, now create zip"""
        target_folder = SHARE_DIRECTORY
        output_filename = os.path.join(CLIENTZIP_DIRECTORY, filename)
        # create zip of folder
        print("Anzahl an Files in %s" % target_folder)
        count = mutual_functions.countFiles(target_folder)
        count = int(count[0])
        # create Zip File
        shutil.make_archive(output_filename, 'zip', target_folder)
        if count > 0:
            # this is the filename of the zip file
            return "%s.zip" % filename
        else:
            # create empty Zip File
            return "%s-%s.zip" % (filename, "Empty")
# Autotrigger Save Part END -------------------------------------------------------------------

    def sendFile(self, filename, filetype):
        """send a file to the server"""
        # rebuild here just in case something changed (zip/screenshot created )
        self.factory.files = mutual_functions.get_file_list(self.factory.files_path)

        if filename not in self.factory.files:  # if folder exists
            self.sendLine(b'filename not found in client directory')
            return

        if filetype in DataType.list():
            # command type filename filehash
            line = '%s %s %s %s %s' % (Command.FILETRANSFER.value, filetype, filename, self.factory.files[filename][2], self.factory.options['id'])
            self.sendEncodedLine(line)
        else:
            return None  # inform that nothing has been done

        self.setRawMode()
        # complete filepath as arg
        for bytess in mutual_functions.read_bytes_from_file(self.factory.files[filename][0]):
            self.transport.write(bytess)

        # send this to inform the server that the datastream is finished
        self.transport.write(b'\r\n')
        # When the transfer is finished, we go back to the line mode
        self.setLineMode()
        # print("Filetransfer finished, switched back to LineMode")

    def _activatePrinterconfig(self, file_path):
        """extracts the config folder /etc/cups moves it to /etc restarts cups service"""

        print("stopping cups service")
        command = "systemctl stop cups.service &"
        os.system(command)
        time.sleep(3)

        print("extracting received printer config")
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(PRINTERCONFIG_DIRECTORY)

        os.unlink(file_path)  # delete zip file
        time.sleep(1)

        self.inform('Restarting Cups Printer Service')

        command = "systemctl start cups.service &"
        os.system(command)

        print("fixing printer files permissions")
        command = "chmod 775 /etc/cups -R &"
        os.system(command)

    def _startExam(self, filename, file_path, cleanup_abgabe, spellcheck):
        """
        extracts the config folder and starts the startexam.sh script
        also sets a lock File to indicate that the EXAM started
        """
        # testClient running on the same machine
        if self.factory.options['host'] != "127.0.0.1":
            # create lock File
            mutual_functions.writeLockFile()

            # extract to unzipDIR / clientID / foldername without .zip
            # (cut last four letters #shutil.unpack_archive(file_path, extract_dir, 'tar')
            # python3 only but twisted RPC is not ported to python3 yet
            extract_dir = os.path.join(WORK_DIRECTORY, filename[:-4])
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            os.unlink(file_path)  # delete zip file
            time.sleep(2)

            # add current server IP address to firewall exceptions
            ipstore = os.path.join(EXAMCONFIG_DIRECTORY, "EXAM-A-IPS.DB")
            thisexamfile = open(ipstore, 'a+')  # anhängen
            thisexamfile.write("\n")
            thisexamfile.write("%s:5000" % self.factory.options['host'])   # server IP, port 5000 (twisted)

            command = "chmod +x %s/startexam.sh &" % EXAMCONFIG_DIRECTORY  # make examscript executable
            os.system(command)
            time.sleep(2)
            # start as user even if the twistd daemon is run by root
            command = "sudo %s/startexam.sh %s %s &" % (EXAMCONFIG_DIRECTORY, cleanup_abgabe, spellcheck)
            os.system(command)  # start script
        else:
            return  # running on the same machine.. do not start exam mode / do not copy zip content over original

    def inform(self, msg, ntype=Notification_Type.Information):
        """ print to the log and show a notification """
        print(msg)
        if ntype == Notification_Type.Information:
            stype = "information"
        elif ntype == Notification_Type.Error:
            stype = "error"
        elif ntype == Notification_Type.Warning:
            stype = "warning"
        elif ntype == Notification_Type.Success:
            stype = "success"

        cmd = 'python3 %s/NotificationDispatcher.py "%s" "%s" &' % (self.notification_path, stype, msg)
        os.system(cmd)

    def hideConnectedInformation(self):
        """ hide Connected Info after 5min ... """
        # time in sec
        countdown_thread = Thread_Countdown(None, 5 * 60, self.checkConnectionInfo_and_CloseIt)
        countdown_thread.start()

    def checkConnectionInfo_and_CloseIt(self):
        """ close all Connection Processes """
        print("Killing all ConnectionInformation Processes")
        processUtil = PsUtil()
        pids = processUtil.GetProcessByName("python", "ConnectionStatusDispatcher")
        print(pids)
        for p in pids:
            pid = int(p[0])
            processUtil.killProcess(pid)


class MyClientFactory(protocol.ReconnectingClientFactory):
    # ReconnectingClientFactory tries to reconnect automatically if connection fails
    def __init__(self, files_path, options):
        self.files_path = files_path
        self.options = options
        self.deferred = defer.Deferred()
        self.files = None
        self.failcount = 0
        self.client_to_server = ClientToServer()  # type: ClientToServer
        self.rootDir = self.options["appdirectory"]
        # ReconnectingClientFactory settings
        self.initialDelay = 2  # initial reconnection after 4 s
        self.maxDelay = 10  # maximim delay
        self.factor = 1.2  # A multiplicitive factor by which the delay grows
        self.maxRetries = 10

    # twisted-Event: Called when a connection has failed to connect
    def clientConnectionFailed(self, connector, reason):  #noqa
        self.failcount += 1

        if self.failcount > 3:  # failcount is set to 100 if server refused connection otherwise its slowly incremented
            command = "%s/client/client.py &" % (self.rootDir)
            print(command)
            os.system(command)
            sys.exit(1)

        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    # twisted Method
    def startedConnecting(self, connector):  #noqa
        # Reconnection delays resetting
        self.resetDelay()

    # twisted Method
    def buildProtocol(self, addr):  #noqa
        # http://twistedmatrix.com/documents/12.1.0/api/twisted.internet.protocol.Factory.html#buildProtocol
        return MyClientProtocol(self, self.rootDir)


"""
Um diese Datei als twisted plugin mit twistd -l client.log --pidfile client.pid examclient -p PORT -h HOST starten zu können
muss die ClientFactory im Service (MyServiceMaker) gestartet werden
tapname ist der name des services
damit twistd dieses überall findet sollte das Stammverzeichnis im pythonpath eingetragen werden

export PYTHONPATH=".:/pathto/life-exam-controlcenter:$PYTHONPATH"
"""


# from twisted.application.internet import backoffPolicy    #only with twisted >=16.03
# retryPolicy=backoffPolicy(initialDelay=1, factor=0.5)    # where to put ???


class Options(usage.Options):
    appDir = "/home/student/.life/applications/life-exam/"
    optParameters = [["port", "p", 5000, "The port number to connect to."],
                     ["host", "h", '127.0.0.1', "The host machine to connect to."],
                     ["id", "i", 'unnamed', "A custom unique Client id."],
                     ["pincode", "c", '12345', "The pincode needed for authorization"],
                     ["appdirectory", "d", appDir, "Directory of the Application itself"],
                     ]


@implementer(IServiceMaker, IPlugin)
class MyServiceMaker():
    # see https://twistedmatrix.com/documents/current/core/howto/plugin.html#extending-an-existing-program
    tapname = "examclient"
    description = "LiFE-Exam Client"
    options = Options

    def makeService(self, options):
        return internet.TCPClient(options["host"], int(options["port"]), MyClientFactory(CLIENTFILES_DIRECTORY, options))  #noqa

    def getDescription(self):
        return self.description


serviceMaker = MyServiceMaker()
