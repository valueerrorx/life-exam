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
import sip
import zipfile
import ntpath

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
        self.factory.client_list.remove_client(self)
        self.file_handler = None
        self.file_data = ()
        self.factory.window.log(
            'Connection from %s lost (%d clients left)' % (
            self.transport.getPeer().host, len(self.factory.client_list.clients)))

        if not self.refused:
            self.factory.window._disableClientScreenshot(self)

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
                        zip_ref.extractall(extract_dir)  # derzeitiges verzeichnis ist .life/SERVER/unzip
                    os.unlink(file_path)  # delete zip file
                    fixFilePermissions(SERVERUNZIP_DIRECTORY)  # fix filepermission of transferred file

                elif self.file_data[1] == DataType.ABGABE:
                    extract_dir = os.path.join(ABGABE_DIRECTORY, self.clientName, filename[
                                                                                  :-4])  # extract to unzipDIR / clientName / foldername without .zip (cut last four letters #shutil.unpack_archive(file_path, extract_dir, 'tar')   #python3 only but twisted RPC is not ported to python3 yet
                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        zip_ref.extractall(extract_dir)  # derzeitiges verzeichnis ist .life/SERVER/unzip
                    os.unlink(file_path)  # delete zip file
                    fixFilePermissions(ABGABE_DIRECTORY)  # fix filepermission of transferred file

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

        if line.startswith(Command.AUTH):
            newID = self.file_data[
                1]  # AUTH is sent immediately after a connection is made and transfers the clientName
            self._checkclientName(newID)  # check if this custom client id (entered by the student) is already taken
        elif line.startswith(Command.FILETRANSFER):
            self.factory.window.log('Incoming File Transfer from Client <b>%s </b>' % (self.clientName))
            self.setRawMode()  # this is a file - set to raw mode

    def _checkclientName(self, newID):
        """searches for the newID in factory.clients and rejects the connection if found"""

        if newID in self.factory.client_list.clients.keys():
            print "this user already exists and is connected"
            self.refused = True
            self.sendLine(Command.REFUSED)
            self.transport.loseConnection()
            self.factory.log('Client Connection from %s has been refused. User already exists' % (newID))

            return
        else:  # otherwise ad this unique id to the client protocol instance and request a screenshot
            self.clientName = newID
            self.factory.window.log('New Connection from <b>%s </b>' % (newID))
            self.sendLine("%s %s %s %s.jpg none" % (
                Command.FILETRANSFER, Command.SEND, DataType.SCREENSHOT, self.transport.client[1]))

            return


class MyServerFactory(protocol.ServerFactory):

    def __init__(self, files_path):
        self.files_path = files_path
        self.client_list = ClientList()                         # type: ClientList
        self.files = None
        self.window = ServerUI(self)                            # type: ServerUI
        self.lc = LoopingCall(lambda: self._onAbgabe("all"))
        # _onAbgabe kann durch lc.start(intevall) im intervall ausgeführt werden
        checkFirewall(self.window.get_firewall_adress_list())  # deactivates all iptable rules if any


    """
    http://twistedmatrix.com/documents/12.1.0/api/twisted.internet.protocol.Factory.html#buildProtocol
    """
    def buildProtocol(self, addr):
        return MyServerProtocol(self)
        """
        wird bei einer eingehenden client connection aufgerufen - erstellt ein object der klasse MyServerProtocol für jede connection und übergibt self (die factory)
        """

