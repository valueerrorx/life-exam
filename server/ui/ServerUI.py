#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import os
import shutil
import sip
import time
from pathlib import Path

from config.config import VERSION, PRINTERCONFIG_DIRECTORY,\
    SERVERZIP_DIRECTORY, SHARE_DIRECTORY, USER, EXAMCONFIG_DIRECTORY,\
    SCRIPTS_DIRECTORY, DEBUG_PIN
from config.enums import DataType
from server.resources.Applist import findApps
from classes.system_commander import dialog_popup, show_ip, start_hotspot,\
    get_primary_ip

from classes.mutual_functions import get_file_list, checkIP

from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QRegExp
from PyQt5.Qt import QRegExpValidator, QFileDialog, Qt
from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap, QImage, QBrush, QCursor
from classes.HTMLTextExtractor import html_to_text

from classes import mutual_functions

from server.resources.MyCustomWidget import MyCustomWidget
from server.resources.ScreenshotWindow import ScreenshotWindow
from server.ui.NetworkProgressBar import NetworkProgressBar
from server.ui.threads.Thread_Progress_Events import client_abgabe_done,\
    client_abgabe_done_exit_exam, client_received_file_done, client_lock_screen,\
    client_unlock_screen
from server.ui.threads.Thread_Progress import Thread_Progress
from server.ui.threads.Heartbeat import Heartbeat


