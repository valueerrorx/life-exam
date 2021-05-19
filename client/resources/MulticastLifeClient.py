#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall

import classes.mutual_functions as mutual_functions
from classes.Event import Event


class MulticastLifeClient(DatagramProtocol):
    def __init__(self):
        self.loopObj = None
        self.server_ip = "0.0.0.0"
        self.info = None

        self.logger = logging.getLogger(__name__)

    def startProtocol(self):
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(5)
        self.transport.joinGroup("228.0.0.5")        # Join the multicast address, so we can receive replies:
        self.loopObj = LoopingCall(self._sendProbe)  # continuously send probe for exam server
        self.loopObj.start(2, now=False)             # wait 2 sec between calls, False start after first wait time

    def datagramReceived(self, datagram, address):
        datagram = datagram.decode()

        if "SERVER" in datagram:
            self.server_ip = address[0]
            self.info = mutual_functions.clean_and_split_input(datagram)

            # fire Event to Dialog
            Event('updateGUI', self)
            self.logger.info("Datagram %s received from %s" % (repr(datagram), repr(address)))


    def _sendProbe(self):  #noqa
        """ Send to 228.0.0.5:8005 - all listeners on the multicast address
            (including us) will receive this message.
        """
        try:
            self.transport.write(b'CLIENT: Looking', ("228.0.0.5", 8005))
        except Exception as e:
            self.logger.error("an exception occurred")
            self.logger.error(e)
