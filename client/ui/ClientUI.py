#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import time

from pathlib import Path

from classes.Observers import Observers
from config.config import EXAMCONFIG_DIRECTORY, SCRIPTS_DIRECTORY,\
    WORK_DIRECTORY, DEBUG_PIN, DEBUG_ID, USER, SERVER_PORT
from classes.mutual_functions import checkIP, prepareDirectories,\
    changePermission

from PyQt5.QtCore import QRegExp, Qt
from PyQt5 import QtWidgets, uic

from PyQt5.QtGui import QIcon, QRegExpValidator, QPixmap, QColor
from classes.psUtil import PsUtil


class ClientDialog(QtWidgets.QDialog, Observers):

    def __init__(self):
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
        self.ui.studentid.setFocus()
        # self.ui.serverip.textChanged.connect(lambda: self._changePalette(self.ui.serverip,'ok'))
        self.ui.pincode.textChanged.connect(lambda: self._changePalette(self.ui.pincode, 'ok'))
        self.ui.serverip.hide()
        self.ui.keyPressEvent = self.newOnkeyPressEvent

        char_regex = QRegExp("[a-z-A-Z\-_]+")   # only allow specif characters in textfields
        char_validator = QRegExpValidator(char_regex)
        self.ui.studentid.setValidator(char_validator)

        num_regex = QRegExp("[0-9_]+")
        num_validator = QRegExpValidator(num_regex)
        self.ui.pincode.setValidator(num_validator)

        # detect changing of userdata, only needed if debugging is active
        self.inputs_changed = False

        self.checkConnectionInfo_and_CloseIt()

    def checkConnectionInfo_and_CloseIt(self):
        '''is there an active connection Info on desktop? > close it'''
        processUtil = PsUtil()
        pids = processUtil.GetProcessByName("python", "ConnectionStatusDispatcher")
        for p in pids:
            pid = int(p[0])
            processUtil.killProcess(pid)

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
        self.msg = QtWidgets.QMessageBox()
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
            startcommand = "%s/startexam.sh &" % (EXAMCONFIG_DIRECTORY)  # start as user even if the twistd daemon is run by root
            os.system(startcommand)  # start script
        else:
            self.msg = False

    def _on_offline_exam_exit(self):
        startcommand = "%s/stopexam.sh &" % (SCRIPTS_DIRECTORY)
        os.system(startcommand)  # start script

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

                # moved this to workdirectory because configdirectory is overwritten on exam start
                namefile = os.path.join(WORK_DIRECTORY, "myname.txt")
                try:
                    openednamefile = open(namefile, 'w+')  # create new file
                    openednamefile.write("%s" % (ID))
                    changePermission(namefile, "777")
                except IOError:
                    self.logger.error("Can't create myname.txt")

                from twisted.plugin import IPlugin, getPlugins
                # Update the cache system
                # see https://twistedmatrix.com/documents/current/core/howto/plugin.html
                list(getPlugins(IPlugin))

                # for item in plgs:
                #    print(item)
                # print(sys.path)

                # port, host, id, pincode, application_dir
                command = "twistd -l %s/client.log --pidfile %s/client.pid examclient -p %s -h %s -i %s -c %s -d %s &" % (WORK_DIRECTORY, WORK_DIRECTORY, SERVER_PORT, SERVER_IP, ID, PIN, self.rootDir)
                self.logger.info(command)
                os.system(command)
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
        self.inputs_changed = True

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
