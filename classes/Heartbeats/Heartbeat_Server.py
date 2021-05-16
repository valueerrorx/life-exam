""" PyHeartBeat server: receives and tracks UDP packets from all clients.

While the BeatLog thread logs each UDP packet in a dictionary, the main
thread periodically scans the dictionary and prints the IP addresses of the
clients that sent at least one packet during the run, but have
not sent any packet since a time longer than the definition of the timeout.
"""

from socket import socket, AF_INET, SOCK_DGRAM
from threading import Lock, Thread, Event
from time import time, ctime
import logging
from config.config import DEBUG_PIN
import threading
from PyQt5.Qt import pyqtSignal


class BeatDict:
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

    def extractSilent(self, howPast):
        "Returns a list of entries older than howPast"
        silent = []
        when = time() - howPast
        self.dictLock.acquire()
        for key in self.beatDict.keys():
            if self.beatDict[key] < when:
                silent.append(key)
        self.dictLock.release()
        return silent


class BeatRecorder(Thread):
    "Receive UDP packets, log them in heartbeat dictionary"
    def __init__(self, goOnEvent, updateDictFunc, port):
        Thread.__init__(self)
        self.goOnEvent = goOnEvent
        self.updateDictFunc = updateDictFunc
        self.port = port
        self.recSocket = socket(AF_INET, SOCK_DGRAM)
        self.recSocket.bind(('', port))

    def __repr__(self):
        return "Heartbeat Server on port: %d\n" % self.port

    def getAddress_Port(self, data):
        return "%s:%s" % (data[0], data[1])

    def run(self):
        while self.goOnEvent.isSet():
            data, addr = self.recSocket.recvfrom(6)

            if DEBUG_PIN != "":
                self.logger.info("Received packet from %s > %s" % (self.getAddress_Port(addr), data.decode()))
            self.updateDictFunc(addr[0])


class HeartBeatServer(Thread):
    """
    Starts the Heartbeat Server
    Listen to the heartbeats and detect inactive clients
    """
    period = 30
    # Signal with silent Clients
    silentClientList_Signal = pyqtSignal(list)

    def __init__(self, port):
        self.logger = logging.getLogger(__name__)
        Thread.__init__(self)
        self.port = port
        self.abort = False
        self.e = threading.Event()

        self.beatRecGoOnEvent = Event()
        self.beatRecGoOnEvent.set()
        self.beatDictObject = BeatDict()
        beatRecordThread = BeatRecorder(self.beatRecGoOnEvent, self.beatDictObject.update, self.port)
        beatRecordThread.start()
        if DEBUG_PIN != "":
            self.logger.info("PyHeartBeat server listening on port %d" % self.port)
        self.start()

    def run(self):
        while self.abort is False:
            if __debug__:
                print(self.beatDictObject)
            silent = self.beatDictObject.extractSilent(self.period)
            if silent:
                self.silentClientList_Signal.emit(silent)
                if DEBUG_PIN != "":
                    self.logger.info(silent)
            self.e.wait(timeout=self.period)   # instead of time.sleep()

    def stop(self):
        """ Stop the Thread """
        self.beatRecGoOnEvent.clear()
        self.beatRecThread.join()
        self.abort = True
        # interrupt sleep
        self.e.set()


# hbs = HeartBeatServer(43278)
