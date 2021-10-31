import atexit
import fcntl
import os
import sys
from pathlib import Path

from classes.psUtil import PsUtil
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall


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
        try:
            self.transport.write(b'HB!', (self.serverIP, self.port))
            print("HB")
        except Exception:
            # Network unreachable
            print("Network unreachable")


def cleanUp(file):
    """ at client shutdown, delete the lock File """
    if os.path.exists(file):
        os.remove(file)


def checkRunningPID():
    """ check id the PID from Lock File is still active, if not then delete LockFile """
    f = open(FILE_NAME, "r")
    pid = f.read()
    ps = PsUtil()
    if ps.isRunning(pid) is False:
        # old Process is dead
        cleanUp(FILE_NAME)
        print("Deleted Client Zombie Process Lock File ...")
        return False
    return True


def lockFile(lockfile):
    """ prevent to start client twice """
    fp = open(lockfile, 'w')  # create a new one
    try:
        fp.write("%s" % os.getpid())
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # the file has been locked
        success = True
    except IOError:
        success = False
    fp.close()
    return success


if __name__ == '__main__':
    rootDir = Path(__file__).parent
    FILE_NAME = rootDir.joinpath("hb_client.lock")
    # do not start twice

    if os.path.exists(FILE_NAME) is True:
        if checkRunningPID() is True:
            print("Client Process found, exiting now ...")
            sys.exit(0)
    else:
        print('Lock File created: Preventing starting twice ...')
        lockFile(FILE_NAME)

    atexit.register(cleanUp, FILE_NAME)

    try:
        # index 0 is the name of the script itself
        serverIP = sys.argv[1]
        port = int(sys.argv[2])
        interval = int(sys.argv[3])

        heartBeatClientObj = HeartbeatClient(serverIP, port, interval)

        reactor.listenMulticast(8005, heartBeatClientObj, listenMultiple=True)  # noqa
        reactor.run()  # noqa
    except Exception as ex:
        print("Usage: HeartbeatClient.py ServerIP Port Intervall")
        print(ex)
