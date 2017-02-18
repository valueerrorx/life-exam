#! /usr/bin/env python
# -*- coding: utf-8 -*-
# STUDENT - CLIENT #

import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # add application root to python path for imports

import shutil
import zipfile
import time

from twisted.internet import reactor, protocol, stdio, defer
from twisted.protocols import basic
from common import *
from config import *
from config.enums import DataType, Command
from dispatch.line_dispatch_student import student_line_dispatcher

from twisted.application.internet import TCPClient
# from twisted.application.service import Application

from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker


class MyClientProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.delimiter = '\n'
        self.file_handler = None
        self.buffer = []
        self.file_data = ()
        prepareDirectories()  # cleans everything and copies script files 

    # twisted
    def connectionMade(self):
        self.buffer = []
        self.file_handler = None
        self.file_data = ()
        self.sendLine('%s %s' % (Command.AUTH, self.factory.options['id']))
        print('Connected to the server')
        showDesktopMessage('Connected to the server')

    # twisted
    def connectionLost(self, reason):
        self.factory.failcount += 1
        self.file_handler = None
        self.file_data = ()
        print('Connection to the server has been lost')
        showDesktopMessage('Connection to the server has been lost')

        if self.factory.failcount > 3:  # failcount is set to 100 if server refused connection otherwise its slowly incremented
            command = "python client/student.py &"
            os.system(command)
            os._exit(1)

    # twisted
    def rawDataReceived(self, data):
        filename = self.file_data[3]
        file_path = os.path.join(self.factory.files_path, filename)
        print('Receiving file chunk (%d KB)' % (len(data)))

        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')

        while not data.endswith("\r\n"):
            self.file_handler.write(data)

        data = data[:-2]
        self.file_handler.write(data)
        self.file_handler.close()
        self.file_handler = None
        self.setLineMode()

        if validate_file_md5_hash(file_path, self.file_data[4]):
            print('File %s has been successfully transfered and saved' % (filename))

            if self.file_data[2] == "EXAM":  # initialize exam mode.. unzip and start exam
                showDesktopMessage('Initializing Exam Mode')
                self._startExam(filename, file_path)
            elif self.file_data[2] == "FILE":
                # FIXME try if destination already exists - save with timecode
                showDesktopMessage('File received!')
                shutil.move(file_path, ABGABE_DIRECTORY)
                fixFilePermissions(ABGABE_DIRECTORY)
        else:
            os.unlink(file_path)
            print('File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename))

    # twisted
    def lineReceived(self, line):
        line_handler = student_line_dispatcher.get(line.split()[0], None)
        line_handler(self, line) if line_handler is not None else self.buffer.append(line)

    def _triggerAutosave(self):
        """this function uses xdotool to find windows and trigger ctrl+s shortcut on them
            which will show the save dialog the first time and silently save the document the next time
        """
        app_id_list = []
        for app in SAVEAPPS:
            if app == "calligrawords" or app == "calligrasheets":  # these programs are qdbus enabled therefore we can trigger "save" directly from commandline
                try:
                    command = "pidof %s" % (app)
                    pid = subprocess.check_output(command, shell=True).rstrip()
                    qdbuscommand = "qdbus org.kde.%s-%s /%s/MainWindow_1/actions/file_save trigger" % (app, pid, app)
                    os.system(qdbuscommand)
                except:
                    print "program not running"

            else:  # make a list of the other running apps
                command = "xdotool search --name %s &" % (app)
                app_ids = subprocess.check_output(command, shell=True).rstrip()
                if app_ids:
                    app_ids = app_ids.split('\n')
                    for app_id in app_ids:
                        app_id_list.append(app_id)

        for application_id in app_id_list:  # try to invoke ctrl+s on the running apps
            command = "xdotool windowactivate %s && xdotool key ctrl+s &" % (application_id)
            os.system(command)
            print "ctrl+s sent to %s" % (application_id)

        # try the current active window too in order to catch other applications not in config.py
        command = "xdotool getactivewindow && xdotool key ctrl+s &"
        os.system(command)

    def _sendFile(self, filename, filetype):
        """send a file to the server"""
        self.factory.files = get_file_list(
            self.factory.files_path)  # rebuild here just in case something changed (zip/screensho created )
        if not filename in self.factory.files:  # if folder exists
            self.sendLine('filename not found in client directory')
            return

        if filetype in vars(DataType).values():
            self.transport.write(
                '%s %s %s %s\n' % (Command.FILETRANSFER, filetype, filename, self.factory.files[filename][2])) # command type filename filehash
        else:
            return  # TODO: inform that nothing has been done

        self.setRawMode()
        for bytes in read_bytes_from_file(self.factory.files[filename][0]):  # complete filepath as arg
            self.transport.write(bytes)
        self.transport.write('\r\n')  # send this to inform the server that the datastream is finished
        self.setLineMode()  # When the transfer is finished, we go back to the line mode 

    def _startExam(self, filename, file_path):
        """extracts the config folder and starts the startexam.sh script"""

        if self.factory.options['host'] != "127.0.0.1":  # testClient running on the same machine
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
            thisexamfile.write(self.factory.options['host'])

            command = "sudo chmod +x %s/startexam.sh &" % EXAMCONFIG_DIRECTORY  # make examscritp executable
            os.system(command)
            time.sleep(2)
            startcommand = "sudo %s/startexam.sh exam &" % EXAMCONFIG_DIRECTORY  # start as user even if the twistd daemon is run by root
            os.system(startcommand)  # start script
        else:
            return  # running on the same machine.. do not start exam mode / do not copy zip content over original


class MyClientFactory(protocol.ReconnectingClientFactory):
    # ReconnectingClientFactory tries to reconnect automatically if connection fails
    def __init__(self, files_path, options):
        self.files_path = files_path
        self.options = options
        self.deferred = defer.Deferred()
        self.files = None
        self.failcount = 0
        self.delay

    def buildProtocol(self, addr):
        # http://twistedmatrix.com/documents/12.1.0/api/twisted.internet.protocol.Factory.html#buildProtocol
        return MyClientProtocol(self)


"""
Um diese Datei als twisted plugin mit twistd -l client.log --pidfile client.pid examclient -p PORT -h HOST starten zu können 
muss die ClientFactory im Service (MyServiceMaker) gestartet werden
tapname ist der name des services 
damit twistd dieses überallfindet sollte das stammverzeichnis im pythonpath eingetragen werden

export PYTHONPATH="/pathto/life-exam-controlcenter:$PYTHONPATH"


"""


# from twisted.application.internet import backoffPolicy    #only with twisted >=16.03
# retryPolicy=backoffPolicy(initialDelay=1, factor=0.5)    # where to put ???


class Options(usage.Options):
    optParameters = [["port", "p", 5000, "The port number to connect to."],
                     ["host", "h", '127.0.0.1', "The host machine to connect to."],
                     ["id", "i", 'unnamed', "A custom unique Client id."]
                     ]


class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "examclient"
    description = "Exam Client"
    options = Options

    def makeService(self, options):
        return TCPClient(options["host"],
                         int(options["port"]),
                         MyClientFactory(CLIENTFILES_DIRECTORY, options))


serviceMaker = MyServiceMaker()
