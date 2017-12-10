#! /usr/bin/env python
# -*- coding: utf-8 -*-
# TEACHER - SERVER #
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # add application root to python path for imports

from twisted.internet.protocol import DatagramProtocol

import qt5reactor
import ipaddress
import datetime
import time
import sip
import zipfile
import ntpath
import shutil

from twisted.internet import protocol
from twisted.protocols import basic
from twisted.internet.task import LoopingCall
from config.config import *
from classes.clients import *
from common import *
from config.enums import *
# from classes.system_commander import *
import classes.system_commander as system_commander

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import QRegExp

class MyServerProtocol(basic.LineReceiver):
    """every new connection builds one MyServerProtocol object"""

    def __init__(self, factory):
        self.factory = factory  # type: MyServerFactory
        self.delimiter = '\n'
        self.clientName = ""
        self.file_handler = None
        self.file_data = ()
        self.refused = False
        self.clientConnectionID = ""

    # twisted
    def connectionMade(self):
        self.factory.client_list.add_client(self)
        self.file_handler = None
        self.file_data = ()
        self.refused = False
        self.clientConnectionID = str(self.transport.client[1])
        self.factory.window.log(
            'Connection from: %s (%d clients total)' % (
            self.transport.getPeer().host, len(self.factory.client_list.clients)))

    # twisted
    def connectionLost(self, reason):
        print reason
        self.factory.client_list.remove_client(self)
        self.file_handler = None
        self.file_data = ()
        self.factory.window.log(
            'Connection from %s lost (%d clients left)' % (
            self.transport.getPeer().host, len(self.factory.client_list.clients)))

        if not self.refused:
            self.factory.window._disableClientScreenshot(self)
            self.factory.disconnected_list.append(self.clientName)  #keep client name in disconnected_list
        else:
            try:
                self.factory.disconnected_list.remove(self.clientName)   # this one is not coming back
            except:
                return
            
    # twisted
    def rawDataReceived(self, data):
        """ handle incoming byte data """
        filename = self.file_data[2]
        file_path = os.path.join(self.factory.files_path, filename)
        # self.factory.window.log('Receiving file chunk (%d KB)' % (len(data)/1024))

        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')

        if data.endswith('\r\n'):  # Last chunk
            data = data[:-2]
            self.file_handler.write(data)
            self.file_handler.close()
            self.file_handler = None
            self.setLineMode()

            if validate_file_md5_hash(file_path, self.file_data[3]):  # everything ok..  file received
                self.factory.window.log('File %s has been successfully transferred' % (filename))

                if self.file_data[1] == DataType.SCREENSHOT:  # screenshot is received on initial connection
                    screenshot_file_path = os.path.join(SERVERSCREENSHOT_DIRECTORY, filename)
                    os.rename(file_path, screenshot_file_path)  # move image to screenshot folder
                    fixFilePermissions(SERVERSCREENSHOT_DIRECTORY)  # fix filepermission of transferred file
                    self.factory.window.createOrUpdateListItem(self, screenshot_file_path)  # make the clientscreenshot visible in the listWidget

                elif self.file_data[1] == DataType.FOLDER:
                    extract_dir = os.path.join(SERVERUNZIP_DIRECTORY, self.clientName, filename[
                                                                                       :-4])  # extract to unzipDIR / clientName / foldername without .zip (cut last four letters #shutil.unpack_archive(file_path, extract_dir, 'tar')   #python3 only but twisted RPC is not ported to python3 yet
                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        zip_ref.extractall(extract_dir)  
                    os.unlink(file_path)  # delete zip file
                    fixFilePermissions(SERVERUNZIP_DIRECTORY)  # fix filepermission of transferred file

                elif self.file_data[1] == DataType.ABGABE:
                    extract_dir = os.path.join(SHARE_DIRECTORY, self.clientName, filename[
                                                                                  :-4])  # extract to unzipDIR / clientName / foldername without .zip (cut last four letters #shutil.unpack_archive(file_path, extract_dir, 'tar')   #python3 only but twisted RPC is not ported to python3 yet
                    user_dir = os.path.join(SHARE_DIRECTORY, self.clientName)
                    checkIfFileExists(user_dir)  ## checks if filename is taken and renames this file in order to make room for the userfolder

                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        zip_ref.extractall(extract_dir) 
                    os.unlink(file_path)  # delete zip file
                    fixFilePermissions(SHARE_DIRECTORY)  # fix filepermission of transferred file

            else:  # wrong file hash
                os.unlink(file_path)
                self.transport.write('File was successfully transferred but not saved, due to invalid MD5 hash\n')
                self.transport.write(Command.ENDMSG + '\n')
                self.factory.window.log(
                    'File %s has been successfully transferred, but deleted due to invalid MD5 hash' % (filename))

        else:
            self.file_handler.write(data)

    # twisted
    def lineReceived(self, line):
        """whenever the client sends something """
        self.file_data = clean_and_split_input(line)
        if len(self.file_data) == 0 or self.file_data == '':
            return
            # command=self.file_data[0] type=self.file_data[1] filename=self.file_data[2] filehash=self.file_data[3] (( clientName=self.file_data[4] ))

        if line.startswith(Command.AUTH):  # AUTH is sent immediately after a connection is made and transfers the clientName
            print "auth request received"
            newID = self.file_data[1] 
            pincode = self.file_data[2]
            self._checkclientAuth(newID, pincode)  # check if this custom client id (entered by the student) is already taken
        elif line.startswith(Command.FILETRANSFER):
            self.factory.window.log('Incoming File Transfer from Client <b>%s </b>' % (self.clientName))
            self.setRawMode()  # this is a file - set to raw mode

    def _checkclientAuth(self, newID, pincode):
        """searches for the newID in factory.clients and rejects the connection if found or wrong pincode"""

        if newID in self.factory.client_list.clients.keys():
            print "this user already exists and is connected"
            self.refused = True
            self.sendLine(Command.REFUSED)
            self.transport.loseConnection()
            self.factory.window.log('Client Connection from %s has been refused. User already exists' % (newID))
            return
        elif int(pincode) != self.factory.pincode:
            print pincode
            print self.factory.pincode
            print "wrong pincode"
            self.refused = True
            self.sendLine(Command.REFUSED)
            self.transport.loseConnection()
            self.factory.window.log('Client Connection from %s has been refused. Wrong pincode given' % (newID))
            return
        else:  # otherwise ad this unique id to the client protocol instance and request a screenshot
            print "pincode ok"
            self.clientName = newID
            self.factory.window.log('New Connection from <b>%s </b>' % (newID))
            #transfer, send, screenshot, filename, hash, cleanabgabe
            self.sendLine("%s %s %s %s.jpg none none" % (Command.FILETRANSFER, Command.SEND, DataType.SCREENSHOT, self.transport.client[1]))
            return


