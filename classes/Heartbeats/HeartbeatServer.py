from twisted.internet.protocol import DatagramProtocol

from threading import Lock
from time import time, ctime
import logging
from config.config import DEBUG_PIN, HEARTBEAT_PORT
from PyQt5.Qt import pyqtSignal


class HeartBeatDict:
    "Manage heartbeat dictionary"

    def __init__(self):
        self.beatDict = {}
        if __debug__:
            self.beatDict['127.0.0.1'] = time()
        self.dictLock = Lock()

    def __repr__(self):
        data = ''
        self.dictLock.acquire()
        for key in self.beatDict.keys():
            data = "%sIP address: %s - Last time: %s\n" % (
                data, key, ctime(self.beatDict[key]))
        self.dictLock.release()
        return data

    def update(self, entry):
        "Create or update a dictionary entry"
        self.dictLock.acquire()
        self.beatDict[entry] = time()
        self.dictLock.release()

    def extractSilentClients(self, howPast):
        "Returns a list of entries older than howPast"
        silent = []
        when = time() - howPast
        self.dictLock.acquire()
        for key in self.beatDict.keys():
            if self.beatDict[key] < when:
                silent.append(key)
        self.dictLock.release()
        return silent


class HeartBeatServer(DatagramProtocol):
    """
    Listen to the heartbeats and detect inactive (silent) clients
    """
    period = 30
    # Signal with silent Clients
    silentClientList_Signal = pyqtSignal(list)

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.port = HEARTBEAT_PORT
        self.HBDictionary = HeartBeatDict()

        if DEBUG_PIN != "":
            self.logger.info("HeartBeatServer server listening on port %d" % self.port)

    # Twisted Part ##################################################

    def startProtocol(self):
        "Called when transport is connected"
        pass

    def stopProtocol(self):
        "Called after all transport is teared down"
        pass

    def datagramReceived(self, data, addr):
        "Receive UDP packets, log them in heartbeat dictionary"
        if DEBUG_PIN != "":
            self.logger.info("Received packet from %s > %s" % (addr[0], data.decode()))
        self.HBDictionary.update(addr[0])

        silent = self.HBDictionary.extractSilentClients(self.period)
        if silent:
            self.silentClientList_Signal.emit(silent)
            if DEBUG_PIN != "":
                self.logger.info(silent)

# hbs = HeartBeatServer(43278)
