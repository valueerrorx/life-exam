import PyQt5.QtCore
from PyQt5.QtCore import pyqtSignal


class HeartbeatSignalEmitter(PyQt5.QtCore.QObject):
    """ just a wrapper for PyQT Signals, cause HeartBeatServer is not a PyQT Object """
    signal_1 = pyqtSignal(list)

    def emit(self, what):
        self.signal_1.emit(what)
