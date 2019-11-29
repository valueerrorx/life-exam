'''
Created on 29.11.2019

@author: Mag. Stefan Hagmann
'''

from twisted.web import proxy, http
from twisted.internet import reactor

#Logging with Rotating
from twisted.python import log
from twisted.python.logfile import DailyLogFile

import sys

class ProxyFactory(http.HTTPFactory):
    protocol = proxy.Proxy

def runTwistedServer():
    """ Main method of the Thread """
    #Twisted Logging
    #log.startLogging(DailyLogFile.fromFullPath("foo.log"))
    #log.startLogging(sys.stdout)
    reactor.listenTCP(8080, ProxyFactory())
    reactor.run()
