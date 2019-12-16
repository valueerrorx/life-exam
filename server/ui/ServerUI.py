#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import os
import shutil
import sip
from pathlib import Path

from config.config import VERSION, PRINTERCONFIG_DIRECTORY,\
    SERVERZIP_DIRECTORY, SHARE_DIRECTORY, USER, EXAMCONFIG_DIRECTORY,\
    SCRIPTS_DIRECTORY
from config.enums import DataType
from server.resources.Applist import findApps
from classes.system_commander import dialog_popup, show_ip, start_hotspot

from classes.mutual_functions import get_file_list, checkIP

from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QRegExp
from PyQt5.Qt import QRegExpValidator
from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap, QImage, QBrush, QCursor
from server.resources import ScreenshotWindow
from classes.HTMLTextExtractor import html_to_text

from classes import mutual_functions
from server.ui.Thread_Wait import Thread_Wait
from server.ui.Thread_Wait_Events import client_abgabe_done_exit_exam, client_recieved_file_done

class ServerUI(QtWidgets.QDialog):
    def __init__(self, factory):
        QtWidgets.QDialog.__init__(self)
        self.logger = logging.getLogger(__name__)
        uic.uiparser.logger.setLevel(logging.INFO)
        uic.properties.logger.setLevel(logging.INFO)
        
        self.factory = factory     # type: MyServerFactory
        #rootDir of Application
        self.rootDir = Path(__file__).parent.parent.parent
        
        uifile=self.rootDir.joinpath('server/server.ui')
        self.ui = uic.loadUi(uifile)        # load UI
        
        iconfile=self.rootDir.joinpath('pixmaps/windowicon.png').as_posix()
        self.ui.setWindowIcon(QIcon(iconfile))  # definiere icon für taskleiste
                
        self.ui.exit.clicked.connect(self._onAbbrechen)  # setup Slots
        self.ui.sendfile.clicked.connect(lambda: self._onSendFile("all"))  # button x   (lambda is not needed - only if you wanna pass a variable to the function)
        self.ui.showip.clicked.connect(self._onShowIP)  # button y
        self.ui.abgabe.clicked.connect(lambda: self._onAbgabe("all"))
        self.ui.screenshots.clicked.connect(lambda: self._onScreenshots("all"))
        self.ui.startexam.clicked.connect(lambda: self._on_start_exam("all"))
        self.ui.openshare.clicked.connect(self._onOpenshare)
        self.ui.starthotspot.clicked.connect(self._onStartHotspot)
        self.ui.testfirewall.clicked.connect(self._onTestFirewall)
        
        self.ui.autoabgabe.clicked.connect(self._onAutoabgabe)
        self.ui.screenlock.clicked.connect(lambda: self._onScreenlock("all"))
        self.ui.exitexam.clicked.connect(lambda: self._on_exit_exam("all"))
        self.ui.closeEvent = self.closeEvent  # links the window close event to our custom ui
        self.ui.printconf.clicked.connect(self._onPrintconf)
        self.ui.printer.clicked.connect(lambda: self._onSendPrintconf("all"))
        
        loading_gif = self.rootDir.joinpath("pixmaps/working.gif").as_posix()
        self.workinganimation = QtGui.QMovie(loading_gif, QtCore.QByteArray(), self) 
        self.workinganimation.setCacheMode(QtGui.QMovie.CacheAll)
        self.workinganimation.setSpeed(100)
        self.ui.working.setMovie(self.workinganimation)
        
        self.timer = False
        self.msg = False
        self.ui.version.setText("<b>Version</b> %s" % VERSION )
        self.ui.currentpin.setText("<b>%s</b>" % self.factory.pincode  )
        self.ui.examlabeledit1.setText(self.factory.examid  )
        self.ui.currentlabel.setText("<b>%s</b>" % self.factory.examid  )
        self.ui.examlabeledit1.textChanged.connect(self._updateExamName)
        self.ui.ssintervall.valueChanged.connect(self._changeAutoscreenshot)
        self.ui.label_clients.setText(self.createClientsLabel())
        
        num_regex=QRegExp("[0-9_]+")
        num_validator = QRegExpValidator(num_regex)
        ip_regex=QRegExp("[0-9\._]+")
        ip_validator = QRegExpValidator(ip_regex)

        self.ui.firewall1.setValidator(ip_validator)
        self.ui.firewall2.setValidator(ip_validator)
        self.ui.firewall3.setValidator(ip_validator)
        self.ui.firewall4.setValidator(ip_validator)

        self.ui.port1.setValidator(num_validator)
        self.ui.port2.setValidator(num_validator)
        self.ui.port3.setValidator(num_validator)
        self.ui.port4.setValidator(num_validator)

        findApps(self.ui.applist, self.ui.appview)
        
        # Stylesheet Rahmen für Client Items
        self.ui.listWidget.setStyleSheet("QListWidget::item{ border-width: 1px; border-style: solid; border-color: #AAA;}")
        
        #Waiting Thread
        self.waiting_thread = Thread_Wait()
        #connect Events        
        self.waiting_thread.client_finished.connect(client_abgabe_done_exit_exam)
        self.waiting_thread.client_recieved_file.connect(client_recieved_file_done)
                
        self.ui.keyPressEvent = self.newOnkeyPressEvent
        self.ui.show()
        
            
    def testImage(self, filename):
        """ test if image is valid """
        pixmap = QtGui.QPixmap(filename)
        if pixmap.isNull():
            self.logger.error('No icon with filename %s found' % filename)
            return False
        else:
            return True

        
    def createClientsLabel(self):
        """ Erzeugt den Text für Clients: <Anzahl> """
        return ("Clients: <b>%s</b>" % self.ui.listWidget.count()) 


    def _changeAutoscreenshot(self):
        self._workingIndicator(True, 200)
        intervall = self.ui.ssintervall.value()
      
        if self.factory.lcs.running:
            self.factory.lcs.stop()
        if intervall is not 0:
            self.log("<b>Changed Screenshot Intervall to %s seconds </b>" % (str(intervall)))
            self.factory.lcs.start(intervall)
        else:
            self.log("<b>Screenshot Intervall is set to 0 - Screenshotupdate deactivated</b>")


    def _onSendPrintconf(self,who):
        """send the printer configuration to all clients"""
        self._workingIndicator(True, 500)
        server_to_client = self.factory.server_to_client

        if self.factory.rawmode == True:   #check if server is already in rawmode (ongoing filetransfer)
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            if not server_to_client.clients:        #check if there are clients connected
                self.log("No clients connected")
                return
            self.factory.rawmode = True;   #ready for filetransfer - LOCK all other fileoperations 


 

        self._workingIndicator(True, 4000)
        self.log('<b>Sending Printer Configuration to All Clients </b>')
        dialog_popup('Sending Printer Configuration to All Clients')

        # create zip file of /etc/cups
        target_folder = PRINTERCONFIG_DIRECTORY
        filename = "PRINTERCONFIG"
        output_filename = os.path.join(SERVERZIP_DIRECTORY, filename)
        shutil.make_archive(output_filename, 'zip', target_folder)
        filename = "%s.zip" % (filename)
        file_path = os.path.join(SERVERZIP_DIRECTORY, filename)  # now with .zip extension

        # regenerate filelist and check for zip file
        self.factory.files = get_file_list(self.factory.files_path)
        if filename not in self.factory.files:
            self.logger.error('filename not found in directory')
            return

        self.log('Sending Configuration: %s (%d KB)' % (filename, self.factory.files[filename][1] / 1024))

        # send line and file to all clients
        server_to_client.send_file(file_path, who, DataType.PRINTER.value)


    def _onPrintconf(self):
        command = "kcmshell5 kcm_printer_manager &"
        os.system(command)

    def _onScreenlock(self,who):
        """locks the client screens"""
        self._workingIndicator(True, 1000)
        
        if self.factory.clientslocked:
            self.log("<b>UnLocking Client Screens </b>")
            icon = self.rootDir.joinpath("pixmaps/network-wired-symbolic.png").as_posix()
            self.ui.screenlock.setIcon(QIcon(icon))
            self.factory.clientslocked = False
            
            if self.factory.rawmode == True:    #dirty hack - thx to nora - gives us at least one option to open filetransfers again if something wicked happens
                self.factory.rawmode = False;
            
            if not self.factory.server_to_client.unlock_screens(who):
                self.log("No clients connected")
        else:
            self.log("<b>Locking Client Screens </b>")
            icon = self.rootDir.joinpath("pixmaps/unlock.png").as_posix()
            self.ui.screenlock.setIcon(QIcon(icon))
            self.factory.clientslocked = True
            if not self.factory.server_to_client.lock_screens(who):
                self.log("No clients connected")
                self.factory.clientslocked = False
                icon = self.rootDir.joinpath("pixmaps/network-wired-symbolic.png.png").as_posix()
                self.ui.screenlock.setIcon(QIcon(icon))
        self._onScreenshots("all")   #update screenshots right after un/lock


    def _onOpenshare(self):
        startcommand = "runuser -u %s /usr/bin/dolphin %s &" %(USER ,SHARE_DIRECTORY)
        os.system(startcommand)

    def _updateExamName(self):
        self.factory.examid = self.ui.examlabeledit1.text()
        self.ui.currentlabel.setText("<b>%s</b>" % self.factory.examid  )


    def _workingIndicator(self, action, duration):
        if self.timer and self.timer.isActive:  # indicator is shown a second time - stop old kill-timer
            self.timer.stop()
        if action is True:  # show working animation and start killtimer
            self.workinganimation.start()
            self.ui.working.show()
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(lambda: self._workingIndicator(False, 0))
            self.timer.start(duration)
        else:
            self.workinganimation.stop()
            self.ui.working.hide()


    def _onSendFile(self, who):
        """
        send a file to single or all clients
        who = connection ID or 'all'
        """
        self._workingIndicator(True, 500)
        server_to_client = self.factory.server_to_client
        
        #check if server is already in rawmode (ongoing filetransfer)
        if self.factory.rawmode == True:   
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            #check if there are clients connected
            if not server_to_client.clients:        
                self.log("No clients connected")
                return
            #ready for filetransfer - LOCK all other fileoperations
            self.factory.rawmode = True;    

        file_path = self._showFilePicker(SHARE_DIRECTORY)

        if file_path:
            # TODO: change working indicator to choose its own time depending on actions 
            # requiring all clients or only one client
            self._workingIndicator(True, 2000)
            
            #start Thread 
            self.log("Waiting for Client to send his Abgabe-Files")
            #on Event call        
            
            
            #läuft der Thread ist er beendet?
            if self.waiting_thread.isRunning():
                self.waiting_thread.start()
            
             
            success, filename, file_size, who = server_to_client.send_file(file_path, who, DataType.FILE.value)

            if success:
                self.log('<b>Sending file:</b> %s (%d Byte) to <b> %s </b>' % (filename, file_size, who))
            else:
                self.log('<b>Sending file:</b> Something went wrong sending file %s (%d KB) to <b> %s </b>' % (filename, file_size / 1024, who))
        else:
            self.factory.rawmode = False;
            
    


    def _showFilePicker(self, directory):
        # show filepicker
        filedialog = QtWidgets.QFileDialog()
        filedialog.setDirectory(directory)  # set default directory
        file_path = filedialog.getOpenFileName()  # get filename
        file_path = file_path[0]
        return file_path


    def _onScreenshots(self, who):
        self.log("<b>Requesting Screenshot Update </b>")
        self._workingIndicator(True, 1000)
        
        if self.factory.rawmode == True:
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            self.factory.rawmode = True;   #LOCK all other fileoperations 
    
        if not self.factory.server_to_client.request_screenshots(who):
            self.factory.rawmode = False;     # UNLOCK all fileoperations 
            self.log("No clients connected")


    def _onShowIP(self):
        self._workingIndicator(True, 500)
        show_ip()



    def _onAbgabe(self, who):
        """get SHARE folder from client"""
        self._workingIndicator(True, 500)
        self.log('Requesting Folder SHARE from <b>%s</b>' % who)
        itime = 2000 if who is 'all' else 1000
        self._workingIndicator(True, itime)

        if self.factory.rawmode == True:
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            self.factory.rawmode = True;   #LOCK all other fileoperations 

        if not self.factory.server_to_client.request_abgabe(who):
            self.factory.rawmode = False;     # UNLOCK all fileoperations 
            self.log("No clients connected")
        
        #start Thread 
        self.log("Waiting for Client to send his Abgabe-Files")
        self.waiting_thread.start()
    

    def _on_start_exam(self, who):
        """
        ZIP examconfig folder
        send configuration-zip to clients - unzip there
        invoke startexam.sh file on clients

        """
        self._workingIndicator(True, 500)
        server_to_client = self.factory.server_to_client
        
        if self.factory.rawmode == True:   #check if server is already in rawmode (ongoing filetransfer)
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            if not server_to_client.clients:        #check if there are clients connected
                self.log("No clients connected")
                return
            self.factory.rawmode = True;   #ready for filetransfer - LOCK all other fileoperations 
    
        self._workingIndicator(True, 4000)
        self.log('<b>Initializing Exam Mode On All Clients </b>')

        cleanup_abgabe = self.ui.cleanabgabe.checkState()
        # create zip file of all examconfigs
        target_folder = EXAMCONFIG_DIRECTORY
        filename = "EXAMCONFIG"
        output_filename = os.path.join(SERVERZIP_DIRECTORY, filename)
        shutil.make_archive(output_filename, 'zip', target_folder)
        filename = "%s.zip" % (filename)
        file_path = os.path.join(SERVERZIP_DIRECTORY, filename)  #now with .zip extension

        #regenerate filelist and check for zip file
        self.factory.files = get_file_list(self.factory.files_path)
        if filename not in self.factory.files:
            self.log('filename not found in directory')
            return

        self.log('Sending Configuration: %s (%d KB)' % (filename, self.factory.files[filename][1] / 1024))

        # send line and file to all clients
        server_to_client.send_file(file_path, who, DataType.EXAM.value, cleanup_abgabe )



    def _on_exit_exam(self,who):
        """
        Ends the Exammode from a Client, who=all or name
        """
        self.log("<b>Finishing Exam</b>")
        self._workingIndicator(True, 2000)
        if self.factory.lcs.running:
            # disable autoscreenshot, lcs = Loopingcall
            self.factory.lcs.stop() 

        if self.factory.lc.running:  
            icon = self.rootDir.joinpath("pixmaps/chronometer-off.png").as_posix()
            self.ui.autoabgabe.setIcon(QIcon(icon))
            #  disable autoabgabe, lc = Loopingcall
            self.factory.lc.stop()
        
        # first fetch Abgabe
        if self.factory.rawmode == True:
            self.log("Waiting for ongoing file-transfers to finish ...")
            return  
        else:
            self.factory.rawmode = True;   #LOCK all other fileoperations 

        if not self.factory.server_to_client.request_abgabe(who):
            self.factory.rawmode = False;     # UNLOCK all fileoperations 
            self.log("No clients connected")
        
        #start Thread 
        self.log("Waiting for all Clients to send their Abgabe-Files")
        #on Event call        
        self.waiting_thread.client_finished.connect(self.client_abgabe_done)
        self.waiting_thread.start()
        mutual_functions.showDesktopMessage("Abgabe Ordner ist Persönlicher Ordner/SHARE")
        
        
    def client_abgabe_done(self, who):
        """ will fired when Client has sent his Abgabe File """
        
        self.log("Client %s has finished sending Abgabe-File, now exiting ..." % who)
        onexit_cleanup_abgabe = self.ui.exitcleanabgabe.checkState()   
        #get from who the connectionID        
        item = self.get_list_widget_by_client_name(who)
        # then send the exam exit signal
        if not self.factory.server_to_client.exit_exam(item.pID, onexit_cleanup_abgabe):
            pass


    def _onStartHotspot(self):
        self._workingIndicator(True, 500)
        start_hotspot()

    def get_firewall_adress_list(self):
        return [[self.ui.firewall1,self.ui.port1],[self.ui.firewall2,self.ui.port2],[self.ui.firewall3,self.ui.port3],[self.ui.firewall4,self.ui.port4]]

    def _onTestFirewall(self):
        self._workingIndicator(True, 1000)
        ipfields = self.get_firewall_adress_list()

        if self.ui.testfirewall.text() == "Stoppe Firewall":    #really don't know why qt sometimes adds these & signs to the ui
            dialog_popup('Die Firewall wird gestoppt!')

            scriptfile = os.path.join(SCRIPTS_DIRECTORY, "exam-firewall.sh")
            startcommand = "exec %s stop &" % (scriptfile)
            os.system(startcommand)
            self.ui.testfirewall.setText("Firewall testen")

            for i in ipfields:
                palettedefault = i[0].palette()
                palettedefault.setColor(QPalette.Active, QPalette.Base, QColor(255, 255, 255))
                i[0].setPalette(palettedefault)

        elif self.ui.testfirewall.text() == "Firewall testen":
            ipstore = os.path.join(EXAMCONFIG_DIRECTORY, "EXAM-A-IPS.DB")
            open(ipstore, 'w+')  # erstelle die datei neu

            number = 0
            for i in ipfields:
                ip = i[0].text()
                port = i[1].text()
                if checkIP(ip):
                    thisexamfile = open(ipstore, 'a+')  # anhängen
                    number += 1
                    if number is not 1:  # zeilenumbruch einfügen ausser vor erster zeile (keine leerzeilen in der datei erlaubt)
                        thisexamfile.write("\n")
                    thisexamfile.write("%s:%s" %(ip,port) )
                else:
                    if ip != "":
                        palettewarn = i[0].palette()
                        palettewarn.setColor(i[0].backgroundRole(), QColor(200, 80, 80))
                        # palettewarn.setColor(QPalette.Active, QPalette.Base, QColor(200, 80, 80))
                        i[0].setPalette(palettewarn)

            dialog_popup("Die Firewall wird aktiviert!")
            scriptfile = os.path.join(SCRIPTS_DIRECTORY, "exam-firewall.sh")
            startcommand = "exec %s start &" % (scriptfile)
            os.system(startcommand)
            self.ui.testfirewall.setText("Stoppe Firewall")


    def _onAutoabgabe(self):
        self._workingIndicator(True, 500)
        intervall = self.ui.aintervall.value()
        minute_intervall = intervall * 60  # minuten nicht sekunden
        if self.factory.lc.running:
            icon = self.rootDir.joinpath("pixmaps/chronometer-off.png").as_posix()
            self.ui.autoabgabe.setIcon(QIcon(icon))
            self.factory.lc.stop()
            self.log("<b>Auto-Submission deactivated </b>")
            return
        if intervall is not 0:
            icon = self.rootDir.joinpath("pixmaps/chronometer.png").as_posix()
            self.ui.autoabgabe.setIcon(QIcon(icon))
            self.log("<b>Activated Auto-Submission every %s minutes </b>" % (str(intervall)))
            self.factory.lc.start(minute_intervall)
        else:
            self.log("Auto-Submission Intervall is set to 0 - Auto-Submission not active")


    def _onRemoveClient(self, client_id):
        """
        Entfernt einen Client aus dem Widget
        """
        self._workingIndicator(True, 500)
        client_name = self.factory.server_to_client.kick_client(client_id)
        
        if client_name:
            #SIP C++ Module deletes the Item from ListWidget
            sip.delete(self.get_list_widget_by_client_id(client_id))
            #remove client widget no matter if client still is connected or not
            # delete all ocurrances of this screenshotitem (the whole item with the according widget and its labels)
            msg='Connection to client <b> %s </b> has been <b>removed</b>.' % (client_name)
            self.log(html_to_text(msg))
            #UI Label Update
            self.ui.label_clients.setText(self.createClientsLabel())

    def _disableClientScreenshot(self, client):
        self._workingIndicator(True, 500)
        client_name = client.clientName
        client_id = client.clientConnectionID
        item = self.get_list_widget_by_client_id(client_id)
        icon = self.rootDir.joinpath("pixmaps/nouserscreenshot.png").as_posix()
        pixmap = QPixmap(icon)
        try:
            item.picture.setPixmap(pixmap)
            item.info.setText('%s \ndisconnected' % client_name)
            item.disabled = True
        except:
            #item not found because first connection attempt
            return

    def log(self, msg, onlyinGUI=True):
        """ creates an log entry inside GUI LOG Textfield """
        timestamp = '[%s]' % datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.logwidget.append(timestamp + " " + str(msg))
        if onlyinGUI==False:
            self.logger.info(html_to_text(msg))


    def createOrUpdateListItem(self, client, screenshot_file_path):
        """
        generates new List Item that displays the client screenshot
        """
        existing_item = self.get_list_widget_by_client_name(client.clientName)

        if existing_item:  # just update screenshot
            self._updateListItemScreenshot(existing_item, client, screenshot_file_path)
        else:
            self._addNewListItem(client, screenshot_file_path)
            #Update Label
            self.ui.label_clients.setText(self.createClientsLabel())


    def _addNewListItem(self, client, screenshot_file_path):
        item = QtWidgets.QListWidgetItem()
                   
        item.setSizeHint(QtCore.QSize(140, 100));
        item.id = client.clientName  # store clientName as itemID for later use (delete event)
        item.pID = client.clientConnectionID
        item.disabled = False

        pixmap = QPixmap(screenshot_file_path)
        pixmap = pixmap.scaled(QtCore.QSize(120,67))
        item.picture = QtWidgets.QLabel()
        item.picture.setPixmap(pixmap)
        item.picture.setAlignment(QtCore.Qt.AlignCenter)
        item.info = QtWidgets.QLabel('%s \n%s' % (client.clientName, client.clientConnectionID))
        item.info = QtWidgets.QLabel('%s' % (client.clientName))
        item.info.setAlignment(QtCore.Qt.AlignCenter)
        
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(1)
        grid.addWidget(item.picture, 1, 0)
        grid.addWidget(item.info, 2, 0)

        widget = QtWidgets.QWidget()
        widget.setLayout(grid)
        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(lambda: self._on_context_menu(item.pID, item.disabled))
        widget.mouseDoubleClickEvent = lambda event: self._onDoubleClick(item.pID, item.id, screenshot_file_path, item.disabled)

        self.ui.listWidget.addItem(item)  # add the listitem to the listwidget
        self.ui.listWidget.setItemWidget(item, widget)  # set the widget as the listitem's widget


    def _updateListItemScreenshot(self, existing_item, client, screenshot_file_path):
        try:
            self.factory.disconnected_list.remove(client.clientName)  # if client reconnected remove from disconnected_list
        except:
            pass            #changed return to pass otherwise the screenshot is not updated
        pixmap = QPixmap(screenshot_file_path)
        pixmap = pixmap.scaled(QtCore.QSize(120, 67))
        existing_item.picture.setPixmap(pixmap)
        existing_item.info.setText('%s' % (client.clientName))
        existing_item.pID = client.clientConnectionID  # in case this is a reconnect - update clientConnectionID in order to address the correct connection
        existing_item.disabled = False

        try:
            if self.screenshotwindow.client_connection_id == existing_item.pID:
                self.screenshotwindow.oImage = QImage(screenshot_file_path)
                self.screenshotwindow.sImage = self.screenshotwindow.oImage.scaled(QtCore.QSize(1200, 675))  # resize Image to widgets size
                self.screenshotwindow.palette = QPalette()
                self.screenshotwindow.palette.setBrush(10, QBrush(self.screenshotwindow.sImage))  # 10 = Windowrole
                self.screenshotwindow.setPalette(self.screenshotwindow.palette)
            
        except:
            pass


    def _onDoubleClick(self, client_connection_id, client_name, screenshot_file_path, client_disabled):
        if client_disabled:
            self.log("Item disabled")
            return
        screenshotfilename = "%s.jpg" % client_connection_id
        self.screenshotwindow = ScreenshotWindow(self, screenshotfilename, client_name, screenshot_file_path, client_connection_id)
        self.screenshotwindow.exec_()



    def _on_context_menu(self, client_connection_id, is_disabled):
        menu = QtWidgets.QMenu()

        action_1 = QtWidgets.QAction("Abgabe holen", menu, triggered=lambda: self._onAbgabe(client_connection_id))
        action_2 = QtWidgets.QAction("Screenshot updaten", menu, triggered=lambda: self._onScreenshots(client_connection_id))
        action_3 = QtWidgets.QAction("Datei senden", menu, triggered=lambda: self._onSendFile(client_connection_id))
        action_4 = QtWidgets.QAction("Exam starten", menu, triggered=lambda: self._on_start_exam(client_connection_id))
        action_5 = QtWidgets.QAction("Exam beenden", menu, triggered=lambda: self._on_exit_exam(client_connection_id))
        action_6 = QtWidgets.QAction("Verbindung trennen", menu,
                                     triggered=lambda: self._onRemoveClient(client_connection_id))
        menu.addActions([action_1, action_2, action_3, action_4, action_5, action_6])

        if is_disabled:
            action_1.setEnabled(False)
            action_2.setEnabled(False)
            action_3.setEnabled(False)
            action_4.setEnabled(False)
            action_5.setEnabled(False)
            action_6.setText("Widget entfernen")

        cursor = QCursor()
        menu.exec_(cursor.pos())
        return
    
    def get_list_widget_items(self):
        """
        Creates an iterable list of all widget elements aka student screenshots
        :return: list of widget items
        """
        items = []
        for index in range(self.ui.listWidget.count()):
            items.append(self.ui.listWidget.item(index))
        return items

    def get_list_widget_by_client_id(self, client_id):
        for widget in self.get_list_widget_items():
            if client_id == widget.pID:
                self.log("Found existing list widget for client connectionId %s" % client_id )
                return widget
        return False

    def get_list_widget_by_client_name(self, client_name):
        for widget in self.get_list_widget_items():
            if client_name == widget.id:
                self.log("Found existing list widget for client name %s" % client_name )
                return widget
        return False
    

    def get_existing_or_skeleton_list_widget(self, client_name):
        pass
    
            
    def newOnkeyPressEvent(self,e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.log("Close-Event triggered")
            self._onAbbrechen()

    def closeEvent(self, evnt):
        evnt.ignore()
        self.log("Close-Event triggered")
        if not self.msg:
            self._onAbbrechen()


    def _onAbbrechen(self):  # Exit button
        self.msg = QtWidgets.QMessageBox()
        self.msg.setIcon(QtWidgets.QMessageBox.Information)
        self.msg.setText("Wollen sie das Programm\nLIFE Exam Server \nbeenden?")
      
        self.msg.setWindowTitle("LiFE Exam")
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        retval = self.msg.exec_()   # 16384 = yes, 65536 = no
       
        if str(retval) == "16384":
            mutual_functions.deletePidFile()
            self.ui.close()
            os._exit(0)  # otherwise only the gui is closed and connections are kept alive
        else:
            self.msg = False
