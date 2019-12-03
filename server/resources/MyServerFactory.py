 #! /usr/bin/env python3
# -*- coding: utf-8 -*-

from twisted.internet import protocol
from twisted.internet.protocol import DatagramProtocol
from twisted.protocols import basic
from twisted.internet.task import LoopingCall

from classes.server2client import *

from server.resources.MultcastLifeServer import *
from server.ui.ServerUI import *

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import QRegExp

class MyServerFactory(protocol.ServerFactory):

    def __init__(self, files_path, reactor):
        self.files_path = files_path
        self.reactor = reactor
        self.server_to_client = ServerToClient() # type: ServerToClient
        self.disconnected_list = []
        self.files = None
        self.clientslocked = False
        self.rawmode = False;  #this is set to True the moment the server sends examconfig, sends file, sends printconf, requests abgabe, requests screenshot
        self.pincode = mutual_functions.generatePin(4)
        self.examid = "Exam-%s" % mutual_functions.generatePin(3)
        self.window = ServerUI(self)                            # type: ServerUI
        self.lc = LoopingCall(lambda: self.window._onAbgabe("all"))
        self.lcs = LoopingCall(lambda: self.window._onScreenshots("all"))
        
        intervall = self.window.ui.ssintervall.value()

        if intervall is not 0:
            self.window.log("<b>Changed Screenshot Intervall to %s seconds </b>" % (str(intervall)))
            self.lcs.start(intervall)
        else:
            self.window.log("<b>Screenshot Intervall is set to 0 - Screenshotupdate deactivated</b>")
        
        
        # _onAbgabe kann durch lc.start(intevall) im intervall ausgeführt werden

        #mutual_functions.checkFirewall(self.window.get_firewall_adress_list())  # deactivates all iptable rules if any
        #starting multicast server here in order to provide "factory" information via broadcast
        self.reactor.listenMulticast(8005, MultcastLifeServer(self), listenMultiple=True)

    """
    http://twistedmatrix.com/documents/12.1.0/api/twisted.internet.protocol.Factory.html#buildProtocol
    """
    def buildProtocol(self, addr):
        return MyServerProtocol(self)
        """
        wird bei einer eingehenden client connection aufgerufen - erstellt ein object der klasse MyServerProtocol für jede connection und übergibt self (die factory)
        """