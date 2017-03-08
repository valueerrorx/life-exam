#! /usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import uic, QtWidgets

import time

from PyQt5.QtGui import QPixmap
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall

from PyQt5.QtGui import QIcon, QColor
import sys
import os

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # add application root to python path for imports

import qt5reactor
from common import checkIP, prepareDirectories, clean_and_split_input
from config.config import *


class ClientDialog(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.examserver = dict()
        self._initUi()
        prepareDirectories()

    def _initUi(self):
        self.ui = uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), "student.ui"))
        self.ui.setWindowIcon(QIcon("pixmaps/security.png"))
        self.ui.exit.clicked.connect(self._onAbbrechen)  # setup Slots
        self.ui.start.clicked.connect(self._onStartExamClient)
        self.ui.serverdropdown.currentIndexChanged.connect(self._updateIP)
        self.ui.studentid.textChanged.connect(lambda: self._changePalette(self.ui.studentid, 'ok'))
        self.ui.studentid.setFocus()
        self.ui.serverip.textChanged.connect(lambda: self._changePalette(self.ui.serverip,'ok'))
        self.ui.pincode.textChanged.connect(lambda: self._changePalette(self.ui.pincode,'ok'))





    def _onAbbrechen(self):  # Exit button
        self.ui.close()

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
                clientkillscript = os.path.join(SCRIPTS_DIRECTORY, "terminate-exam-process.sh")
                os.system("sudo %s %s" % (clientkillscript, 'client'))  # make sure only one client instance is running per client

                command = "kdesudo 'twistd -l %s/client.log --pidfile %s/client.pid examclient -p %s -h %s -i %s -c %s' &" % (
                    WORK_DIRECTORY, WORK_DIRECTORY, SERVER_PORT, SERVER_IP, ID, PIN)
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

    def _updateServerlist(self):
        """updates the dropdownmenu if new servers are found"""
        self.ui.serverdropdown.clear()
        for server in self.examserver:
            self.ui.serverdropdown.addItem(server)

    def _updateIP(self):
        """updates the ip address fiel according to the selection in the dropdownmenu """
        current = self.ui.serverdropdown.currentText()
        self.ui.serverip.setText(self.examserver.get(current) )





class MulticastLifeClient(DatagramProtocol):
    def __init__(self):
        self.loopObj = None
        self.server_ip = "0.0.0.0"
        self.info = None

    def startProtocol(self):
        self.transport.joinGroup("228.0.0.5")   # Join the multicast address, so we can receive replies:
        self.loopObj = LoopingCall(self._sendProbe)  # continuously send probe for exam server
        self.loopObj.start(2, now=False)

    def datagramReceived(self, datagram, address):
        if "SERVER" in datagram:
            self.server_ip = address[0]
            self.info = clean_and_split_input(datagram)
            self.disconnected_clients = self.info[2:]
            self.completer = QtWidgets.QCompleter(self.disconnected_clients)
            dialog.ui.studentid.setCompleter(self.completer)

            if self.info[1] not in dialog.examserver:   #if this is a new server name 
                for key in dialog.examserver:
                    ip = dialog.examserver.get(key)
                    if ip == self.server_ip:            #check if the same ip is already there (server just got renamed)
                        dialog.examserver.pop(key)      #remove old entry
                        break

                dialog.examserver.update({ self.info[1] : str(address[0]) })   #add new entry
                dialog._updateServerlist()      #update gui

            dialog.ui.serversearch.setText("Server Found!")
            dialog.ui.servercheck.setPixmap(QPixmap("pixmaps/checked.png"))
            print "Datagram %s received from %s" % (repr(datagram), repr(address))

    def _sendProbe(self):
        """ Send to 228.0.0.5:8005 - all listeners on the multicast address
            (including us) will receive this message.
        """
        self.transport.write('CLIENT: Looking', ("228.0.0.5", 8005))



app = QtWidgets.QApplication(sys.argv)
dialog = ClientDialog()
dialog.ui.show()
qt5reactor.install()  # imported from file and needed for Qt to function properly in combination with twisted reactor
from twisted.internet import reactor
reactor.listenMulticast(8005, MulticastLifeClient(), listenMultiple=True)
sys.exit(app.exec_())
