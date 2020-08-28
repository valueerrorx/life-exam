#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann
from pathlib import Path
from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QGuiApplication
import os
import stat
import psutil
from PyQt5.QtWidgets import QMainWindow


class ConnectionStatus(QMainWindow):
    """ Display a Status Window for some reasons """
    def __init__(self, parent=None):
        super(ConnectionStatus, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.rootDir = Path(__file__).parent
        uifile = self.rootDir.joinpath('status.ui')
        self.ui = uic.loadUi(uifile)        # load UI
        # this will hide the app from task bar
        self.ui.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.ui.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.moveToDefaultPosition()
        
        # be sure that in Designe MouseTracking is enabled!
        self.ui.icon.mousePressEvent = lambda event: self._onClick(event)
                
        self.msgpattern = "%s\n%s"
        self.serverid = "None"
        self.workdir = "."
        # terminate existing ConnectionStatus
        self._checkPID()
        # create new PID File
        self._writePID()
        
    def _onClick(self, event):
        if event.buttons() == QtCore.Qt.NoButton:
            # print("Simple mouse motion")
            pass
        elif event.buttons() == QtCore.Qt.LeftButton:
            # maybe hide the Status Icon
            print("Left click drag")
        elif event.buttons() == QtCore.Qt.RightButton:
            # print("Right click drag")
            pass
   
    def show(self):
        """ show it """
        # self.ticker.start()
        self.ui.show()

    def hide(self):
        """ show it """
        self.ui.hide()

    def _onAbbrechen(self):
        """ click event, hide it"""
        self._delPID()
        self.close()
        
    def setType(self, typ):
        if typ==1:
            self.setIcon("connected.png")
            self._setMessage("connected")
        else:
            self.setIcon("disconnected.png")
            self._setMessage("disconnected")
    
    def setServerID(self, theid):
        """the identifier from the server"""
        self.serverid = theid

    def _setMessage(self, txt):
        """ set the Message of the notification """       
        self.ui.msg.setText(self.msgpattern % (self.serverid, txt))

    def setIcon(self, icon):
        iconfile = self.rootDir.joinpath("img/"+icon).as_posix()
        self.ui.icon.setPixmap(QPixmap(iconfile))
        
    def setWorkDirectory(self, path):
        """where is the PID File stored?"""
        self.workdir = path

    def moveToDefaultPosition(self):
        """ the default position right bottom of screen """
        self.ui.adjustSize()
        # get main screen
        screen = QGuiApplication.screens()[0]
        taskbar_height = screen.geometry().height() - screen.availableVirtualGeometry().height()
        self.ui.move(screen.geometry().width(), screen.geometry().height() - taskbar_height)
        x = screen.geometry().width() - self.ui.width()
        y = (screen.availableVirtualGeometry().height() - self.ui.height()) // 2
        self.ui.move(x, y)
        
    def _writePID(self):
        """write your PID on disk top path"""
        file = os.path.join(self.workdir, 'connection.pid')
        pid = str(os.getpid())
    
        f = open(file, 'w+')
        f.write(pid)
        f.close()
        self._changePermission(file, "777")
    
    def _changePermission(self, path, octal):
        st = os.stat(path)
        if octal == "777":
            mode = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO
        os.chmod(path, st.st_mode | mode)
        
    def _delPID(self):
        """ delete the PID File"""
        file = os.path.join(self.workdir, 'connection.pid')
        os.remove(file)
        
    def _checkPID(self):
        """
        check for a PID File
        :return: Pid Number if exists, or None
        """
        my_file = Path(self.workdir).joinpath('connection.pid')
        if my_file.is_file():
            # file exists
            file = open(my_file, "r")
            pid = file.read()
            self.closeDialog(pid) 
        else:
            return None
        
    def closeDialog(self, pid):
        """kill the old running Process"""
        PID = int(pid) 
        if psutil.pid_exists(PID):
            p = psutil.Process(PID)
            p.terminate()  #or p.kill()