class MyServerFactory(protocol.ServerFactory):

    def __init__(self, files_path, reactor):
        self.files_path = files_path
        self.reactor = reactor
        self.client_list = ClientList() # type: ClientList
        self.disconnected_list = []
        self.files = None
        self.clientslocked = False
        self.pincode = generatePin(4)
        self.examid = "Exam-%s" % generatePin(3)
        self.window = ServerUI(self)                            # type: ServerUI
        self.lc = LoopingCall(lambda: self.window._onAbgabe("all"))
        self.lcs = LoopingCall(lambda: self.window._onScreenshots("all"))
        self.lcs.start(20)   #TODO make this configurable over the UI
        # _onAbgabe kann durch lc.start(intevall) im intervall ausgeführt werden

        checkFirewall(self.window.get_firewall_adress_list())  # deactivates all iptable rules if any
        #starting multicast server here in order to provide "factory" information via broadcast
        self.reactor.listenMulticast(8005, MultcastLifeServer(self), listenMultiple=True)

    """
    http://twistedmatrix.com/documents/12.1.0/api/twisted.internet.protocol.Factory.html#buildProtocol
    """
    def buildProtocol(self, addr):
        return MyServerProtocol(self)
        """
        wird bei einer eingehenden client connection aufgerufen - erstellt ein object der klasse MyServerProtocol für jede connection und übergibt self (die factory)
        """

class MultcastLifeServer(DatagramProtocol):
    def __init__(self, factory):
         self.factory = factory

    def startProtocol(self):
        """Called after protocol has started listening. """
        self.transport.setTTL(5)     # Set the TTL>1 so multicast will cross router hops:
        self.transport.joinGroup("228.0.0.5")   # Join a specific multicast group:

    def datagramReceived(self, datagram, address):

        if "CLIENT" in datagram:
            # Rather than replying to the group multicast address, we send the
            # reply directly (unicast) to the originating port:
            print "Datagram %s received from %s" % (repr(datagram), repr(address))

            serverinfo = self.factory.examid + " " + " ".join(self.factory.disconnected_list)
            message = "SERVER %s" % serverinfo
            self.transport.write(message, ("228.0.0.5", 8005))

            #self.transport.write("SERVER: Assimilate", address)  #this is NOT WORKINC






