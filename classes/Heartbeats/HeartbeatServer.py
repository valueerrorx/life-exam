from twisted.internet.protocol import DatagramProtocol

from threading import Lock
from time import time, ctime
import logging
from config.config import DEBUG_PIN, HEARTBEAT_PORT, MAX_HEARTBEAT_DELTA_TIME,\
    HEARTBEAT_CLEANUP
from classes.Heartbeats.PeriodicThread.PeriodicThread import PeriodicThread
from classes.Heartbeats.HeartbeatSignalEmitter import HeartbeatSignalEmitter


class HeartBeatDict:
    """ Manage heartbeat dictionary """

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
            # dont do home sweet home
            if "127.0.0.1" not in key:
                if self.beatDict[key] < when:
                    silent.append(key)
        self.dictLock.release()
        return silent


class HeartBeatServer(DatagramProtocol):
    """
    Listen to the heartbeats and detect inactive (silent) clients
    """
    # delta time a client may be silent in sec
    silent_period = MAX_HEARTBEAT_DELTA_TIME
    # auto cleanup intervall in sec
    cleanup = HEARTBEAT_CLEANUP
    abort = False

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.port = HEARTBEAT_PORT
        self.HBDictionary = HeartBeatDict()
        # just a wrapper
        self.emitter = HeartbeatSignalEmitter()

        if DEBUG_PIN != "":
            self.logger.info("HeartBeatServer server listening on port %d" % self.port)
        # check periodic for silent clients
        self.periodic_check = PeriodicThread(self.auto_checkSilentClients, self.cleanup, "HBCleanUp")
        self.periodic_check.start()

    def auto_checkSilentClients(self):
        if DEBUG_PIN != "":
            self.logger.info("AutoCleanUp Heartbeat Server Dictionary ...")
        self.checkSilentClients()

    def checkSilentClients(self):
        """ check for silent clients in dict """
        silent = self.HBDictionary.extractSilentClients(self.silent_period)
        # debug
        silent = ["192.168.1.10", "192.168.1.11"]
        if silent:
            self.emitter.emit(silent)
            if DEBUG_PIN != "":
                self.logger.info(silent)

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
        self.checkSilentClients()

# Testing if Standalone
# hbs = HeartBeatServer(43278)
