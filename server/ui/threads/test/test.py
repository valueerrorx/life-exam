import sys
from pathlib import Path
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.Qt import QGuiApplication
from server.ui.threads.Thread_Jobs import Thread_Jobs

sys.path.insert(0, Path(__file__).parent.parent.as_posix())
print(Path(__file__).parent.parent.as_posix())


class MAIN_UI(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.parent = parent
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('main.ui')
        uic.loadUi(uifile, self)        # load UI inside QMainWindow

        self.btn.clicked.connect(lambda: self.stopIt())

        self.jobs = Thread_Jobs()  # no parent!
        self.jobs.jobs_done.connect(self.allJobsDone)
        self.jobs.start()

    def allJobsDone(self):
        print("All Jobs done ....")
        QApplication.quit()

    def stopIt(self):
        self.jobs.stop()
        QApplication.quit()

    def closeEvent(self, event):
        ''' window tries to close '''
        self.stopIt()
        event.ignore()


def testScreens():
    # first approach
    screen = QApplication.primaryScreen()
    screenGeometry = screen.geometry()
    print("Screen %s x %s" % (screenGeometry.height(), screenGeometry.width()))

    # second
    qgui = QGuiApplication
    print("Number of screens: %s" % len(qgui.screens()))
    print("Primary screen: %s" % qgui.primaryScreen().name())

    for screen in qgui.screens():
        print("Information for screen: %s" % screen.name())
        print("  Available geometry: %s %s, %s x %s" % (screen.availableGeometry().x(), screen.availableGeometry().y(), screen.availableGeometry().width(), screen.availableGeometry().height()))
        print("  Available size: %s x %s" % (screen.availableSize().width(), screen.availableSize().height()))
        print("  Available virtual geometry: %s %s, %s x %s" % (screen.availableVirtualGeometry().x(), screen.availableVirtualGeometry().y(), screen.availableVirtualGeometry().width(), screen.availableVirtualGeometry().height()))
        print("  Available virtual size: %s x %s" % (screen.availableVirtualSize().width(), screen.availableVirtualSize().height()))
        print("  Depth: %s bits" % screen.depth())
        print("  Geometry: %s %s, %s x %s" % (screen.geometry().x(), screen.geometry().y(), screen.geometry().width(), screen.geometry().height()))
        print("  Logical DPI: %s" % screen.logicalDotsPerInch())
        print("  Logical DPI X: %s" % screen.logicalDotsPerInchX())
        print("  Logical DPI Y: %s" % screen.logicalDotsPerInchY())
        print("  Physical DPI: %s" % screen.physicalDotsPerInch())
        print("  Physical DPI X: %s" % screen.physicalDotsPerInchX())
        print("  Physical DPI Y: %s" % screen.physicalDotsPerInchY())
        print("  Physical size: %s x %s mm" % (screen.physicalSize().width(), screen.physicalSize().height()))
        print("  Refresh rate: %s Hz" % screen.refreshRate())
        print("  Size: %s x %s" % (screen.size().width(), screen.size().height()))
        print("  Virtual geometry: %s %s, %s x %s" % (screen.virtualGeometry().x(), screen.virtualGeometry().y(), screen.virtualGeometry().width(), screen.virtualGeometry().height()))
        print("  Virtual size: %s x %s" % (screen.virtualSize().width(), screen.virtualSize().height()))


def main():
    app = QApplication(sys.argv)

    # show main Window
    gui = MAIN_UI()  #noqa
    gui.show()
    testScreens()
    app.exec_()


if __name__ == '__main__':
    main()