class ScreenshotWindow(QtWidgets.QDialog):
    def __init__(self, serverui, screenshot, clientname, screenshot_file_path, client_connection_id):
        QtWidgets.QDialog.__init__(self)
        self.setWindowIcon(QIcon("pixmaps/windowicon.png"))  # definiere icon für taskleiste
        self.screenshot = screenshot
        self.serverui = serverui
        self.screenshot_file_path = screenshot_file_path
        self.client_connection_id = client_connection_id
        text =  "Screenshot - %s - %s" %(screenshot, clientname)
        self.setWindowTitle(text)
        self.setGeometry(100,100,1200,675)
        self.setFixedSize(1200, 675)
        oImage = QImage(screenshot_file_path)
        sImage = oImage.scaled(QtCore.QSize(1200,675))                   # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))                     # 10 = Windowrole
        self.setPalette(palette)

        button1 = QtWidgets.QPushButton('Screenshot archivieren', self)
        button1.move(1020, 580)
        button1.resize(150,40)
        button1.clicked.connect(self._archivescreenshot)

        button2 = QtWidgets.QPushButton('Abgabe holen', self)
        button2.move(1020, 480)
        button2.resize(150,40)
        button2.clicked.connect(lambda: serverui._onAbgabe(client_connection_id))

        button3 = QtWidgets.QPushButton('Screenshot updaten', self)
        button3.move(1020, 530)
        button3.resize(150,40)
        button3.clicked.connect(lambda: serverui._onScreenshots(client_connection_id))

        button4 = QtWidgets.QPushButton('Fenster schließen', self)
        button4.move(1020, 430)
        button4.resize(150,40)
        button4.clicked.connect(self._onClose)


    def _onClose(self):  # Exit button
        self.close()



    def _archivescreenshot(self):
        filedialog = QtWidgets.QFileDialog()
        filedialog.setDirectory(SHARE_DIRECTORY)  # set default directory
        file_path = filedialog.getSaveFileName()  # get filename
        file_path = file_path[0]

        if file_path:
            #os.rename(self.screenshot_file_path, file_path)  #moves the file (its not available in src anymore)
            shutil.copyfile(self.screenshot_file_path,file_path)
            print "screensshot archived"













