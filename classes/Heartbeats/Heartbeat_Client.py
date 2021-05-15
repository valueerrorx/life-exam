from socket import socket, AF_INET, SOCK_DGRAM
from time import sleep
from threading import Thread


class HeartbeatClient(Thread):
    """
    PyHeartBeat client: sends an UDP packet to a given server every x seconds.
    PyHBClient.py serverip [udpport]
    """

    BEATWAIT = 10             # number of seconds between heartbeats

    def __init__(self, ip, port):
        Thread.__init__(self)
        self.serverIP = ip
        self.port = port
        self.abort = False

        self.hbsocket = socket(AF_INET, SOCK_DGRAM)

    def __repr__(self):
        return "Heartbeat Client on port: %d\n" % self.port

    def run(self):
        print("PyHeartBeat client sending to IP %s , port %d" % (self.serverIP, self.port))
        while self.abort is False:
            self.hbsocket.sendto('Thump!'.encode(), (self.serverIP, self.port))
            sleep(self.BEATWAIT)

    def stop(self):
        """ Stop the Thread """
        self.abort = True