class MultcastLifeServer(DatagramProtocol):
    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(5)
        # Join a specific multicast group:
        self.transport.joinGroup("228.0.0.5")
        # self.transport.write("SERVER: Assimilate", ("228.0.0.5", 8005))

    def datagramReceived(self, datagram, address):
        print "Datagram %s received from %s" % (repr(datagram), repr(address))
        if "CLIENT" in datagram:
            # Rather than replying to the group multicast address, we send the
            # reply directly (unicast) to the originating port:
            self.transport.write('SERVER: Assimilate', ("228.0.0.5", 8005))
            self.transport.write("SERVER: Assimilate", address)


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
        self.ui.startexam.clicked.connect(self._onStartExam)
        self.ui.starthotspot.clicked.connect(self._onStartHotspot)
        self.ui.startconfig.clicked.connect(self._onStartConfig)
        self.ui.testfirewall.clicked.connect(self._onTestFirewall)
        self.ui.loaddefaults.clicked.connect(self._onLoadDefaults)
        self.ui.autoabgabe.clicked.connect(self._onAutoabgabe)
        self.ui.closeEvent = self.closeEvent  # links the window close event to our custom ui

        self.workinganimation = QMovie("pixmaps/working.gif", QtCore.QByteArray(), self)
        self.workinganimation.setCacheMode(QMovie.CacheAll)
        self.workinganimation.setSpeed(100)
        self.ui.working.setMovie(self.workinganimation)
        self.timer = False
        self.ui.show()

    def closeEvent(self, evnt):
        self.showMinimized()
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

        file_path = self._showFilePicker(ABGABE_DIRECTORY)

        if file_path:
            self._workingIndicator(True, 2000) # TODO: change working indicator to choose its own time depending on actions requiring all clients or only one client
            success, filename, file_size, who = client_list.send_file(file_path, who)

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
        """get ABGABE folder"""
        self.log('<b>Requesting Client Folder ABGABE </b>')
        time = 2000 if who is 'all' else 1000
        self._workingIndicator(True, time)
        if not self.factory.client_list.request_abgabe(who):
            self.window.log("no clients connected")

    def _onStartExam(self):
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
        target_folder = EXAMCONFIG_DIRECTORY
        filename = "EXAMCONFIG"
        output_filename = os.path.join(SERVERZIP_DIRECTORY, filename)
        shutil.make_archive(output_filename, 'zip', target_folder)
        filename = "%s.zip" % (filename)


        self.factory.files = get_file_list(self.factory.files_path)
        if filename not in self.factory.files:
            self.log('filename not found in directory')
            return

        self.log('Sending Configuration: %s (%d KB)' % (filename, self.factory.files[filename][1] / 1024))

        for client in client_list.clients.values():
            #command.filtransfer and command.get trigger rawMode on clients - Datatype.exam triggers exam mode after filename is received
            client.transport.write('%s %s %s %s %s %s\n' % (Command.FILETRANSFER, Command.GET, DataType.EXAM, filename, self.factory.files[filename][2], cleanup_abgabe ))
            client.setRawMode()

            print self.factory.files[filename][0]
            for bytes in read_bytes_from_file(self.factory.files[filename][0]):
                client.transport.write(bytes)

            client.transport.write('\r\n')
            client.setLineMode()

    def _onStartConfig(self):
        self._workingIndicator(True, 500)
        system_commander.start_exam()
        self.ui.close()

    def _onStartHotspot(self):
        self._workingIndicator(True, 500)
        system_commander.start_hotspot()

    def _onTestFirewall(self):
        self._workingIndicator(True, 1000)
        ipfields = self.get_firewall_adress_list()
        if self.ui.testfirewall.text() == "&Stoppe Firewall":
            system_commander.dialog_popup('Die Firewall wird gestoppt!')

            scriptfile = os.path.join(SCRIPTS_DIRECTORY, "exam-firewall.sh")
            startcommand = "exec %s stop &" % (scriptfile)
            os.system(startcommand)
            self.ui.testfirewall.setText("Firewall testen")

            for i in ipfields:
                palettedefault = i.palette()
                palettedefault.setColor(QPalette.Active, QPalette.Base, QColor(255, 255, 255))
                i.setPalette(palettedefault)

        elif self.ui.testfirewall.text() == "&Firewall testen":
            ipstore = os.path.join(EXAMCONFIG_DIRECTORY, "EXAM-A-IPS.DB")
            openedexamfile = open(ipstore, 'w+')  # erstelle die datei neu

            number = 0
            for i in ipfields:
                ip = i.text()
                if checkIP(ip):
                    thisexamfile = open(ipstore, 'a+')  # anhängen
                    number += 1
                    if number is not 1:  # zeilenumbruch einfügen ausser vor erster zeile (keine leerzeilen in der datei erlaubt)
                        thisexamfile.write("\n")
                    thisexamfile.write("%s" % ip)
                else:
                    if ip != "":
                        palettewarn = i.palette()
                        palettewarn.setColor(i.backgroundRole(), QColor(200, 80, 80))
                        # palettewarn.setColor(QPalette.Active, QPalette.Base, QColor(200, 80, 80))
                        i.setPalette(palettewarn)

            system_commander.dialog_popup("Die Firewall wird aktiviert!")

            scriptfile = os.path.join(SCRIPTS_DIRECTORY, "exam-firewall.sh")
            startcommand = "exec %s start &" % (scriptfile)
            os.system(startcommand)
            self.ui.testfirewall.setText("Stoppe Firewall")

    def _onLoadDefaults(self):
        self._workingIndicator(True, 500)
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
        if client_name:
            sip.delete(self.get_list_widget_by_client_id(client_id))
            # delete all ocurrances of this screenshotitem (the whole item with the according widget and its labels)
        self.log('Connection to client <b> %s </b> has been <b>removed</b>.' % client_name)

    def _disableClientScreenshot(self, client):
        self._workingIndicator(True, 500)
        client_name = client.clientName
        client_id = client.clientConnectionID
        item = self.get_list_widget_by_client_id(client_id)
        pixmap = QPixmap("pixmaps/nouserscreenshot.png")
        item.picture.setPixmap(pixmap)
        item.info.setText('%s \ndisconnected' % client_name)
        item.disabled = True

    def log(self, msg):
        timestamp = '[%s]' % datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.logwidget.append(timestamp + " " + str(msg))

    def _onAbbrechen(self):  # Exit button
        os.remove(SERVER_PIDFILE)
        self.ui.close()
        os._exit(0)  # otherwise only the gui is closed and connections are kept alive

    def get_firewall_adress_list(self):
        return [self.ui.firewall1, self.ui.firewall2, self.ui.firewall3, self.ui.firewall4]

    def createOrUpdateListItem(self, client, screenshot_file_path):
        """generates new listitem that displays the clientscreenshot"""
        existing_item = self.get_list_widget_by_client_name(client.clientName)

        if existing_item:  # just update screenshot
            self._updateListItemScreenshot(existing_item, client, screenshot_file_path)
        else:
            self._addNewListItem(client, screenshot_file_path)

    def _addNewListItem(self, client, screenshot_file_path):
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(140, 140));
        item.id = client.clientName  # store clientName as itemID for later use (delete event)
        item.pID = client.clientConnectionID
        item.disabled = False

        pixmap = QPixmap(screenshot_file_path)
        item.picture = QtWidgets.QLabel()
        item.picture.setPixmap(pixmap)
        item.picture.setAlignment(QtCore.Qt.AlignCenter)
        item.info = QtWidgets.QLabel('%s \n%s' % (client.clientName, client.clientConnectionID))
        item.info.setAlignment(QtCore.Qt.AlignCenter)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(4)
        grid.addWidget(item.picture, 1, 0)
        grid.addWidget(item.info, 2, 0)

        widget = QtWidgets.QWidget()
        widget.setLayout(grid)
        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(lambda: self._on_context_menu(item.pID, item.disabled))

        self.ui.listWidget.addItem(item)  # add the listitem to the listwidget
        self.ui.listWidget.setItemWidget(item, widget)  # set the widget as the listitem's widget

    def _updateListItemScreenshot(self, existing_item, client, screenshot_file_path):
        pixmap = QPixmap(screenshot_file_path)
        existing_item.picture.setPixmap(pixmap)
        existing_item.info.setText('%s \n%s' % (client.clientName, client.clientConnectionID))
        existing_item.pID = client.clientConnectionID  # in case this is a reconnect - update clientConnectionID in order to address the correct connection
        existing_item.disabled = False

    def _on_context_menu(self, client_connection_id, is_disabled):
        menu = QtWidgets.QMenu()

        action_1 = QtWidgets.QAction("Abgabe holen", menu, triggered=lambda: self._onAbgabe(client_connection_id))
        action_2 = QtWidgets.QAction("Screenshot updaten", menu, triggered=lambda: self._onScreenshots(client_connection_id))
        action_3 = QtWidgets.QAction("Datei senden", menu, triggered=lambda: self._onSendFile(client_connection_id))
        action_4 = QtWidgets.QAction("Verbindung beenden", menu, triggered=lambda: self._onRemoveClient(client_connection_id))

        menu.addActions([action_1, action_2, action_3, action_4])

        if is_disabled:
            action_1.setEnabled(False)
            action_2.setEnabled(False)
            action_3.setEnabled(False)

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

    reactor.listenTCP(SERVER_PORT, MyServerFactory(SERVERFILES_DIRECTORY))  # start the server on SERVER_PORT

    reactor.listenMulticast(8005, MultcastLifeServer(),
                            listenMultiple=True)

    print ('Listening on port %d' % (SERVER_PORT))
    reactor.run()
