from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
import logging
from config.config import DEBUG_PIN
import threading


class HeartbeatClient(Thread):
    """
    PyHeartBeat client: sends an UDP packet to a given server every x seconds.
    PyHBClient.py serverip [udpport]
    """

    period = 10             # number of seconds between heartbeats

    def __init__(self, ip, port):
        self.logger = logging.getLogger(__name__)
        Thread.__init__(self)
        self.serverIP = ip
        self.port = port
        self.abort = False
        self.e = threading.Event()

        self.hbsocket = socket(AF_INET, SOCK_DGRAM)
        self.start()

    def __repr__(self):
        return "Heartbeat Client on port: %d\n" % self.port

    def run(self):
        if DEBUG_PIN != "":
            self.logger.info("PyHeartBeat client sending to IP %s , port %d" % (self.serverIP, self.port))
        while self.abort is False:
            self.hbsocket.sendto('Thump!'.encode(), (self.serverIP, self.port))
            self.e.wait(timeout=self.period)   # instead of time.sleep()

    def stop(self):
        """ Stop the Thread """
        self.abort = True
        # interrupt sleep
        self.e.set()


# hbc = HeartbeatClient('127.0.0.1', 43278)
