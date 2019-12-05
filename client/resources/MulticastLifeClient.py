 #! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall

import classes.mutual_functions as mutual_functions
from client.resources.Event import Event

class MulticastLifeClient(DatagramProtocol):
    def __init__(self):
        self.loopObj = None
        self.server_ip = "0.0.0.0"
        self.info = None
        
        self.logger = logging.getLogger(__name__)

    def startProtocol(self):
        self.transport.joinGroup("228.0.0.5")        # Join the multicast address, so we can receive replies:
        self.loopObj = LoopingCall(self._sendProbe)  # continuously send probe for exam server
        self.loopObj.start(2, now=False)             # wait 2 sec between calls, False start after first wait time

    def datagramReceived(self, datagram, address):
        datagram = datagram.decode()
        
        if "SERVER" in datagram:
            self.server_ip = address[0]
            self.info = mutual_functions.clean_and_split_input(datagram)
            
            #fire Event to Dialog
            Event('updateGUI',self.info, self.server_ip)
            self.logger.info("Datagram %s received from %s" % (repr(datagram), repr(address)) )
            
            #Stop Listening?
            #self.loopObj.stop()
            #self.logger.info("STOP" )
    

    def _sendProbe(self):
        """ Send to 228.0.0.5:8005 - all listeners on the multicast address
            (including us) will receive this message.
        """
        try:
            self.transport.write(b'CLIENT: Looking', ("228.0.0.5", 8005))
        except Exception as e:
            self.logger.error("an exception occurred")
            self.logger.error(e)
