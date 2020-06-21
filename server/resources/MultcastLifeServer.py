#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from twisted.internet.protocol import DatagramProtocol
from config.config import DEBUG_PIN


class MultcastLifeServer(DatagramProtocol):

    def __init__(self, factory):
        self.factory = factory
        self.logger = logging.getLogger(__name__)

    def startProtocol(self):
        """Called after protocol has started listening. """
        self.transport.setTTL(5)     # Set the TTL>1 so multicast will cross router hops:
        self.transport.joinGroup("228.0.0.5")   # Join a specific multicast group:

    def datagramReceived(self, datagram, address):
        datagram = datagram.decode()

        if "CLIENT" in datagram:
            # Rather than replying to the group multicast address, we send the
            # reply directly (unicast) to the originating port:
            if DEBUG_PIN != "":
                self.logger.info("Datagram %s received from %s" % (repr(datagram), repr(address)))

            serverinfo = self.factory.examid + " " + " ".join(self.factory.disconnected_list)
            message = "SERVER %s" % serverinfo
            self.transport.write(message.encode(), ("228.0.0.5", 8005))

            # self.transport.write("SERVER: Assimilate", address)  #this is NOT WORKINC
