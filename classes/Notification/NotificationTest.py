#!/usr/bin/env python3
import sys
from pathlib import Path
import PyQt5
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from Notification import Notification_Core, Notification


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
        # creates the Notification Dialog
        n = Notification_Core()
        notification = Notification(n)
        notification.setDemo()
        notification.showInformation(texte[0])

        n = Notification_Core()
        notification = Notification(n)
        notification.setDemo()
        notification.showError(texte[1])

        n = Notification_Core()
        notification = Notification(n)
        notification.setDemo()
        notification.showWarning(texte[2])

        n = Notification_Core()
        notification = Notification(n)
        notification.setDemo()
        notification.showSuccess(texte[0])


def main():
    app = QApplication(sys.argv)

    # show main Window
    MAIN_UI()  #noqa
    app.exec_()


if __name__ == '__main__':
    main()
