#! /usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import  uic, QtWidgets
from PyQt5.QtGui import QIcon, QColor
import sys
import os
from common import checkIP
from config import *

class MeinDialog(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.ui = uic.loadUi("student.ui")        # load UI
        self.ui.setWindowIcon(QIcon("pixmaps/security.png"))
        self.ui.exit.clicked.connect(self._onAbbrechen)        # setup Slots
        self.ui.start.clicked.connect(self._onStartExamClient)
       
        clientkillscript = os.path.join(SCRIPTS_DIRECTORY, "terminate-exam-process.sh")
        os.system("sudo %s %s" %(clientkillscript, 'client') )  #make sure only one client instance is running per client

    def _onAbbrechen(self):    # Exit button
        self.ui.close()

    def _onStartExamClient(self):
        SERVER_IP=self.ui.serverip.text()
        ID=self.ui.studentid.text()
        if checkIP(SERVER_IP):
            palettedefault = self.ui.serverip.palette()
            palettedefault.setColor(self.ui.serverip.backgroundRole(), QColor(255, 255, 255))
            self.ui.serverip.setPalette(palettedefault)
            if ID != "":
                self.ui.close()
                #command = "kdesudo python client.py %s %s &" %(SERVER_IP, ID)
                #command = "kdesudo 'twistd -l client.log --pidfile client.pid -y client.tac %s %s' &" %(SERVER_IP, ID)
                
                command = "kdesudo 'twistd -l %s/client.log --pidfile %s/client.pid examclient -p %s -h %s -i %s' &" %(WORK_DIRECTORY, WORK_DIRECTORY, SERVER_PORT, SERVER_IP, ID)
                
                
                os.system(command)
            palettewarn = self.ui.studentid.palette()
            palettewarn.setColor(self.ui.studentid.backgroundRole(), QColor(200, 80, 80))
            self.ui.studentid.setPalette(palettewarn)
        else:
            palettewarn = self.ui.serverip.palette()
            palettewarn.setColor(self.ui.serverip.backgroundRole(), QColor(200, 80, 80))
            self.ui.serverip.setPalette(palettewarn)
    
           
        
        

app = QtWidgets.QApplication(sys.argv)
dialog = MeinDialog()
dialog.ui.show()
sys.exit(app.exec_())
