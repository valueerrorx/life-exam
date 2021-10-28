import PyQt5.QtCore
from PyQt5.QtCore import pyqtSignal


class HeartbeatSignalEmitter(PyQt5.QtCore.QObject):
    """ just a wrapper for PyQT Signals, cause HeartBeatServer is not a PyQT Object """
    signal_1 = pyqtSignal(list)

    def __init__(self, main_ui):
        super(HeartbeatSignalEmitter, self).__init__()
        self.main_ui = main_ui
        self.connectSilentClientsSignal()

    def connectSilentClientsSignal(self):
        self.signal_1.connect(self.main_ui.silentClientsUpdate)

    def emitSilentClients(self, what):
        """ fire Signal which Clients are silent """
        self.signal_1.emit(what)
