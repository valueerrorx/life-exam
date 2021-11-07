#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import time

from pathlib import Path

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QIcon, QRegExpValidator, QPixmap, QColor


from config.config import EXAMCONFIG_DIRECTORY, WORK_DIRECTORY, DEBUG_PIN, DEBUG_ID, USER, SERVER_PORT,\
    HEARTBEAT_INTERVALL, HEARTBEAT_PORT

from classes.Observers import Observers
from classes.mutual_functions import checkIP, prepareDirectories,\
    changePermission
from classes.psUtil import PsUtil
from PyQt5.Qt import QTimer


class ClientDialog(QtWidgets.QDialog, Observers):
    """ A dialog """

    CLIENT_PID_FILE = "client_extras.pid"

    def __init__(self):  # noqa 
        QtWidgets.QDialog.__init__(self)

        self.logger = logging.getLogger(__name__)
        uic.uiparser.logger.setLevel(logging.INFO)
        uic.properties.logger.setLevel(logging.INFO)

        # rootDir of Application
        self.rootDir = Path(__file__).parent.parent.parent

        self.examserver = dict()
        self.disconnected_clients = dict()
        self.completer = QtWidgets.QCompleter()
        self.completerlist = []
        self._initUi()
        prepareDirectories()

    def _initUi(self):
        # Register self to Global Observer List Object
        Observers.__init__(self)
        # Register event
        self.observe('updateGUI', self.updateGUI)

        self.scriptdir = os.path.dirname(os.path.abspath(__file__))
        uifile = self.rootDir.joinpath('client/client.ui')
        self.ui = uic.loadUi(uifile)

        iconfile = self.rootDir.joinpath('pixmaps/windowicon.png').as_posix()
        self.ui.setWindowIcon(QIcon(iconfile))

        # only debug if DEBUG_PIN is not ""
        if DEBUG_PIN != "":
            self.ui.setWindowTitle(".: DEBUG MODE :. - LiFE Exam - .: DEBUG MODE :.")
            debug_css = "QDialog{ background: #ffffbf; }"
            self.ui.setStyleSheet(debug_css)
        else:
            self.ui.setWindowTitle("LiFE Exam")

        self.ui.exit.clicked.connect(self._onAbbrechen)  # setup3 Slots
        self.ui.start.clicked.connect(self._onStartExamClient)
        self.ui.offlineexam.clicked.connect(self._on_offline_exam)
        self.ui.offlineexamexit.clicked.connect(self._on_offline_exam_exit)
        self.ui.serverdropdown.currentIndexChanged.connect(self._updateIP)
        self.ui.serverdropdown.activated.connect(self._updateIP)
        self.ui.studentid.textChanged.connect(lambda: self._changePalette(self.ui.studentid, 'ok'))
        self.ui.studentid.returnPressed.connect(self._onStartExamClient)
        self.ui.pincode.setFocus()
        # self.ui.serverip.textChanged.connect(lambda: self._changePalette(self.ui.serverip,'ok'))
        self.ui.pincode.textChanged.connect(lambda: self._changePalette(self.ui.pincode, 'ok'))
        self.ui.serverip.hide()
        self.ui.keyPressEvent = self.newOnkeyPressEvent

        char_regex = QRegExp(r"[a-z-A-Z\-_]+")   # only allow specif characters in textfields
        char_validator = QRegExpValidator(char_regex)
        self.ui.studentid.setValidator(char_validator)

        num_regex = QRegExp("[0-9_]+")
        num_validator = QRegExpValidator(num_regex)
        self.ui.pincode.setValidator(num_validator)

        # detect changing of userdata, only needed if debugging is active
        self.inputs_changed = False

        self.testRunningTwistd()
        self.checkConnectionInfo_and_CloseIt()

    def testRunningTwistd(self):
        """ if a running twistd client is found > kill it """
        processUtil = PsUtil()
        pid = processUtil.GetProcessByName("twistd3")
        if len(pid) > 0:
            self.ui.status.setText("Connection daemon already running!")
            self.ui.start.setText("Kill connection")

            self.ui.start.clicked.disconnect()
            self.ui.start.clicked.connect(self.killRunningTwistd)

    def clearStatusMessage(self):
        self.ui.status.setText("")

    def showNhide(self, msg, time=2000):
        """ show a Status Message and hide it after some time """
        self.ui.status.setText(msg)
        QTimer.singleShot(time, self.clearStatusMessage)

    def killRunningTwistd(self):
        """ if a running twistd client is found > kill it """
        processUtil = PsUtil()
        pid = processUtil.GetProcessByName("twistd3")
        if len(pid) > 0:
            # found a twistd process, kill all pids
            for p in pid:
                try:
                    # only kills as root
                    processUtil.killProcess(int(p[0]))
                except Exception as e:
                    self.logger.error(e)

            self.ui.start.setText("Verbinden")
            self.showNhide("Terminated existing connection")
            self.ui.start.clicked.disconnect()
            self.ui.start.clicked.connect(self._onStartExamClient)

    def checkConnectionInfo_and_CloseIt(self):
        '''is there an active connection Info on desktop? > close it'''

        processUtil = PsUtil()
        pids = processUtil.GetProcessByName("ConnectionStatusDispatcher")
        for p in pids:
            pid = int(p[0])
            processUtil.killProcess(pid)
        # benötigt sudo Password wenn mit nachfolgender Zeile, daher obige Lösung
        # os.system("sudo pkill -f ConnectionStatusDispatcher")

    def newOnkeyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.logger.info("Close-Event triggered ...")

    def closeEvent(self, evnt):
        evnt.ignore()
        self._onAbbrechen()

    def _onAbbrechen(self):  # Exit button
        # if in root mode than change log Files to student User
        print("root?: uid: %s" % os.getuid())
        if os.getuid() == 0:
            # root has uid = 0
            os.system("cd %s && chown %s:%s *.log" % (self.rootDir, USER, USER))
        self.ui.close()
        print("-Exit-")

    def updateGUI(self, multicast_client):
        """
        Event Update from Observeable MultiCastClient
        """
        data = multicast_client.info
        server_ip = multicast_client.server_ip

        # { servername : ['clientname1','clientname2'] }
        self.disconnected_clients.update({data[1]: data[2:]})
        # if this is a new server name
        if data[1] not in self.examserver:
            for key in self.examserver:
                ip = self.examserver.get(key)
                if ip == server_ip:               # check if the same ip is already there (server just got renamed)
                    self.examserver.pop(key)      # remove old entry
                    break

            self.examserver.update({data[1]: str(server_ip)})    # add new entry
            self._updateServerlist()                             # update gui

        self.ui.serversearch.setText("Server Found!")
        icon = self.rootDir.joinpath("pixmaps/checked.png").as_posix()
        self.ui.servercheck.setPixmap(QPixmap(icon))

        # reduce Multicast Period from 2 to 5sec
        multicast_client.loopObj.stop()
        multicast_client.loopObj.start(5, now=False)

        # only debug if DEBUG_PIN is not ""
        if DEBUG_PIN != "":
            if self.inputs_changed is False:
                ID = DEBUG_ID
                PIN = DEBUG_PIN
                self.ui.studentid.setText(ID)
                self.ui.pincode.setText(PIN)
                # print("Update: %s %s" % (ID, PIN))

    def _on_offline_exam(self):
        self.msg = QtWidgets.QMessageBox()  # noqa
        self.msg.setIcon(QtWidgets.QMessageBox.Information)
        self.msg.setText("Wollen sie in den abgesicherten Exam Modus wechseln?")
        self.msg.setDetailedText("Die automatische Abgabe,\nScreenlock, senden und empfangen von Dateien\nund andere Funktionen sind in diesem Modus nicht verfügbar.")
        self.msg.setWindowTitle("LiFE Exam")
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        retval = self.msg.exec_()   # 16384 = yes, 65536 = no

        if str(retval) == "16384":
            command = "chmod +x %s/startexam.sh &" % EXAMCONFIG_DIRECTORY  # make exam script executable
            os.system(command)
            time.sleep(2)
            startcommand = "sudo -E %s/startexam.sh &" % (EXAMCONFIG_DIRECTORY)  # start as user even if the twistd daemon is run by root
            os.system(startcommand)  # start script
        else:
            self.msg = False  # noqa

    def _on_offline_exam_exit(self):
        startcommand = "sudo -E %s/lockdown/stopexam.sh &" % (EXAMCONFIG_DIRECTORY)
        os.system(startcommand)  # start script

    def writeExtraPIDFile(self, pids):
        filename = os.path.join(WORK_DIRECTORY, self.CLIENT_PID_FILE)
        try:
            f = open(filename, 'w+')  # create new file
            for p in pids:
                f.write("%s\n" % (p))
            f.close()
            changePermission(filename, "777")
        except IOError:
            self.logger.error("Can't create file %s" % filename)

    def _onStartExamClient(self):
        SERVER_IP = self.ui.serverip.text()
        ID = self.ui.studentid.text()
        PIN = self.ui.pincode.text()

        if checkIP(SERVER_IP):
            if ID == "":
                self._changePalette(self.ui.studentid, "warn")
            elif PIN == "":
                self._changePalette(self.ui.pincode, "warn")
            else:
                self.ui.close()

                # show Connected Information -------------------
                path = os.path.join(self.rootDir, "classes/ConnectionStatus/ConnectionStatusDispatcher.py")
                exam = self.ui.serverdropdown.currentText()
                # 1 = connected
                cmd = 'python3 %s "%s" "%s" &' % (path, 1, exam)
                os.system(cmd)

                from twisted.plugin import IPlugin, getPlugins
                # Update the cache system
                # see https://twistedmatrix.com/documents/current/core/howto/plugin.html
                list(getPlugins(IPlugin))

                # for item in plgs:
                #    print(item)
                # print(sys.path)
                processUtil = PsUtil()
                pids = []
                # Start Heartbeat Client ------------------------------------
                # examclient_plugin connectionLost() is starting client.py again with parameter -r
                # that means kill the running HeratbeatClient
                client_path = self.rootDir.joinpath("classes", "Heartbeats").as_posix()
                # ip, port, interval
                command = "python3 %s/HeartbeatClient.py %s %s %s &" % (client_path, SERVER_IP, HEARTBEAT_PORT, HEARTBEAT_INTERVALL)
                os.system(command)
                if DEBUG_PIN != "":
                    self.logger.debug(command)

                # Start Twisted Client ---------------------------------------
                # port, host, id, pincode, application_dir
                command = "sudo -E twistd3 -l %s/client.log --pidfile %s/client.pid examclient -p %s -h %s -i %s -c %s -d %s &" % (WORK_DIRECTORY, WORK_DIRECTORY, SERVER_PORT, SERVER_IP, ID, PIN, self.rootDir)
                os.system(command)
                if DEBUG_PIN != "":
                    self.logger.debug(command)

                # search for running PIDS for Client
                # Heartbeat Client Connection Info
                pid = processUtil.GetProcessByName("HeartbeatClient")
                for p in pid:
                    pids.append(p[0])
                if DEBUG_PIN != "":
                    self.logger.debug("** HeartbeatClient Pid: %s" % pid)

                pid = processUtil.GetProcessByName("ConnectionStatusDispatcher")
                for p in pid:
                    pids.append(p[0])
                if DEBUG_PIN != "":
                    self.logger.debug("** ConnectionStatusDispatcher Pid: %s" % pid)
                # remember active PID's from extra programs started by the client
                self.writeExtraPIDFile(pids)

                # Kill ConnectionStatusDispatcher, we don't need it during exam
                # we dont remove it from stored PID's twice ist better ;)
                processUtil.killProcess(p[0])
        else:
            self._changePalette(self.ui.serverip, "warn")

    def _changePalette(self, item, reason):
        if reason == 'warn':
            palettewarn = item.palette()
            palettewarn.setColor(item.backgroundRole(), QColor(160, 80, 80))
            item.setPalette(palettewarn)
        else:
            palettedefault = item.palette()
            palettedefault.setColor(item.backgroundRole(), QColor(255, 255, 255))
            item.setPalette(palettedefault)
        self.inputs_changed = True  # noqa

    def _updateServerlist(self):
        """updates the dropdownmenu if new servers are found"""
        self.ui.serverdropdown.clear()
        for server in self.examserver:
            self.ui.serverdropdown.addItem(server)

    def _updateIP(self):
        """updates the ip address fiel according to the selection in the dropdownmenu """
        current = self.ui.serverdropdown.currentText()
        self.ui.serverip.setText(self.examserver.get(current))

        self.completerlist = self.disconnected_clients.get(current)  # gets a list from the dict
        self.completer = QtWidgets.QCompleter(self.completerlist)
        self.ui.studentid.setCompleter(self.completer)
