#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import time

from client.resources.Observers import Observers
from config.config import APP_DIRECTORY, EXAMCONFIG_DIRECTORY, SCRIPTS_DIRECTORY,\
    WORK_DIRECTORY, SERVER_PORT, DEBUG_PIN, DEBUG_ID
from classes.mutual_functions import checkIP, prepareDirectories

from PyQt5.QtCore import QRegExp, Qt
from PyQt5 import QtWidgets, uic

from PyQt5.QtGui import QIcon, QRegExpValidator, QPixmap, QColor


class ClientDialog(QtWidgets.QDialog, Observers):
    
    def __init__(self):
        QtWidgets.QDialog.__init__(self)

        self.logger = logging.getLogger(__name__)
        uic.uiparser.logger.setLevel(logging.INFO)
        uic.properties.logger.setLevel(logging.INFO)
        
        self.examserver = dict()
        self.disconnected_clients = dict()
        self.completer = QtWidgets.QCompleter()
        self.completerlist = []
        self._initUi()
        prepareDirectories()

    def _initUi(self):
        #Register self to Global Observer List Object 
        Observers.__init__(self)
        #Register event
        self.observe('updateGUI',  self.updateGUI)
        
        self.scriptdir=os.path.dirname(os.path.abspath(__file__))
        uifile=os.path.join(APP_DIRECTORY,'client/client.ui')
        self.ui = uic.loadUi(uifile) 
        winicon=os.path.join(APP_DIRECTORY,'pixmaps/windowicon.png')
        self.ui.setWindowIcon(QIcon(winicon))
        self.ui.exit.clicked.connect(self._onAbbrechen)  # setup Slots
        self.ui.start.clicked.connect(self._onStartExamClient)
        self.ui.offlineexam.clicked.connect(self._on_offline_exam)
        self.ui.offlineexamexit.clicked.connect(self._on_offline_exam_exit)
        self.ui.serverdropdown.currentIndexChanged.connect(self._updateIP)
        self.ui.serverdropdown.activated.connect(self._updateIP)
        self.ui.studentid.textChanged.connect(lambda: self._changePalette(self.ui.studentid, 'ok'))
        self.ui.studentid.setFocus()
        #self.ui.serverip.textChanged.connect(lambda: self._changePalette(self.ui.serverip,'ok'))
        self.ui.pincode.textChanged.connect(lambda: self._changePalette(self.ui.pincode,'ok'))
        self.ui.serverip.hide()
        self.ui.keyPressEvent = self.newOnkeyPressEvent

        char_regex=QRegExp("[a-z-A-Z\-_]+")   # only allow specif characters in textfields
        char_validator = QRegExpValidator(char_regex)
        self.ui.studentid.setValidator(char_validator)

        num_regex=QRegExp("[0-9_]+")
        num_validator = QRegExpValidator(num_regex)
        self.ui.pincode.setValidator(num_validator)

        ip_regex=QRegExp("[0-9\._]+")
        ip_validator = QRegExpValidator(ip_regex)
        #self.ui.serverip.setValidator(ip_validator)

    def newOnkeyPressEvent(self,e):
        if e.key() == Qt.Key_Escape:
            self.logger.info("Close-Event triggered")


    def _onAbbrechen(self):  # Exit button
        self.ui.close()
            
    def updateGUI(self, data, server_ip):
        """
        Event Update from Observeable MultiCastClient
        """
        # { servername : ['clientname1','clientname2'] }
        self.disconnected_clients.update({ data[1] : data[2:] })
        #if this is a new server name 
        if data[1] not in self.examserver:   
            for key in self.examserver:
                ip = self.examserver.get(key)
                if ip == self.server_ip:          #check if the same ip is already there (server just got renamed)
                    self.examserver.pop(key)      #remove old entry
                    break

            self.examserver.update({ data[1] : str(server_ip) })    #add new entry
            self._updateServerlist()                                #update gui

        self.ui.serversearch.setText("Server Found!")
        checkimage=os.path.join(APP_DIRECTORY,'pixmaps/checked.png')
        self.ui.servercheck.setPixmap(QPixmap(checkimage))
        
        #only debug if DEBUG_PIN is not ""
        if DEBUG_PIN !="":
            ID = DEBUG_ID
            PIN = DEBUG_PIN
            self.ui.studentid.setText(ID)
            self.ui.pincode.setText(PIN)
            self.logger.info("DEBUGGING Mode")


    def _on_offline_exam(self):     
        self.msg = QtWidgets.QMessageBox()
        self.msg.setIcon(QtWidgets.QMessageBox.Information)
        self.msg.setText("Wollen sie in den abgesicherten Exam Modus wechseln?")
        self.msg.setDetailedText("Die automatische Abgabe,\nScreenlock, senden und empfangen von Dateien\nund andere Funktionen sind in diesem Modus nicht verfügbar.")
        self.msg.setWindowTitle("LiFE Exam")
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        retval = self.msg.exec_()   # 16384 = yes, 65536 = no
       
        if str(retval) == "16384":
            command = "chmod +x %s/startexam.sh &" % EXAMCONFIG_DIRECTORY  # make exam script executable
            os.system(command)
            time.sleep(2)
            startcommand = "%s/startexam.sh &" %(EXAMCONFIG_DIRECTORY) # start as user even if the twistd daemon is run by root
            os.system(startcommand)  # start script
        else:
            self.msg = False
        
        
    def _on_offline_exam_exit(self):  
        startcommand = "%s/stopexam.sh &" %(SCRIPTS_DIRECTORY) 
        os.system(startcommand)  # start script


    def _onStartExamClient(self):
        SERVER_IP = self.ui.serverip.text()
        ID = self.ui.studentid.text()
        PIN = self.ui.pincode.text()
        
        if checkIP(SERVER_IP):
            if ID == "":
                self._changePalette(self.ui.studentid, "warn")
            elif PIN == "":
                self._changePalette(self.ui.pincode, "warn")
            else:
                self.ui.close()
                clientkillscript = os.path.join(SCRIPTS_DIRECTORY, "terminate-exam-process.sh")
                # make sure only one client instance is running per client
                os.system("bash %s %s" % (clientkillscript, 'client'))
                self.logger.info("Terminated old running twisted Client")  
                
                namefile = os.path.join(WORK_DIRECTORY, "myname.txt")  # moved this to workdirectory because configdirectory is overwritten on exam start
                openednamefile = open(namefile, 'w+')  # erstelle die datei neu
                openednamefile.write("%s" %(ID) )
                
                
                from twisted.plugin import IPlugin, getPlugins
                #plgs = 
                list(getPlugins(IPlugin))
                
                #for item in plgs:
                #    print(item)    
                #print(sys.path)           

                command = "twistd -l %s/client.log --pidfile %s/client.pid examclient -p %s -h %s -i %s -c %s &" % (
                    WORK_DIRECTORY, WORK_DIRECTORY, SERVER_PORT, SERVER_IP, ID, PIN)
                self.logger.info(command)
                os.system(command)
                
                #subprocess.call(command, shell=True,env=dict(os.environ ))
                # for non daemon mode manual to track bugs
                #sudo twistd -n --pidfile /home/student/.life/EXAM/client.pid examclient -p 11411 -h 10.0.0.110 -i ich -c 2604
            
        else:
            self._changePalette(self.ui.serverip, "warn")


    def _changePalette(self, item, reason):
        if reason == 'warn':
            palettewarn = item.palette()
            palettewarn.setColor(item.backgroundRole(), QColor(160, 80, 80))
            item.setPalette(palettewarn)
        else:
            palettedefault = item.palette()
            palettedefault.setColor(item.backgroundRole(), QColor(255, 255, 255))
            item.setPalette(palettedefault)

    def _updateServerlist(self):
        """updates the dropdownmenu if new servers are found"""
        self.ui.serverdropdown.clear()
        for server in self.examserver:
            self.ui.serverdropdown.addItem(server)

    def _updateIP(self):
        """updates the ip address fiel according to the selection in the dropdownmenu """
        current = self.ui.serverdropdown.currentText()
        self.ui.serverip.setText(self.examserver.get(current) )
        
        self.completerlist = self.disconnected_clients.get(current)  # gets a list from the dict
        self.completer = QtWidgets.QCompleter(self.completerlist)
        self.ui.studentid.setCompleter(self.completer)