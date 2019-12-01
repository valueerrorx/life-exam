'''
@author: Mag. Stefan Hagmann
'''

from twisted.internet import reactor, protocol

import logging
from twisted.python import log

from config.config import *

logger = logging.getLogger('twistedServer')

class Upperprotocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.count += 1
        self.transport.write('Hi! Send me the text to Uppercase!\n')
    
    def connectionLost(self, reason):
        self.factory.count -= 1

    def dataReceived(self, data):
        self.transport.write(data.upper())
        self.transport.loseConnection()


class CountingFactory(protocol.ServerFactory):
    protocol = Upperprotocol
    count = 0    

def start_server():
    """ Main method, starts a Twisted Server """
    observer = log.PythonLoggingObserver(loggerName='twistedServer')
    observer.start()
    
    logger.info("Twisted server started on Port %s" % (SERVER_PORT))
    log.msg("PythonLoggingObserver hooked up", logLevel=logging.DEBUG)
    
    reactor.listenTCP(SERVER_PORT, CountingFactory())
    reactor.run
    
    
    
    
start_server()