class ServerUI(QtWidgets.QDialog):
    def __init__(self, factory, splash, app):
        """
        :param factory: Server Factory
        :param splash: the Splashscreen started in Main Application
        :param app: the main QApplication
        """
        QtWidgets.QDialog.__init__(self)
        self.logger = logging.getLogger(__name__)
        uic.uiparser.logger.setLevel(logging.INFO)
        uic.properties.logger.setLevel(logging.INFO)

        self.application = app
        self.splashscreen = splash
        # loadUI, findApps, timeout
        self.splashscreen.setProgressMax(3)
        self.splashscreen.setMessage("Loading UI")

        self.factory = factory     # type: MyServerFactory
        # rootDir of Application
        self.rootDir = Path(__file__).parent.parent.parent

        uifile = self.rootDir.joinpath('server/server.ui')
        self.ui = uic.loadUi(uifile)        # load UI

        self.splashscreen.step()
        self.application.processEvents()

        iconfile = self.rootDir.joinpath('pixmaps/windowicon.png').as_posix()
        self.ui.setWindowIcon(QIcon(iconfile))  # definiere icon für taskleiste

        # only debug if DEBUG_PIN is not ""
        debug_css = ""
        if DEBUG_PIN != "":
            self.ui.setWindowTitle(".: DEBUG MODE :. - Exam Server - .: DEBUG MODE :.")
            debug_css = "QDialog{ background: #ffffbf; }"
        else:
            self.ui.setWindowTitle("Exam Server")

        self.ui.exit.clicked.connect(self._onAbbrechen)  # setup3 Slots
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
        self.ui.info_label.setText("")
        self.application.processEvents()

        self.timer = False
        self.msg = False
        self.ui.version.setText("<b>Version</b> %s" % VERSION)
        self.ui.currentpin.setText("<b>%s</b>" % self.factory.pincode)
        self.ui.examlabeledit1.setText(self.factory.examid)
        self.ui.currentlabel.setText("<b>%s</b>" % self.factory.examid)
        self.ui.examlabeledit1.textChanged.connect(self._updateExamName)
        self.ui.ssintervall.valueChanged.connect(self._changeAutoscreenshot)
        self.ui.label_clients.setText(self.createClientsLabel())
        # ProgressBar Network operations
        self.networkProgress = NetworkProgressBar(self.ui.networkProgress)

        self.filedialog = QtWidgets.QFileDialog()

        num_regex = QRegExp("[0-9_]+")
        num_validator = QRegExpValidator(num_regex)
        ip_regex = QRegExp("[0-9\._]+")
        ip_validator = QRegExpValidator(ip_regex)

        self.ui.firewall1.setValidator(ip_validator)
        self.ui.firewall2.setValidator(ip_validator)
        self.ui.firewall3.setValidator(ip_validator)
        self.ui.firewall4.setValidator(ip_validator)

        self.ui.port1.setValidator(num_validator)
        self.ui.port2.setValidator(num_validator)
        self.ui.port3.setValidator(num_validator)
        self.ui.port4.setValidator(num_validator)

        # Applications ------------------------------------------------------
        self.splashscreen.setMessage("Generating Application List")
        findApps(self.ui.applist, self.ui.appview, self.application)
        self.splashscreen.step()

        # Waiting Thread
        self.progress_thread = Thread_Progress(self)
        # connect Events
        self.progress_thread.client_finished.connect(client_abgabe_done)
        self.progress_thread.client_finished.connect(client_abgabe_done_exit_exam)
        self.progress_thread.client_received_file.connect(client_received_file_done)
        self.progress_thread.client_lock_screen.connect(client_lock_screen)
        self.progress_thread.client_unlock_screen.connect(client_unlock_screen)

        # get your IP
        self.ui.currentip.setText("<b>%s</b>" % get_primary_ip())

        # CSS Styling
        self.ui.listWidget.setStyleSheet("""
            QListWidget::item{
                background: rgb(255,255,255);
            }
            QListWidget::item:selected{
                background: rgb(255,227,245);
            }""")

        self.ui.setStyleSheet("""
            QToolTip{
                background: #ffff96;
                color: #000000;
                border: 1px solid #666666;
            }""" + debug_css)

        self.splashscreen.step()
        if DEBUG_PIN == "":
            time.sleep(3)  # only if not debugging
        self.splashscreen.setMessage("Done")
        self.splashscreen.finish(self)

        # Heartbeat Thread
        self.heartbeat = Heartbeat(self)
        self.heartbeat.client_is_dead.connect(self.removeZombie)
        self.heartbeat.start()

        self.ui.keyPressEvent = self.newOnkeyPressEvent
        self.ui.show()
        # TEST
        # file_path = self._showFilePicker(SHARE_DIRECTORY)

    def createClientsLabel(self):
        """ Erzeugt den Text für Clients: <Anzahl> """
        return ("Clients: <b>%s</b>" % self.ui.listWidget.count())

    def _changeAutoscreenshot(self):
        self._show_workingIndicator(200, "Screenshot intervall gesetzt")
        intervall = self.ui.ssintervall.value()

        if self.factory.lcs.running:
            self.factory.lcs.stop()
        if intervall != 0:
            self.log("<b>Changed Screenshot Intervall to %s seconds </b>" % (str(intervall)))
            self.factory.lcs.start(intervall)
        else:
            self.log("<b>Screenshot Intervall is set to 0 - Screenshotupdate deactivated</b>")

    def _onSendPrintconf(self, who):
        """send the printer configuration to all clients"""
        self._show_workingIndicator(500, "Drucker Konfiguration senden")
        server_to_client = self.factory.server_to_client

        if self.factory.rawmode is True:   # check if server is already in rawmode (ongoing filetransfer)
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            if not server_to_client.clients:        # check if there are clients connected
                self.log("No clients connected")
                return
            self.factory.rawmode = True  # ready for filetransfer - LOCK all other fileoperations

        self._show_workingIndicator(4000)
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

    def _onScreenlock(self, who):
        """locks or unlock the client screens"""
        clients = self.get_list_widget_items()

        self._startWorkingIndicator("Locking Client Screens ... ")
        self.networkProgress.show(len(clients))

        # Waiting Thread
        self.progress_thread.restart(clients)

        if self.factory.clientslocked:
            self.log("<b>UnLocking Client Screens</b>")
            icon = self.rootDir.joinpath("pixmaps/network-wired-symbolic.png").as_posix()
            self.ui.screenlock.setIcon(QIcon(icon))
            self.factory.clientslocked = False

            if self.factory.rawmode is True:    # dirty hack - thx to nora - gives us at least one option to open filetransfers again if something wicked happens
                self.factory.rawmode = False

            if not self.factory.server_to_client.unlock_screens(who):
                self.log("No clients connected")
        else:
            self.log("<b>Locking Client Screens</b>")
            icon = self.rootDir.joinpath("pixmaps/unlock.png").as_posix()
            self.ui.screenlock.setIcon(QIcon(icon))
            self.factory.clientslocked = True
            if not self.factory.server_to_client.lock_screens(who):
                self.log("No clients connected")
                self.factory.clientslocked = False
                icon = self.rootDir.joinpath("pixmaps/network-wired-symbolic.png.png").as_posix()
                self.ui.screenlock.setIcon(QIcon(icon))
        self._onScreenshots("all")   # update screenshots right after un/lock

    def _onOpenshare(self):
        startcommand = "runuser -u %s /usr/bin/dolphin %s &" % (USER, SHARE_DIRECTORY)
        os.system(startcommand)

    def _updateExamName(self):
        self.factory.examid = self.ui.examlabeledit1.text()
        self.ui.currentlabel.setText("<b>%s</b>" % self.factory.examid)

    def _startWorkingIndicator(self, info=""):
        """ display and start the indicator, no timeout """
        if self.timer and self.timer.isActive:  # running indicator
            self.timer.stop()

        self.workinganimation.stop()
        self.ui.info_label.setText("%s ..." % info)
        time.sleep(0.1)
        self.workinganimation.start()
        self.ui.working.show()

    def _stopWorkingIndicator(self):
        """ stop and hide the working indicator """
        self.workinganimation.stop()
        self.ui.info_label.setText("")
        self.ui.working.hide()

    def stopWorkingIndicatorTimer(self):
        self.workinganimation.stop()
        self.ui.info_label.setText("")
        self.ui.working.hide()

    def _show_workingIndicator(self, duration, info=""):
        if self.timer and self.timer.isActive:  # stop old kill-timer
            self.timer.stop()

        self.workinganimation.start()
        self.ui.info_label.setText("%s ..." % info)
        self.ui.working.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.stopWorkingIndicatorTimer)
        self.timer.start(duration)

    def _onSendFile(self, client_id):
        """
        send a file to single or all clients
        who = connection ID or 'all'
        """
        server_to_client = self.factory.server_to_client

        # check if server is already in rawmode (ongoing filetransfer)
        if self.factory.rawmode is True:
            self.logger.info("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            # check if there are clients connected
            if not server_to_client.clients:
                self.logger.info("No clients connected")
                return
            # ready for filetransfer - LOCK all other fileoperations
            self.factory.rawmode = True

        file_path = self._showFilePicker(SHARE_DIRECTORY)

        if file_path:
            # give a list to waiting thread, to regonize if filetransfer is ok
            clients = []
            if client_id == "all":
                clients = self.get_list_widget_items()
                receiver = "all"
            else:
                c = self.get_list_widget_by_client_id(client_id)
                clients.append(c)
                receiver = c.id

            self._startWorkingIndicator("%s wird an %s gesendet" % (os.path.basename(file_path), receiver))

            # Waiting Thread
            self.progress_thread.setClients(clients)
            if self.progress_thread:
                self.progress_thread.stop()
            self.progress_thread.start()

            self.networkProgress.show(len(clients))

            # here starts the bytestream
            success, filename, file_size, client_id = server_to_client.send_file(file_path, client_id, DataType.FILE.value)

            msg = "Sending File %s to %s" % (os.path.basename(file_path), receiver)
            self.log(msg)

            if success:
                msg = '<b>Sending file:</b> %s (%d Byte) to <b> %s </b>' % (filename, file_size, receiver)
            else:
                msg = '<b>Sending file:</b> Something went wrong sending file %s (%d KB) to <b> %s </b>' % (filename, file_size / 1024, receiver)

            self.log(msg)
            self.logger.info(html_to_text(msg))
        else:
            self.factory.rawmode = False

    def _showFilePicker(self, directory):
        # show filepicker
        self.filedialog.setDirectory(directory)
        self.filedialog.setAcceptMode(QFileDialog.AcceptOpen)
        self.filedialog.setFileMode(QFileDialog.AnyFile)
        # get filename
        file_path = self.filedialog.getOpenFileName()
        file_path = file_path[0]
        return file_path

    def _onScreenshots(self, who):
        msg = "<b>Requesting Screenshot Update </b>"
        self.log(msg)
        self.log(html_to_text(msg), True)
        self._show_workingIndicator(1000, "Screenhot Update")

        if self.factory.rawmode is True:
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            self.factory.rawmode = True  # LOCK all other fileoperations

        if not self.factory.server_to_client.request_screenshots(who):
            self.factory.rawmode = False   # UNLOCK all fileoperations
            self.log("No clients connected")

    def _onShowIP(self):
        self._show_workingIndicator(500, "Zeige deine IP an")
        show_ip()

    def _onAbgabe(self, who):
        """get SHARE folder from client"""
        self.log('Requesting Folder SHARE from <b>%s</b>' % who)
        self._startWorkingIndicator('Abgabe ...')

        clients = []
        if who == "all":
            clients = self.get_list_widget_items()
        else:
            c = self.get_list_widget_by_client_id(who)
            clients.append(c)

        # Waiting Thread
        self.log("Waiting for Client to send Abgabe-Files")
        self.progress_thread.setClients(clients)
        if self.progress_thread:
            self.progress_thread.stop()
        self.progress_thread.start()

        self.networkProgress.show(len(clients))

        if self.factory.rawmode is True:
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            self.factory.rawmode = True  # LOCK all other fileoperations

        if not self.factory.server_to_client.request_abgabe(who):
            self.factory.rawmode = False   # UNLOCK all fileoperations
            self.log("No clients connected")

    def _on_start_exam(self, who):
        """
        ZIP examconfig folder
        send configuration-zip to clients - unzip there
        invoke startexam.sh file on clients

        """
        self._show_workingIndicator(500, "Starte die Prüfung")
        server_to_client = self.factory.server_to_client

        if self.factory.rawmode is True:   # check if server is already in rawmode (ongoing filetransfer)
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            if not server_to_client.clients:        # check if there are clients connected
                self.log("No clients connected")
                return
            self.factory.rawmode = True   # ready for filetransfer - LOCK all other fileoperations

        self._show_workingIndicator(4000)
        self.log('<b>Initializing Exam Mode On All Clients </b>')

        cleanup_abgabe = self.ui.cleanabgabe.checkState()
        # create zip file of all examconfigs
        target_folder = EXAMCONFIG_DIRECTORY
        filename = "EXAMCONFIG"
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
        server_to_client.send_file(file_path, who, DataType.EXAM.value, cleanup_abgabe)

    def _on_exit_exam(self, who):
        """
        Ends the Exammode from a Client, who=all or name
        """
        self.log("<b>Finishing Exam</b>")
        self._show_workingIndicator(2000, "Prüfung wird beendet")
        if self.factory.lcs.running:
            # disable autoscreenshot, lcs = Loopingcall
            self.factory.lcs.stop()

        if self.factory.lc.running:
            icon = self.rootDir.joinpath("pixmaps/chronometer-off.png").as_posix()
            self.ui.autoabgabe.setIcon(QIcon(icon))
            #  disable autoabgabe, lc = Loopingcall
            self.factory.lc.stop()

        # first fetch Abgabe
        if self.factory.rawmode is True:
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            self.factory.rawmode = True  # LOCK all other fileoperations

        if not self.factory.server_to_client.request_abgabe(who):
            self.factory.rawmode = False  # UNLOCK all fileoperations
            self.log("No clients connected")

        # start Thread
        self.log("Waiting for all Clients to send their Abgabe-Files")
        # on Event call
        self.progress_thread.start()
        mutual_functions.showDesktopMessage("Abgabe Ordner ist Persönlicher Ordner/SHARE")

    def _onStartHotspot(self):
        self._show_workingIndicator(500, "Starte Hotspot")
        start_hotspot()

    def get_firewall_adress_list(self):
        return [[self.ui.firewall1, self.ui.port1], [self.ui.firewall2, self.ui.port2], [self.ui.firewall3, self.ui.port3], [self.ui.firewall4, self.ui.port4]]

    def _onTestFirewall(self):
        self._show_workingIndicator(1000, "Teste dir Firewall")
        ipfields = self.get_firewall_adress_list()

        if self.ui.testfirewall.text() == "Stoppe Firewall":    # really don't know why qt sometimes adds these & signs to the ui
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
                    if number != 1:  # zeilenumbruch einfügen ausser vor erster zeile (keine leerzeilen in der datei erlaubt)
                        thisexamfile.write("\n")
                    thisexamfile.write("%s:%s" % (ip, port))
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
        self._show_workingIndicator(500)
        intervall = self.ui.aintervall.value()
        minute_intervall = intervall * 60  # minuten nicht sekunden
        if self.factory.lc.running:
            icon = self.rootDir.joinpath("pixmaps/chronometer-off.png").as_posix()
            self.ui.autoabgabe.setIcon(QIcon(icon))
            self.factory.lc.stop()
            self.log("<b>Auto-Submission deactivated </b>")
            return
        if intervall != 0:
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
        self._show_workingIndicator(500, "Client wird entfernt")
        client_name = self.factory.server_to_client.kick_client(client_id)

        if client_name:
            # SIP C++ Module deletes the Item from ListWidget

            item = self.get_list_widget_by_client_id(client_id)
            if item:
                item = self.get_QListWidgetItem_by_client_id(client_id)
                sip.delete(item)
                # remove client widget no matter if client still is connected or not
                msg = 'Connection to client <b> %s </b> has been <b>removed</b>.' % (client_name)
                self.log(html_to_text(msg))
                # remove from Listwidget the QListWidgetItem
                # UI Label Update count clients
                self.ui.label_clients.setText(self.createClientsLabel())
                # Update Heartbeat List
                self.heartbeat.updateClientHeartbeats()
            else:
                self.logger.error("Can't delete client %s" % client_name)

    def _disableClientScreenshot(self, client):
        self._show_workingIndicator(500, "Client Screenshot ausgeschaltet")
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
            # item not found because first connection attempt
            return

    def log(self, msg, onlyinGUI=False):
        """ creates an log entry inside GUI LOG Textfield """
        timestamp = '[%s]' % datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.logwidget.append(timestamp + " " + str(msg))
        if onlyinGUI is False:
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
            # Update Label
            self.ui.label_clients.setText(self.createClientsLabel())

    def _addNewListItem(self, client, screenshot_file_path):
        itemN = QtWidgets.QListWidgetItem()

        # Create widget
        widget = MyCustomWidget(client, screenshot_file_path)
        widget.setText('%s' % (client.clientName))
        widget.setImage(screenshot_file_path)
        widget.setExamIconOFF()

        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(lambda: self._on_context_menu(client.clientConnectionID, False))
        widget.mouseDoubleClickEvent = lambda event: self._onDoubleClick(client.clientConnectionID, client.clientName, screenshot_file_path)

        # important!
        itemN.setSizeHint(widget.sizeHint())
        # link Object to item
        itemN.setData(QtCore.Qt.UserRole, widget)

        # Add widget to QListWidget
        self.ui.listWidget.addItem(itemN)                # add the listitem to the listwidget
        self.ui.listWidget.setItemWidget(itemN, widget)  # set the widget as the listitem's widget

        # Update Heartbeat List
        self.heartbeat.updateClientHeartbeats()

    def _updateListItemScreenshot(self, existing_item, client, screenshot_file_path):
        try:
            # if client reconnected remove from disconnected_list
            self.factory.disconnected_list.remove(client.clientName)
        except:
            pass            # changed return to pass otherwise the screenshot is not updated

        existing_item.setImage(screenshot_file_path)
        existing_item.setText('%s' % (client.clientName))
        # in case this is a reconnect - update clientConnectionID in order to address the correct connection
        existing_item.setID(client.clientConnectionID)
        existing_item.setDisabled()

        try:
            if self.screenshotwindow.client_connection_id == existing_item.pID:
                self.screenshotwindow.oImage = QImage(screenshot_file_path)
                # resize Image to widgets size
                self.screenshotwindow.sImage = self.screenshotwindow.oImage.scaled(1200, 675, Qt.SmoothTransformation)
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
            item = self.ui.listWidget.item(index)
            # get the linked object back
            mycustomwidget = item.data(QtCore.Qt.UserRole)
            items.append(mycustomwidget)
        return items

    def get_list_widget_by_client_id(self, client_connection_id):
        """ returns the widget from a client """
        for widget in self.get_list_widget_items():
            if client_connection_id == widget.getConnectionID():
                self.log("Found existing list widget for client connectionId %s" % client_connection_id)
                return widget
        return False

    def get_QListWidgetItem_by_client_id(self, client_id):
        """
        returns the QListWidgetItem from a client
        the widget itself is connected to that Item
        """
        for index in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(index)
            # get the linked object back
            mycustomwidget = item.data(QtCore.Qt.UserRole)
            if client_id == mycustomwidget.getID():
                self.log("Found existing list widget for client connectionId %s" % client_id)
                return item
        return False

    def get_list_widget_by_client_name(self, client_name):
        """ returns the widget from a client """
        for widget in self.get_list_widget_items():
            if client_name == widget.getName():
                self.log("Found existing list widget for client name %s" % client_name)
                return widget
        return False

    def get_existing_or_skeleton_list_widget(self, client_name):
        pass

    def newOnkeyPressEvent(self, e):
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
            # Threads Shutdown
            #self.jobs.stop()
            self.heartbeat.stop()

            # if in root mode than change log Files to student User
            self.log("Shuting down >")
            self.log("root?: uid: %s" % os.getuid())
            if os.getuid() == 0:
                # root has uid = 0
                os.system("cd %s && chown %s:%s *.log" % (self.rootDir, USER, USER))

            mutual_functions.deletePidFile()
            self.ui.close()
            os._exit(0)  # otherwise only the gui is closed and connections are kept alive
        else:
            self.msg = False

    def removeZombie(self):
        """
        removes a zombie client
        fired from Heartbeat.py
        """
        print("Client is dead")
