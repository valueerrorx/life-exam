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

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # add application root to python path for imports

import qt5reactor
from common import checkIP, prepareDirectories
from config.config import *


class ClientDialog(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self._initUi()
        prepareDirectories()

    def _initUi(self):
        self.ui = uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), "student.ui"))
        self.ui.setWindowIcon(QIcon("pixmaps/security.png"))
        self.ui.exit.clicked.connect(self._onAbbrechen)  # setup Slots
        self.ui.start.clicked.connect(self._onStartExamClient)

    def _onAbbrechen(self):  # Exit button
        self.ui.close()

    def _onStartExamClient(self):
        SERVER_IP = self.ui.serverip.text()
        ID = self.ui.studentid.text()
        if checkIP(SERVER_IP):
            palettedefault = self.ui.serverip.palette()
            palettedefault.setColor(self.ui.serverip.backgroundRole(), QColor(255, 255, 255))
            self.ui.serverip.setPalette(palettedefault)
            if ID != "":
                self.ui.close()
                clientkillscript = os.path.join(SCRIPTS_DIRECTORY, "terminate-exam-process.sh")
                os.system("sudo %s %s" % (clientkillscript, 'client'))  # make sure only one client instance is running per client

                command = "kdesudo 'twistd -l %s/client.log --pidfile %s/client.pid examclient -p %s -h %s -i %s' &" % (
                    WORK_DIRECTORY, WORK_DIRECTORY, SERVER_PORT, SERVER_IP, ID)

                os.system(command)
            palettewarn = self.ui.studentid.palette()
            palettewarn.setColor(self.ui.studentid.backgroundRole(), QColor(200, 80, 80))
            self.ui.studentid.setPalette(palettewarn)
        else:
            palettewarn = self.ui.serverip.palette()
            palettewarn.setColor(self.ui.serverip.backgroundRole(), QColor(200, 80, 80))
            self.ui.serverip.setPalette(palettewarn)


class MulticastLifeClient(DatagramProtocol):
    def __init__(self):
        self.loopObj = None
        self.server_found = False
        self.server_ip = "0.0.0.0"

    def startProtocol(self):
        # Join the multicast address, so we can receive replies:
        self.transport.joinGroup("228.0.0.5")
        # Send to 228.0.0.5:8005 - all listeners on the multicast address
        # (including us) will receive this message.
        self.loopObj = LoopingCall(self._sendProbe)
        self.loopObj.start(2, now=False)

    def datagramReceived(self, datagram, address):
        if "CLIENT" not in datagram:
            if not self.server_found:
                self.loopObj.stop()

            self.server_found = True
            self.server_ip = address[0]
            dialog.ui.serverip.setText(str(address[0]))
            dialog.ui.serversearch.setText("Server Found!")
            dialog.ui.servercheck.setPixmap(QPixmap("pixmaps/checked.png"))

        print "Datagram %s received from %s" % (repr(datagram), repr(address))

    def _sendProbe(self):
        self.transport.write('CLIENT: Looking', ("228.0.0.5", 8005))


app = QtWidgets.QApplication(sys.argv)
dialog = ClientDialog()
dialog.ui.show()

qt5reactor.install()  # imported from file and needed for Qt to function properly in combination with twisted reactor

from twisted.internet import reactor

reactor.listenMulticast(8005, MulticastLifeClient(), listenMultiple=True)

sys.exit(app.exec_())
