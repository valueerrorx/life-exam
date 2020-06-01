import sys
from pathlib import Path
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication

sys.path.insert(0, Path(__file__).parent.parent.as_posix())
print(Path(__file__).parent.parent.as_posix())

from Thread_Jobs import Thread_Jobs


class MAIN_UI(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('main.ui')
        uic.loadUi(uifile, self)        # load UI inside QMainWindow

        self.btn.clicked.connect(lambda: self.stopIt()())

        self.jobs = Thread_Jobs()  # no parent!
        self.jobs.jobs_done.connect(self.allJobsDone)
        self.jobs.start()

    def allJobsDone(self):
        print("All Jobs done ....")
        QApplication.quit

    def stopIt(self):
        self.jobs.stop()
        QApplication.quit

    def closeEvent(self, event):
        ''' window tries to close '''
        self.stopIt()
        event.ignore()


def main():
    app = QApplication(sys.argv)

    # show main Window
    gui = MAIN_UI()  #noqa
    gui.show()
    app.exec_()


if __name__ == '__main__':
    main()
