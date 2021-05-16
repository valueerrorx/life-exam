import logging
from config.config import DEBUG_PIN, HEARTBEAT_PORT
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall


class HeartbeatClient(DatagramProtocol):
    """
    HeartbeatClient: sends an UDP packet to a given server every x seconds.
    """

    period = 10             # number of seconds between heartbeats

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.loopObj = None
        self.serverIP = None
        self.port = HEARTBEAT_PORT

    def __repr__(self):
        return "Heartbeat Client on port: %d\n" % self.port

    def setServerIP(self, ip):
        """ which Server to conntact """
        self.serverIP = ip

    def start(self):
        """ Startup Looping Call Heartbeats """
        if self.serverIP is None:
            self.logger.error("HeartbeatClient: NO ServerIP is set!")
            return
        # I am ready to send heart beats
        self.loopObj = LoopingCall(self.sendHeartBeat)
        self.loopObj.start(self.period, now=False)
        if DEBUG_PIN != "":
            self.logger.info("HeartbeatClient client sending to IP %s , port %d" % (self.serverIP, self.port))

    # Twisted Part ##################################################

    def startProtocol(self):
        # Called when transport is connected
        pass

    def stopProtocol(self):
        "Called after all transport is teared down"
        pass

    def datagramReceived(self, data, addr):
        if DEBUG_PIN != "":
            self.logger.info("Received packet from %s > %s" % (addr[0], data.decode()))

    def sendHeartBeat(self):
        self.transport.write('HB!', (self.serverIP, self.port))

# hbc = HeartbeatClient('127.0.0.1', 43278)
