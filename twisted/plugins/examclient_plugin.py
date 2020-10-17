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
from config.config import SHARE_DIRECTORY, SAVEAPPS, USER,\
    PRINTERCONFIG_DIRECTORY, WORK_DIRECTORY, EXAMCONFIG_DIRECTORY,\
    CLIENTFILES_DIRECTORY
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

    # twisted-Event: Client connects to server
    def connectionMade(self):
        self.buffer = []
        self.file_handler = None
        self.line_data_list = ()
        line = '%s %s %s' % (Command.AUTH.value, self.factory.options['id'], self.factory.options['pincode'])
        self.sendEncodedLine(line)
        self.inform('Authentication with server ...')

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
            os._exit(1)

    def rawDataReceived(self, data):
        """ twisted-Event: Data received > what should i do? """
        print(self.line_data_list)
        filename = self.line_data_list[3]
        cleanup_abgabe = self.line_data_list[5]
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

                    self._startExam(filename, file_path, cleanup_abgabe)

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

    def _triggerAutosave(self):
        """
        this function uses xdotool to find windows and trigger ctrl+s shortcut on them
        which will show the save dialog the first time and silently save the document the next time
        """
        app_id_list = []
        for app in SAVEAPPS:
            if app == "calligrawords" or app == "calligrasheets" or app == "kate":  # these programs are qdbus enabled therefore we can trigger "save" directly from commandline
                if app == "kate":
                    savetrigger = "file_save_all"
                else:
                    savetrigger = "file_save"
                try:
                    command = "pidof %s" % (app)
                    pids = subprocess.check_output(command, shell=True).decode().rstrip()
                    print(pids)
                    pids = pids.split(' ')
                    print(pids)
                    for pid in pids:
                        qdbuscommand = "runuser -u %s -- qdbus org.kde.%s-%s /%s/MainWindow_1/actions/%s trigger" % (USER, app, pid, app, savetrigger)
                        print(qdbuscommand)
                        os.system(qdbuscommand)
                except:
                    print("program not running")

            else:  # make a list of the other running apps
                command = "xdotool search --name %s &" % (app)
                app_ids = subprocess.check_output(command, shell=True).decode().rstrip()
                if app_ids:
                    app_ids = app_ids.split('\n')
                    for app_id in app_ids:
                        app_id_list.append(app_id)

        for application_id in app_id_list:  # try to invoke ctrl+s on the running apps
            command = "xdotool windowactivate %s && xdotool key ctrl+s &" % (application_id)
            os.system(command)
            print("ctrl+s sent to %s" % (application_id))

        # try the current active window too in order to catch other applications not in config.py
        # command = "xdotool getactivewindow && xdotool key ctrl+s &"   #this is bad if you want to watch with console
        # os.system(command)

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

    def _startExam(self, filename, file_path, cleanup_abgabe):
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

            command = "chmod +x %s/startexam.sh &" % EXAMCONFIG_DIRECTORY  # make examscritp executable
            os.system(command)
            time.sleep(2)
            startcommand = "%s/startexam.sh %s &" % (EXAMCONFIG_DIRECTORY, cleanup_abgabe)  # start as user even if the twistd daemon is run by root
            os.system(startcommand)  # start script
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
            os._exit(1)

        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    # twisted Method
    def startedConnecting(self, connector):
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
damit twistd dieses überallfindet sollte das stammverzeichnis im pythonpath eingetragen werden

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
class MyServiceMaker(object):
    # see https://twistedmatrix.com/documents/current/core/howto/plugin.html#extending-an-existing-program
    tapname = "examclient"
    description = "LiFE-Exam Client"
    options = Options

    def makeService(self, options):
        return internet.TCPClient(options["host"], int(options["port"]), MyClientFactory(CLIENTFILES_DIRECTORY, options))  #noqa


serviceMaker = MyServiceMaker()
