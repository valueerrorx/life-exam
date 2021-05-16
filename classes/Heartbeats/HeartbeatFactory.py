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


class HeartbeatFactory(protocol.ServerFactory):
    def __init__(self, files_path, reactor, splash, app):

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
