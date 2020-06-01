import sys
from pathlib import Path
import PyQt5
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from Thread_Jobs import Thread_Jobs


class MAIN_UI(PyQt5.QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MAIN_UI, self).__init__(parent)
        self.parent = parent
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('main.ui')
        self.ui = uic.loadUi(uifile)        # load UI
        self.ui.show()

        self.ui.btn.clicked.connect(lambda: self.stopIt()())

        self.jobs = Thread_Jobs()  # no parent!
        self.jobs.jobs_done.connect(self.allJobsDone)
        self.jobs.start()

    def allJobsDone(self):
        print("All Jobs done ....")
        QApplication.quit

    def stopIt(self):
        self.jobs.stop()


def main():
    app = QApplication(sys.argv)

    # show main Window
    gui = MAIN_UI()  #noqa
    app.exec_()


if __name__ == '__main__':
    main()
