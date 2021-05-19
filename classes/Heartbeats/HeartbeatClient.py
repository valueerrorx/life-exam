from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
import sys


class HeartbeatClient(DatagramProtocol):
    """
    HeartbeatClient: sends an UDP packet to a given server every x seconds.
    """

    def __init__(self, ip, port, interval):
        self.loopObj = None
        self.serverIP = ip
        self.port = port
        self.interval = interval

    def __repr__(self):
        return "Heartbeat Client on port: %d\n" % self.port

    # Twisted Part ##################################################
    def startProtocol(self):
        print("HeartbeatClient client sending to IP %s, port %d" % (self.serverIP, self.port))
        # Called when transport is connected
        self.loopObj = LoopingCall(self.sendHeartBeat)
        self.loopObj.start(self.interval, now=True)

    def stopProtocol(self):
        "Called after all transport is teared down"
        print("HeartbeatClient stopped ...")

    def datagramReceived(self, data, addr):
        pass

    def sendHeartBeat(self):
        self.transport.write(b'HB!', (self.serverIP, self.port))


if __name__ == '__main__':
    # index 0 is the name of the script itself
    try:
        serverIP = sys.argv[1]
        port = int(sys.argv[2])
        interval = int(sys.argv[3])

        heartBeatClientObj = HeartbeatClient(serverIP, port, interval)

        reactor.listenMulticast(8005, heartBeatClientObj, listenMultiple=True)    #noqa
        reactor.run()  #noqa
    except Exception as ex:
        print("Usage: HeartbeatClient.py ServerIP Port Intervall")
        print(ex)
