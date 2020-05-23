#!/usr/bin/env python3
import sys
from pathlib import Path
import PyQt5
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from Qt.Notification.Notification import Notification_Core, Notification_Type,\
    Notification
from PyQt5.Qt import QThread
import threading


class MAIN_UI(PyQt5.QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MAIN_UI, self).__init__(parent)
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('main.ui')
        self.ui = uic.loadUi(uifile)        # load UI
        self.ui.btn1.clicked.connect(lambda: self.startNotificationTest())
        self.ui.show()

    def startNotificationTest(self):
        texte = ["Vor langer langer Zeit lebte ein Tux in Österreich und hatte keine Windows daheim",
                 "Quod erat demonsdrandum",
                 "Einer der nichts weiß und nicht weiß das er nichts weiß, weiß weniger als einer der weiß dass er nichts weiß"]
        """ start showing Notification within a Thread for non blocking """
        
        """
        t = QThread()
        notification.moveToThread(t)
        t.started.connect(worker.run)
        t.start()
        """
        
        n = Notification_Core()
        n.setMessage(texte[0])
        n.setType(Notification_Type.Information)
        notification = Notification(n)
        #notification.run()
        
        t = threading.Thread(target=notification)
        t.daemon = True
        t.start()
        
                
        
        
"""
        n = Notification_Core()
        n.setMessage(texte[1])
        n.setType(Notification_Type.Error)
        notification = Notification(n)
        notification.start()

        n = Notification_Core()
        n.setMessage(texte[2])
        n.setType(Notification_Type.Success)
        notification = Notification(n)
        notification.start()

        n = Notification_Core()
        n.setMessage(texte[3])
        n.setType(Notification_Type.Warning)
        notification = Notification(n)
        notification.start()
"""

def main():
    app = QApplication(sys.argv)

    # show main Window
    mainUI = MAIN_UI()  #noqa
    app.exec_()


if __name__ == '__main__':
    main()
