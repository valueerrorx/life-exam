from PyQt5.QtCore import QThread, QObject, QCoreApplication

class Worker(QObject):
    def run(self):
        print('Worker called from: %#x' % int(QThread.currentThreadId()))
        QThread.sleep(2)
        print('Finished')
        QCoreApplication.quit()

if __name__ == '__main__':

    import sys
    app = QCoreApplication(sys.argv)
    print('From main thread: %#x' % int(QThread.currentThreadId()))
    t = QThread()
    worker = Worker()
    worker.moveToThread(t)
    t.started.connect(worker.run)
    t.start()
    app.exec_()