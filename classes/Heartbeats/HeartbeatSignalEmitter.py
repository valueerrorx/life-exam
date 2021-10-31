import PyQt5.QtCore
from PyQt5.QtCore import pyqtSignal


class HeartbeatSignalEmitter(PyQt5.QtCore.QObject):
    """ just a wrapper for PyQT Signals, cause HeartBeatServer is not a PyQT Object """
    signal_1 = pyqtSignal(list)
    signal_2 = pyqtSignal(list)

    def __init__(self, main_ui):
        super(HeartbeatSignalEmitter, self).__init__()
        self.main_ui = main_ui

        self.signal_1.connect(self.main_ui.silentClientsUpdate)
        self.signal_2.connect(self.main_ui.checkOnlineClients)

    def emitSilentClients(self, what):
        """ fire Signal which Clients are silent """
        self.signal_1.emit(what)

    def emitcheckOnlineClients(self, what):
        """ fire Signal: check which clients must marked as online """
        self.signal_2.emit(what)
