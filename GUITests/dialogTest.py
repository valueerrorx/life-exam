#!/usr/bin/env python3
import sys
import multiprocessing
import threading
import time
from pathlib import Path
import PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap, QImage, QBrush, QCursor
from PyQt5.QtCore import pyqtSignal
import multitasking


class Notification(QtWidgets.QDialog):
    """ Display a Notififation for some reasons """
    def __init__(self, parent=None):
        super(Notification, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('Notification.ui')
        self.ui = uic.loadUi(uifile)        # load UI
        self.ui.setWindowFlags(Qt.FramelessWindowHint)

        # center widget on the screen
        self.ui.adjustSize()  # update self.rect() now
        # position right middle of screen
        screen = QApplication.instance().desktop().screen().rect()
        self.ui.move(screen.width() - self.ui.width(), (screen.height() - self.ui.height()) // 2)
        iconfile = self.rootDir.joinpath('pixmaps/success.png').as_posix()
        self.ui.icon.setPixmap(QPixmap(iconfile))

        self.ui.exit.clicked.connect(self._onAbbrechen)

        # Waiting Thread
        self.ticker = Notification_Ticker(self)
        # connect Events
        self.ticker.timeout_event.connect(self.timer_done)

    def moveTo(self, x, y):
        """ move the dialog on the screen """
        self.ui.move(x, y)

    def show(self):
        """ show it """
        # self.ticker.start()
        self.ui.show()

    def hide(self):
        """ show it """
        self.ui.hide()

    def _onAbbrechen(self):
        """ hide it"""
        self.hide()

    def timer_done(self):
        self.hide()

    def showInformation(self, titel, text):
        """Information with a success Icon"""
        self.ui.header.setText(titel)
        self.ui.text.setText(text)
        self.show()

    def showWarning(self, titel, text):
        """Information with a warning Icon"""
        self.ui.header.setText(titel)
        self.ui.text.setText(text)
        self.show()


class Notification_Ticker(QtCore.QThread):
    """ just a ticker to close the dialog"""

    # event
    timeout_event = pyqtSignal()

    def __init__(self, parent, timeout=3):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.parent = parent
        self.timeout = timeout
        self.overall_time = 0

    def __del__(self):
        self.wait()

    def stop(self):
        self.running = False
        self.quit()

    def isAlive(self):
        if self.running:
            return True
        else:
            return False

    def run(self):
        self.running = True
        self.overall_time = 0
        while(True):
            time.sleep(1)
            self.overall_time += 1
            if self.running==False:
                break
            elif self.overall_time >= self.timeout:
                break
        return 0

    def fireTimeout(self):
        """ Thread has finished """
        if len(self.clients) > 0:
            self.timeout_event.emit(self.parent)


# ------------------------------------------------------------------------------
# only for testing
class MAIN_UI(PyQt5.QtWidgets.QMainWindow):
    startNotification = pyqtSignal()
    endNotification = pyqtSignal()

    def __init__(self,parent=None):
        super(MAIN_UI, self).__init__(parent)
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('main.ui')
        self.ui = uic.loadUi(uifile)        # load UI

        self.startNotification.connect(Notification().show)
        self.endNotification.connect(Notification().hide)

        self.ui.btn1.clicked.connect(lambda: self.startTest())
        self.ui.btn1.clicked.connect(lambda: self.stopTest())

        self.ui.show()

    def startThread(self,functionName):
        t = threading.Thread(target=functionName)
        t.daemon = True
        t.start()

    def exampleMethod1(self):
        #This function will show the dialog box at the beginning of the process
        # and will update the text and button once the process is complete
        mainUI.startSignal.emit()
        #Do lots of things here that take a long time
        mainUI.endSignal.emit()

    def startTest(self):
        self.startThread(self.exampleMethod1)

    def stopTest(self):
        pass



def main():
    app = QApplication(sys.argv)
    #notification = Notification()
    #notification.showInformation("Information", "Vor langer langer Zeit lebte ein Tux in Österreich und hatte keine Windows daheim")

    #notification.moveTo(100, 100)
    #notification.showWarning("Warnung", "Vor langer langer Zeit lebte ein Tux in Österreich und hatte keine Windows daheim")

    # show main Window
    mainUI = MAIN_UI()


    app.exec_()


if __name__ == '__main__':
    main()