class ServerUI(QtWidgets.QDialog):
    def __init__(self, factory):
        QtWidgets.QDialog.__init__(self)
        self.factory = factory     # type: MyServerFactory
        self.ui = uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.ui"))  # load UI
        self.ui.setWindowIcon(QIcon("pixmaps/windowicon.png"))  # definiere icon für taskleiste
        self.ui.exit.clicked.connect(self._onAbbrechen)  # setup Slots
        self.ui.sendfile.clicked.connect(lambda: self._onSendFile("all"))  # button x   (lambda is not needed - only if you wanna pass a variable to the function)
        self.ui.showip.clicked.connect(self._onShowIP)  # button y
        self.ui.abgabe.clicked.connect(lambda: self._onAbgabe("all"))
        self.ui.screenshots.clicked.connect(lambda: self._onScreenshots("all"))
        self.ui.startexam.clicked.connect(lambda: self._onStartExam("all"))
        self.ui.openshare.clicked.connect(self._onOpenshare)
        self.ui.starthotspot.clicked.connect(self._onStartHotspot)
        self.ui.startconfig.clicked.connect(self._onStartConfig)
        self.ui.testfirewall.clicked.connect(self._onTestFirewall)
        self.ui.loaddefaults.clicked.connect(self._onLoadDefaults)
        self.ui.autoabgabe.clicked.connect(self._onAutoabgabe)
        self.ui.screenlock.clicked.connect(lambda: self._onScreenlock("all"))
        self.ui.exitexam.clicked.connect(lambda: self._onExitExam("all"))
        self.ui.closeEvent = self.closeEvent  # links the window close event to our custom ui
        self.ui.printconf.clicked.connect(self._onPrintconf)
        self.ui.printer.clicked.connect(lambda: self._onSendPrintconf("all"))

        self.workinganimation = QMovie("pixmaps/working.gif", QtCore.QByteArray(), self)
        self.workinganimation.setCacheMode(QMovie.CacheAll)
        self.workinganimation.setSpeed(100)
        self.ui.working.setMovie(self.workinganimation)
        self.timer = False
        self.ui.version.setText("<b>Version</b> %s" % VERSION )
        self.ui.currentpin.setText("<b>%s</b>" % self.factory.pincode  )
        self.ui.examlabeledit1.setText(self.factory.examid  )
        self.ui.currentlabel.setText("<b>%s</b>" % self.factory.examid  )
        self.ui.examlabeledit1.textChanged.connect(self._updateExamName)

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

        self.ui.show()


    def _onSendPrintconf(self,who):
        """send the printer configuration to all clients"""
        self._workingIndicator(True, 500)
        client_list = self.factory.client_list

        if not client_list.clients:
            self.log("no clients connected")
            return

        self._workingIndicator(True, 4000)
        self.log('<b>Sending Printer Configuration to All Clients </b>')
        system_commander.dialog_popup('Sending Printer Configuration to All Clients')

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
            self.log('filename not found in directory')
            return

        self.log('Sending Configuration: %s (%d KB)' % (filename, self.factory.files[filename][1] / 1024))



        # send line and file to all clients
        client_list.send_file(file_path, who, DataType.PRINTER)






    def _onPrintconf(selfs):
        command = "kcmshell5 kcm_printer_manager &"
        os.system(command)

    def _onScreenlock(self,who):
        """locks the client screens"""
        self.log("<b>Locking Client Screens </b>")
        self._workingIndicator(True, 1000)

        if self.factory.clientslocked:
            self.ui.screenlock.setIcon(QIcon("pixmaps/network-wired-symbolic.png"))
            self.factory.clientslocked = False
            if not self.factory.client_list.unlock_screens(who):
                self.log("no clients connected")
        else:
            self.ui.screenlock.setIcon(QIcon("pixmaps/unlock.png"))
            self.factory.clientslocked = True
            if not self.factory.client_list.lock_screens(who):
                self.log("no clients connected")
                self.factory.clientslocked = False
                self.ui.screenlock.setIcon(QIcon("pixmaps/network-wired-symbolic.png"))


    def _onOpenshare(self):
        startcommand = "exec sudo -u %s -H /usr/bin/dolphin %s &" %(USER ,SHARE_DIRECTORY)
        os.system(startcommand)

    def _updateExamName(self):
        self.factory.examid = self.ui.examlabeledit1.text()
        self.ui.currentlabel.setText("<b>%s</b>" % self.factory.examid  )

    def closeEvent(self, evnt):
        #self.showMinimized()  #shows a weird window in the last version #FIXME
        evnt.ignore()

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
        """send a file to all clients"""
        self._workingIndicator(True, 500)
        client_list = self.factory.client_list

        if not client_list.clients:
            self.log("no clients connected")
            return

        file_path = self._showFilePicker(SHARE_DIRECTORY)

        if file_path:
            self._workingIndicator(True, 2000) # TODO: change working indicator to choose its own time depending on actions requiring all clients or only one client
            success, filename, file_size, who = client_list.send_file(file_path, who, DataType.FILE)

            if success:
                self.log('<b>Sending file:</b> %s (%d KB) to <b> %s </b>' % (filename, file_size / 1024, who))
            else:
                self.log('<b>Sending file:</b> Something went wrong sending file %s (%d KB) to <b> %s </b>' % (filename, file_size / 1024, who))

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
        if not self.factory.client_list.request_screenshots(who):
            self.log("no clients connected")

    def _onShowIP(self):
        self._workingIndicator(True, 500)
        system_commander.show_ip()

    def _onAbgabe(self, who):
        self._workingIndicator(True, 500)
        """get SHARE folder"""
        self.log('<b>Requesting Client Folder SHARE </b>')
        itime = 2000 if who is 'all' else 1000
        self._workingIndicator(True, itime)
        if not self.factory.client_list.request_abgabe(who):
            self.log("no clients connected")

    def _onStartExam(self, who):
        """
                ZIP examconfig folder
                send configuration-zip to clients - unzip there
                invoke startexam.sh file on clients

                """
        self._workingIndicator(True, 500)
        client_list = self.factory.client_list
        if not client_list.clients:
            self.log("no clients connected")
            return

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

        # check for exam mode
        if self.ui.radiomath.isChecked():
            subject = "math"
        else:
            subject = "lang"

        # send line and file to all clients
        client_list.send_file(file_path, who, DataType.EXAM, cleanup_abgabe, subject )

        # for client in client_list.clients.values():
        #     #command.filtransfer and command.get trigger rawMode on clients - Datatype.exam triggers exam mode after filename is received
        #     client.transport.write('%s %s %s %s %s %s %s\n' % (Command.FILETRANSFER, Command.GET, DataType.EXAM, filename, self.factory.files[filename][2], cleanup_abgabe, subject ))
        #     client.setRawMode()
        #
        #     print self.factory.files[filename][0]
        #     for bytes in read_bytes_from_file(self.factory.files[filename][0]):
        #         client.transport.write(bytes)
        #
        #     client.transport.write('\r\n')
        #     client.setLineMode()



    def _onExitExam(self,who):
        self.log("<b>Finishing Exam </b>")
        self._workingIndicator(True, 2000)
        # first fetch abgabe
        if not self.factory.client_list.request_abgabe(who):
            self.log("no clients connected")
        # then send the exam exit signal
        if not self.factory.client_list.exit_exam(who):
            self.log("no clients connected")




    def _onStartConfig(self):
        self._workingIndicator(True, 500)
        if self.ui.radiomath.isChecked():
            subject = "math"
        else:
            subject = "lang"
        system_commander.start_config(subject)
        self.ui.close()

    def _onStartHotspot(self):
        self._workingIndicator(True, 500)
        system_commander.start_hotspot()

    def get_firewall_adress_list(self):
        return [[self.ui.firewall1,self.ui.port1],[self.ui.firewall2,self.ui.port2],[self.ui.firewall3,self.ui.port3],[self.ui.firewall4,self.ui.port4]]

    def _onTestFirewall(self):
        self._workingIndicator(True, 1000)
        ipfields = self.get_firewall_adress_list()

        if self.ui.testfirewall.text() == "Stoppe &Firewall":    #really don't know why qt sometimes adds these & signs to the ui
            system_commander.dialog_popup('Die Firewall wird gestoppt!')

            scriptfile = os.path.join(SCRIPTS_DIRECTORY, "exam-firewall.sh")
            startcommand = "exec %s stop &" % (scriptfile)
            os.system(startcommand)
            self.ui.testfirewall.setText("Firewall testen")

            for i in ipfields:
                palettedefault = i[0].palette()
                palettedefault.setColor(QPalette.Active, QPalette.Base, QColor(255, 255, 255))
                i[0].setPalette(palettedefault)

        elif self.ui.testfirewall.text() == "&Firewall testen":
            ipstore = os.path.join(EXAMCONFIG_DIRECTORY, "EXAM-A-IPS.DB")
            openedexamfile = open(ipstore, 'w+')  # erstelle die datei neu

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

            system_commander.dialog_popup("Die Firewall wird aktiviert!")

            scriptfile = os.path.join(SCRIPTS_DIRECTORY, "exam-firewall.sh")
            startcommand = "exec %s start &" % (scriptfile)
            os.system(startcommand)
            self.ui.testfirewall.setText("Stoppe Firewall")

    def _onLoadDefaults(self):
        self._workingIndicator(True, 500)
        showDesktopMessage('Default Configuration for EXAM Desktop restored.')
        self.log('Default Configuration for EXAM Desktop restored.')

        system_commander.copy('./DATA/EXAMCONFIG', WORK_DIRECTORY)

    def _onAutoabgabe(self):
        self._workingIndicator(True, 500)
        intervall = self.ui.aintervall.value()
        minute_intervall = intervall * 60  # minuten nicht sekunden
        if self.factory.lc.running:
            self.ui.autoabgabe.setIcon(QIcon("pixmaps/chronometer-off.png"))
            self.factory.lc.stop()
            self.log("<b>Auto-Submission deactivated </b>")
            return
        if intervall is not 0:
            self.ui.autoabgabe.setIcon(QIcon("pixmaps/chronometer.png"))
            self.log("<b>Activated Auto-Submission every %s minutes </b>" % (str(intervall)))
            self.factory.lc.start(minute_intervall)
        else:
            self.log("Auto-Submission Intervall is set to 0 - Auto-Submission not active")

    def _onRemoveClient(self, client_id):
        self._workingIndicator(True, 500)
        client_name = self.factory.client_list.kick_client(client_id)
        #if client_name:
        sip.delete(self.get_list_widget_by_client_id(client_id))   #remove client widget no matter if client still is connected or not
            # delete all ocurrances of this screenshotitem (the whole item with the according widget and its labels)
        self.log('Connection to client <b> %s </b> has been <b>removed</b>.' % client_name)

    def _disableClientScreenshot(self, client):
        self._workingIndicator(True, 500)
        client_name = client.clientName
        client_id = client.clientConnectionID
        item = self.get_list_widget_by_client_id(client_id)
        pixmap = QPixmap("pixmaps/nouserscreenshot.png")
        try:
            item.picture.setPixmap(pixmap)
            item.info.setText('%s \ndisconnected' % client_name)
            item.disabled = True
        except:
            #item not found because first connection attempt
            return

    def log(self, msg):
        timestamp = '[%s]' % datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.logwidget.append(timestamp + " " + str(msg))

    def _onAbbrechen(self):  # Exit button
        os.remove(SERVER_PIDFILE)
        self.ui.close()
        os._exit(0)  # otherwise only the gui is closed and connections are kept alive

    def createOrUpdateListItem(self, client, screenshot_file_path):
        """generates new listitem that displays the clientscreenshot"""
        existing_item = self.get_list_widget_by_client_name(client.clientName)

        if existing_item:  # just update screenshot
            self._updateListItemScreenshot(existing_item, client, screenshot_file_path)
        else:
            self._addNewListItem(client, screenshot_file_path)

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
        widget.mouseDoubleClickEvent = lambda event: self._onDoubleClick(item.pID, item.id, screenshot_file_path)

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
            self.screenshotwindow.oImage = QImage(screenshot_file_path)
            self.screenshotwindow.sImage = self.screenshotwindow.oImage.scaled(QtCore.QSize(1200, 675))  # resize Image to widgets size
            self.screenshotwindow.palette = QPalette()
            self.screenshotwindow.palette.setBrush(10, QBrush(self.screenshotwindow.sImage))  # 10 = Windowrole
            self.screenshotwindow.setPalette(self.screenshotwindow.palette)
        except:
            pass


    def _onDoubleClick(self, client_connection_id, client_name, screenshot_file_path):
        screenshotfilename = "%s.jpg" % client_connection_id
        self.screenshotwindow = ScreenshotWindow(self, screenshotfilename, client_name, screenshot_file_path, client_connection_id)
        self.screenshotwindow.exec_()



    def _on_context_menu(self, client_connection_id, is_disabled):
        menu = QtWidgets.QMenu()

        action_1 = QtWidgets.QAction("Abgabe holen", menu, triggered=lambda: self._onAbgabe(client_connection_id))
        action_2 = QtWidgets.QAction("Screenshot updaten", menu, triggered=lambda: self._onScreenshots(client_connection_id))
        action_3 = QtWidgets.QAction("Datei senden", menu, triggered=lambda: self._onSendFile(client_connection_id))
        action_4 = QtWidgets.QAction("Exam starten", menu, triggered=lambda: self._onStartExam(client_connection_id))
        action_5 = QtWidgets.QAction("Exam beenden", menu, triggered=lambda: self._onExitExam(client_connection_id))
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
        for index in xrange(self.ui.listWidget.count()):
            items.append(self.ui.listWidget.item(index))
        return items

    def get_list_widget_by_client_id(self, client_id):
        for widget in self.get_list_widget_items():
            if client_id == widget.pID:
                print "Found existing list widget for client connectionId %s" % client_id
                return widget
        return False

    def get_list_widget_by_client_name(self, client_name):
        for widget in self.get_list_widget_items():
            if client_name == widget.id:
                print "Found existing list widget for client name %s" % client_name
                return widget
        return False

    def get_existing_or_skeleton_list_widget(self, client_name):
        pass

if __name__ == '__main__':
    prepareDirectories()  # cleans everything and copies some scripts
    killscript = os.path.join(SCRIPTS_DIRECTORY, "terminate-exam-process.sh")
    os.system("sudo %s %s" % (killscript, 'server'))  # make sure only one client instance is running per client
    # time.sleep(1)
    writePidFile()

    app = QtWidgets.QApplication(sys.argv)
    qt5reactor.install()  # imported from file and needed for Qt to function properly in combination with twisted reactor

    from twisted.internet import reactor

    reactor.listenTCP(SERVER_PORT, MyServerFactory(SERVERFILES_DIRECTORY, reactor ))  # start the server on SERVER_PORT
    # moved multicastserver starting sequence to factory
    #reactor.listenMulticast(8005, MultcastLifeServer(), listenMultiple=True)

    print ('Listening on port %d' % (SERVER_PORT))
    reactor.run()
