#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from pathlib import Path

# add application root to python path for imports at position 0
sys.path.insert(0, Path(__file__).parent.parent.parent.as_posix())

from server.resources.MultcastLifeServer import MultcastLifeServer
from server.ui.ServerUI import ServerUI

from config.config import DEBUG_PIN
from classes.server2client import ServerToClient
from classes import mutual_functions

from twisted.internet import protocol
from twisted.internet.task import LoopingCall

from server.resources.MyServerProtocol import MyServerProtocol




class MyServerFactory(protocol.ServerFactory):
    def __init__(self, files_path, reactor, splash, app):
        """
        :param splash: the Splashscreen started in Main Application
        :param app: the main QApplication
        """
        self.logger = logging.getLogger(__name__)
        self.files_path = files_path
        self.reactor = reactor
        self.server_to_client = ServerToClient()  # type: ServerToClient
        self.files = None
        self.clientslocked = False
        '''
        this is set to True the moment the server sends examconfig,
        sends file, sends printconf, requests abgabe, requests screenshot
        '''
        self.rawmode = False
        self.pincode = mutual_functions.generatePin(4)

        # only debug if DEBUG_PIN is not ""
        if DEBUG_PIN != "":
            self.pincode = DEBUG_PIN
            self.logger.info("DEBUGGING Mode")

        self.examid = self.createExamId()
        self.window = ServerUI(self, splash, app)
        self.lc = LoopingCall(lambda: self.window.onAbgabe("all", True))
        self.lcs = LoopingCall(lambda: self.window.onScreenshots("all"))

        intervall = self.window.ui.ssintervall.value()

        if intervall != 0:
            self.window.log("<b>Changed Screenshot Intervall to %s seconds </b>" % (str(intervall)))
            self.lcs.start(intervall)
        else:
            self.window.log("<b>Screenshot Intervall is set to 0 - Screenshotupdate deactivated</b>")

        #  onAbgabe() kann durch lc.start(intevall) im intervall ausgeführt werden

        # mutual_functions.checkFirewall(self.window.get_firewall_adress_list())  # deactivates all iptable rules if any
        # starting multicast server here in order to provide "factory" information via broadcast
        self.reactor.listenMulticast(8005, MultcastLifeServer(self), listenMultiple=True)

    def createExamId(self):
        return "Exam-%s" % mutual_functions.generatePin(3)

    """
    https://twistedmatrix.com/documents/current/api/twisted.internet.protocol.Factory.html
    """
    # twisted Method
    def buildProtocol(self, addr):  # noqa
        """
        wird bei einer eingehenden client connection aufgerufen
        erstellt ein object der Klasse MyServerProtocol für jede connection und übergibt self (die factory)
        """
        return MyServerProtocol(self)
