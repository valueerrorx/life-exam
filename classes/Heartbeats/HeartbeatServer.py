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

    # equals to __toString() from Java
    def __repr__(self):
        data = ''
        self.dictLock.acquire()
        for key in self.beatDict.keys():
            data = "%sIP address: %s - Last time: %s\n" % (
                data, key, ctime(self.beatDict[key]))
        self.dictLock.release()
        return data

    def update(self, entry):
        """Create or update a dictionary entry"""
        self.dictLock.acquire()
        self.beatDict[entry] = time()
        self.dictLock.release()

    def extractSilentClients(self, delta_time):
        """
        Returns a list of entries older than delta_time in sec
        :return: ['192.168.3.4', sec]
        """
        silent = []
        now = time()
        when = now - delta_time  # jetzt - Intervall alles was davor liegt ist tot
        self.dictLock.acquire()
        for key in self.beatDict.keys():
            # print("%s: %s" % (key, now-self.beatDict[key]))
            # dont do home sweet home
            if "127.0.0.1" not in key:
                if self.beatDict[key] < when:
                    silent.append([key, round(now - self.beatDict[key])])
        self.dictLock.release()
        return silent


class HeartBeatServer(DatagramProtocol):
    """
    Listen to the heartbeats and detect inactive (silent) clients
    """
    # delta time a client may be silent in sec
    silent_period = MAX_HEARTBEAT_DELTA_TIME
    # auto cleanup intervall in sec
    cleanup_interval = HEARTBEAT_CLEANUP
    abort = False

    def __init__(self, main_ui):
        self.logger = logging.getLogger(__name__)
        self.port = HEARTBEAT_PORT
        self.HBDictionary = HeartBeatDict()
        # the main UI
        self.main_ui = main_ui
        # just a wrapper, pass Main UI to perform Signals to it
        self.emitter = HeartbeatSignalEmitter(self.main_ui)

        if DEBUG_PIN != "":
            self.logger.info("HeartBeatServer server listening on port %d" % self.port)
        # check periodic for silent clients
        self.periodic_check = PeriodicThread(self.auto_checkSilentClients, self.cleanup_interval, "HBCleanUp")
        self.periodic_check.start()

    def auto_checkSilentClients(self):
        # if DEBUG_PIN != "":
        #    self.logger.info("AutoCleanUp Heartbeat Server Dictionary ...")
        self.checkSilentClients()

    def checkSilentClients(self):
        """ check for silent clients in dict """
        silent = self.HBDictionary.extractSilentClients(self.silent_period)
        if silent:
            self.emitter.emitSilentClients(silent)
            if DEBUG_PIN != "":
                self.logger.info(silent)
        # send also an Signal to check wich clients has marked as ONline
        self.emitter.emitcheckOnlineClients(silent)

    # Twisted Part ##################################################

    def startProtocol(self):
        "Called when transport is connected"
        pass

    def stopProtocol(self):
        "Called after all transport is teared down"
        pass

    def datagramReceived(self, data, addr):  # noqa
        "Receive UDP packets, log them in heartbeat dictionary"
        # self.logger.info("Received packet from %s > %s" % (addr[0], data.decode()))
        self.HBDictionary.update(addr[0])
        self.checkSilentClients()

# Testing if Standalone
# hbs = HeartBeatServer(43278)
