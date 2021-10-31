#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime
import os
import shutil
from time import sleep
from pathlib import Path
import sip  #noqa

from config.config import PRINTERCONFIG_DIRECTORY,\
    SERVERZIP_DIRECTORY, SHARE_DIRECTORY, USER, EXAMCONFIG_DIRECTORY,\
    SCRIPTS_DIRECTORY, DEBUG_PIN, GEOGEBRA_PATH, WEB_ROOT,\
    DELIVERY_DIRECTORY, USER_HOME_DIR, MAX_SILENT_TIME_OFf_CLIENT
from config.enums import DataType
from server.resources.Applist import findApps
from classes.system_commander import dialog_popup, show_ip, start_hotspot,\
    get_primary_ip
from version import __version__
from enum import Enum

from PyQt5 import uic, QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QRegExp
from PyQt5.Qt import QRegExpValidator, QFileDialog, QTimer
from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap, QCursor

from server.resources.MyCustomWidget import MyCustomWidget
from server.resources.ScreenshotWindow import ScreenshotWindow
from server.ui.NetworkProgressBar import NetworkProgressBar
from server.ui.threads.Thread_Progress_Events import client_abgabe_done,\
    client_abgabe_done_exit_exam, client_received_file_done, client_lock_screen,\
    client_unlock_screen
from server.ui.threads.Thread_Progress import Thread_Progress
from classes.ConfigTools import ConfigTools
from classes import mutual_functions
from classes.HTMLTextExtractor import html_to_text
from classes.mutual_functions import get_file_list, checkIP
from classes.PlasmaRCTool import PlasmaRCTool
from classes.Hasher import Hasher


class MsgType(Enum):
    AllwaysDebug = 1


class ServerUI(QtWidgets.QDialog):
    backupTitel = ""
    backupBackgroundColor = "#000000"
    examBackgroundColor = "#fab1a0"

    defaultTitel = "Exam Server"
    defaultBgColor = "#eff0f1"

    debugTitel = ".: DEBUG MODE :. - Exam Server - .: DEBUG MODE :."
    debugBgColor = "#ffffbf"

    def __init__(self, factory, splash, app):
        """
        :param factory: Server Factory
        :param splash: the Splashscreen started in Main Application
        :param app: the main QApplication
        """
        QtWidgets.QDialog.__init__(self)
        # rootDir of Application
        self.rootDir = Path(__file__).parent.parent.parent

        self.logger = logging.getLogger(__name__)
        uic.uiparser.logger.setLevel(logging.INFO)
        uic.properties.logger.setLevel(logging.INFO)

        path_to_yml = self.rootDir.joinpath('config/config_ui.yaml')
        self.configUI = ConfigTools(path_to_yml)

        self.application = app
        self.splashscreen = splash

        # loadUI, findApps, timeout
        self.splashscreen.setProgressMax(3)
        self.splashscreen.setMessage("Loading UI")

        self.factory = factory     # MyServerFactory

        uifile = self.rootDir.joinpath('server/server.ui')
        self.ui = uic.loadUi(uifile)        # load UI

        self.splashscreen.step()
        self.application.processEvents()

        iconfile = self.rootDir.joinpath('pixmaps/windowicon.png').as_posix()
        self.ui.setWindowIcon(QIcon(iconfile))  # definiere icon für taskleiste

        # only debug if DEBUG_PIN is not ""
        debug_css = ""
        if DEBUG_PIN != "":
            self.ui.setWindowTitle(self.debugTitel)
            debug_css = "QDialog{ background: %s; }" % self.debugBgColor
            self.backupTitel = self.debugTitel
            self.backupBackgroundColor = self.debugBgColor
        else:
            self.ui.setWindowTitle(self.defaultTitel)
            self.backupTitel = self.defaultTitel
            self.backupBackgroundColor = self.defaultBgColor

        self.ui.exit.clicked.connect(self._onAbbrechen)  # setup3 Slots
        self.ui.sendfile.clicked.connect(lambda: self._onSendFile("all"))  # button x   (lambda is not needed - only if you wanna pass a variable to the function)
        self.ui.showip.clicked.connect(self._onShowIP)  # button y
        self.ui.abgabe.clicked.connect(lambda: self.onAbgabe("all", False))
        self.ui.screenshots.clicked.connect(lambda: self.onScreenshots("all"))
        self.ui.startexam.clicked.connect(lambda: self._on_start_exam("all"))
        self.ui.openshare.clicked.connect(self._onOpenshare)
        self.ui.starthotspot.clicked.connect(self._onStartHotspot)
        self.ui.testfirewall.clicked.connect(self._onTestFirewall)

        self.ui.autoabgabe.clicked.connect(self._onAutoabgabe)
        # is Auto Abgabe triggered
        self.autoAbgabe = False

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
        self.ui.version.setText("<b>Version</b> %s" % __version__)
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
        ip_regex = QRegExp(r"[0-9\._]+")
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

        # debug turn it off here
        # self.splashscreen.finish(self)

        findApps(self.ui.applist, self.ui.appview, self.application)
        self.splashscreen.step()

        # Waiting Thread
        self.progress_thread = Thread_Progress(self)
        # connect Events
        self.progress_thread.client_finished.connect(client_abgabe_done)
        self.progress_thread.client_exitExam.connect(client_abgabe_done_exit_exam)
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
            sleep(3)
        self.splashscreen.setMessage("Done")
        self.splashscreen.finish(self)
        self.ui.keyPressEvent = self.newOnkeyPressEvent

        self.ui.show()

        self.screenshotwindow = ScreenshotWindow(self)

        # Set UI Values from config_ui.yml file
        self.configUI.setConfig(self.ui)

        # search for GGB Web Apps
        self.testGGB()

        # TEST
        if len(DEBUG_PIN) > 0:
            self.ui.testbtn.clicked.connect(self._test)
        else:
            self.ui.testbtn.hide()

        # TEST
        # file_path = self._showFilePicker(SHARE_DIRECTORY)
        # mutual_functions.openFileManager("/home/student")

    def _test(self):
        print("TEST ---------------------------")
        for widget in self.get_list_widget_items():
            widget.setFileReceivedOK()

        # Color the UI for visual Feedback
        self.ui.setWindowTitle("%s - EXAM MODE" % self.defaultTitel)
        self.ui.setStyleSheet("QDialog{ background: %s; }" % self.examBackgroundColor)
        self.update()

    def createClientsLabel(self):
        """ Erzeugt den Text für Clients: <Anzahl> """
        return ("Clients: <b>%s</b>" % self.ui.listWidget.count())

    def _changeAutoscreenshot(self):
        self._show_workingIndicator(200, "Screenshot Intervall gesetzt")
        intervall = self.ui.ssintervall.value()

        if hasattr(self.factory, 'lcs'):
            if self.factory.lcs.running:
                self.factory.lcs.stop()
            if intervall != 0:
                self.log("<b>Changed Screenshot Intervall to %s seconds </b>" % (str(intervall)))
                self.factory.lcs.start(intervall)
            else:
                self.log("<b>Screenshot Intervall is set to 0 - Screenshotupdate deactivated</b>")

    def _onSendPrintconf(self, who):
        """send the printer configuration to all clients"""

        if self.clientsConnected() is False:
            return

        self._show_workingIndicator(500, "Drucker Konfiguration senden")
        server_to_client = self.factory.server_to_client

        if self.factory.rawmode is True:   # check if server is already in rawmode (ongoing filetransfer)
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            if not server_to_client.clients:       # check if there are clients connected
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

    def clientsConnected(self):
        """ check if clients connected """
        clients = self.get_list_widget_items()
        if len(clients) == 0:
            return False
        return True

    def _onScreenlock(self, who):
        """locks or unlock the client screens"""
        if self.clientsConnected() is False:
            return

        clients = self.get_list_widget_items()
        # self._startWorkingIndicator("Locking Client Screens ... ")
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

    def _onOpenshare(self):
        dir_path = os.path.join(SHARE_DIRECTORY, DELIVERY_DIRECTORY)
        # be sure directory exists
        os.system("mkdir -p %s" % dir_path)
        mutual_functions.openFileManager(dir_path)

    def _updateExamName(self):
        self.factory.examid = self.ui.examlabeledit1.text()
        if self.ui.examlabeledit1.text() == "":
            self.factory.examid = self.factory.createExamId()

        self.ui.currentlabel.setText("<b>%s</b>" % self.factory.examid)

    def _startWorkingIndicator(self, info=""):
        """ display and start the indicator, no timeout """
        if self.timer and self.timer.isActive:  # running indicator
            self.timer.stop()

        self.workinganimation.stop()
        self.ui.info_label.setText("%s ..." % info)
        sleep(0.1)
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
                c = self.get_list_widget_by_client_ConID(client_id)
                clients.append(c)
                receiver = c.id

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

    def onScreenshots(self, who):
        msg = "<b>Requesting Screenshot Update </b>"
        self.log(msg)

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

    def onAbgabe(self, who, auto):
        """
        get SHARE folder from client
        :who: client or all
        :auto: True/False is this a AutoAbgabe Event?
        """
        if self.clientsConnected() is False:
            return

        # manual triggered?
        self.autoAbgabe = auto

        self.log('Requesting Folder SHARE from <b>%s</b>' % who)

        clients = []
        if who == "all":
            clients = self.get_list_widget_items()
        else:
            c = self.get_list_widget_by_client_ConID(who)
            clients.append(c)

        # Waiting Thread
        self.log("Waiting for Client to send Abgabe-Files")

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

        # check if server is already in rawmode (ongoing filetransfer)
        if self.factory.rawmode is True:
            self.log("Waiting for ongoing file-transfers to finish ...")
            return
        else:
            # check if there are clients connected
            if not server_to_client.clients:
                self.log("No clients connected")
                return
            self.factory.rawmode = True   # ready for filetransfer - LOCK all other fileoperations

        self._show_workingIndicator(4000)
        self.log('<b>Initializing Exam Mode On All Clients </b>')

        self.prepareDesktopStarter()

        # Checkbox
        _cleanup_abgabe = self.ui.cleanabgabe.checkState()
        _spellcheck = self.ui.spellcheck.checkState()
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
        server_to_client.send_file(
            file_path, who, DataType.EXAM.value,
            cleanup_abgabe=_cleanup_abgabe, spellcheck=_spellcheck)

        if who == 'all':
            if DEBUG_PIN != "":
                self.logger.info("Starting Exam on ALL Clients: %s")
            client_widgets = self.get_list_widget_items()
            for client_widget in client_widgets:
                # set the status Icon
                # client_widget = self.get_list_widget_by_client_name(who)
                client_widget.setExamIconON()
        else:
            # single Widget
            if DEBUG_PIN != "":
                self.logger.info("Starting Exam on Client: %s" % who)
            client_widget = self.get_list_widget_by_client_ConID(who)
            client_widget.setExamIconON()

        # Color the UI for visual Feedback
        self.ui.setWindowTitle("%s - EXAM MODE" % self.defaultTitel)
        self.ui.setStyleSheet("QDialog{ background: %s; }" % self.examBackgroundColor)

    def _on_exit_exam(self, who):
        """
        Ends the Exammode from a Client, who=all or name
        """
        self.log("<b>Finishing Exam</b>")
        self._show_workingIndicator(2000, "Prüfung wird beendet")
        # if self.factory.lcs.running:
        # disable autoscreenshot, lcs = Loopingcall
        # self.factory.lcs.stop()

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

        dir_path = os.path.join(SHARE_DIRECTORY, DELIVERY_DIRECTORY)
        # subtract
        dir_path = dir_path[len(USER_HOME_DIR):]
        mutual_functions.showDesktopMessage("Abgabe Ordner ist Persönlicher Ordner%s" % dir_path)

        if self.progress_thread:
            self.progress_thread.fireEvent_exitExam(who, "0")

        # Color the UI for visual Feedback back to normal
        self.ui.setWindowTitle(self.backupTitel)
        self.ui.setStyleSheet("QDialog{ background: %s; }" % self.backupBackgroundColor)

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

    def stopAutoAbgabe(self):
        """stop Auto Abgabe"""
        if self.factory.lc.running:
            self.factory.lc.stop()

    def startAutoAbgabe(self):
        """start Auto Abgabe"""
        intervall = self.ui.aintervall.value()
        if intervall != 0:
            minute_intervall = intervall * 60
            self.factory.lc.start(minute_intervall)

    def _onAutoabgabe(self):
        # self._show_workingIndicator(500)
        if self.factory.lc.running:
            icon = self.rootDir.joinpath("pixmaps/chronometer-off.png").as_posix()
            self.ui.autoabgabe.setIcon(QIcon(icon))
            self.log("<b>Auto-Submission deactivated </b>")
            self.stopAutoAbgabe()
            return

        intervall = self.ui.aintervall.value()
        if intervall != 0:
            icon = self.rootDir.joinpath("pixmaps/chronometer.png").as_posix()
            self.ui.autoabgabe.setIcon(QIcon(icon))
            self.log("<b>Activated Auto-Submission every %s minutes </b>" % (str(intervall)))
            self.startAutoAbgabe()
        else:
            self.log("Auto-Submission Intervall is set to 0 - Auto-Submission not active")

    def _removeClientWidget(self, con_id):
        """ remove from Widget Clients """
        item = self.get_list_widget_by_client_ConID(con_id)
        if item:
            Qitem = self.get_QListWidgetItem_by_client_id(con_id)
            sip.delete(Qitem)  # noqa
            # remove client widget no matter if client still is connected or not
            msg = 'Connection to client <b> %s </b> has been <b>removed</b>.' % (item.getName())
            self.log(html_to_text(msg))
            # remove from Listwidget the QListWidgetItem
            # UI Label Update count clients
            self.ui.label_clients.setText(self.createClientsLabel())

    def _onRemoveClient(self, con_id):
        """ Entfernt einen Client aus dem Widget """
        self._show_workingIndicator(500, "Client wird entfernt")
        # send I kick you to client
        self.factory.server_to_client.kick_client(con_id)
        item = self.get_list_widget_by_client_ConID(con_id)
        client_name = item.getName()

        if client_name:
            # SIP C++ Module deletes the Item from ListWidget
            self._removeClientWidget(con_id)
        else:
            self.logger.error("Can't delete client %s" % client_name)

    def disableClientScreenshot(self, client):
        self._show_workingIndicator(500, "Client Screenshot ausgeschaltet")
        client_name = client.clientName
        client_id = client.clientConnectionID
        item = self.get_list_widget_by_client_ConID(client_id)
        icon = self.rootDir.joinpath("pixmaps/nouserscreenshot.png").as_posix()
        pixmap = QPixmap(icon)
        try:
            item.picture.setPixmap(pixmap)
            item.info.setText('%s \ndisconnected' % client_name)
            item.disabled = True
        except Exception:
            # item not found because first connection attempt
            return

    def DebugLog(self, msg, show_allways=-1):
        """ Debug Logging """
        if show_allways == MsgType.AllwaysDebug:
            self.logger.info(html_to_text(msg))
        elif DEBUG_PIN != "":
            self.logger.info(html_to_text(msg))

    def log(self, msg, show_allways=-1):
        """ creates an log entry inside GUI LOG Textfield """
        timestamp = '[%s]' % datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.logwidget.append(timestamp + " " + str(msg))
        # ...
        self.DebugLog(msg, show_allways)

    def createOrUpdateListItem(self, client, screenshot_file_path):
        """ generates new List Item that displays the client screenshot """
        hasher = Hasher()
        uniqueID = hasher.getUniqueConnectionID(client.clientName, client.clientConnectionID)

        existing_item = self.get_list_widget_by_client_ConID(uniqueID)

        if existing_item:  # just update screenshot
            self._updateListItemScreenshot(existing_item, client, screenshot_file_path)
        else:
            new_client_name = self._checkDoubleClientName(client)
            # change name or leave it the same
            client.clientName = new_client_name
            print("createOrUpdateListItem %s" % new_client_name)
            self._addNewListItem(client, screenshot_file_path)
            # Update Label
            self.ui.label_clients.setText(self.createClientsLabel())

    def _checkDoubleClientName(self, client):
        """
        check for if Client name exists > rename it
        Connection is unique with connectionID!
        """
        newName = client.clientName
        index = 1
        widget = self._testName(client.clientName)
        if widget:
            found = True
            # search as long Name is Unique
            while found:
                newName = "%s[%s]" % (client.clientName, index)
                found = self._testName(newName)
                index += 1
        return newName

    def _testName(self, name):
        """just a helper"""
        for widget in self.get_list_widget_items():
            if name == widget.getName():
                return widget
        return False

    def _addNewListItem(self, client, screenshot_file_path):
        itemN = QtWidgets.QListWidgetItem()

        # Create widget
        widget = MyCustomWidget(client, screenshot_file_path)
        widget.setText('%s' % (client.clientName))
        widget.setImage(screenshot_file_path)
        widget.setExamIconOFF()

        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(lambda: self._on_context_menu(client.clientName, False))
        widget.mouseDoubleClickEvent = lambda event: self._onDoubleClick(client.clientConnectionID, client.clientName, screenshot_file_path)  # noqa

        # important!
        itemN.setSizeHint(widget.sizeHint())
        # link Object to item
        itemN.setData(QtCore.Qt.UserRole, widget)

        # Add widget to QListWidget
        self.ui.listWidget.addItem(itemN)                # add the listitem to the listwidget
        self.ui.listWidget.setItemWidget(itemN, widget)  # set the widget as the listitem's widget

    def _updateListItemScreenshot(self, existing_item, client, screenshot_file_path):
        existing_item.setImage(screenshot_file_path)
        existing_item.setText('%s' % (client.clientName))

        hasher = Hasher()
        uniqueID = hasher.getUniqueConnectionID(client.clientName, client.clientConnectionID)
        existing_item.setID(uniqueID)

    def _onDoubleClick(self, client_connection_id, client_name, screenshot_file_path):  # noqa
        print(screenshot_file_path)

        self.screenshotwindow.setClientConnectionID(client_name)
        self.screenshotwindow.setClientname(client_name)
        self.screenshotwindow.setScreenshotFilePath(screenshot_file_path)
        self.screenshotwindow.updateUI()
        self.screenshotwindow.exec_()

    def _on_context_menu(self, client_connection_id, is_disabled):
        menu = QtWidgets.QMenu()

        action_1 = QtWidgets.QAction("Abgabe holen", menu, triggered=lambda: self.onAbgabe(client_connection_id, False))
        action_2 = QtWidgets.QAction("Screenshot updaten", menu, triggered=lambda: self.onScreenshots(client_connection_id))
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

    def get_list_widget_by_client_ConID(self, client_connection_id):
        """ returns the widget from a client """
        for widget in self.get_list_widget_items():
            if client_connection_id == widget.getConnectionID():
                return widget
        # there are items in list
        if len(self.get_list_widget_items()) > 0:
            self.log("Error: No list widget for connectionID %s" % client_connection_id)
            if DEBUG_PIN != "":
                self.logger.debug("Widgets in List")
                for widget in self.get_list_widget_items():
                    self.logger.debug(widget.getConnectionID())
        return False

    def get_list_widget_by_client_IP(self, client_IP):
        """ returns the widget from a client """
        for widget in self.get_list_widget_items():
            if client_IP == widget.getIP():
                return widget
        # there are items in list
        if len(self.get_list_widget_items()) > 0:
            self.log("Error: No list widget for IP %s" % client_IP)
            if DEBUG_PIN != "":
                self.logger.debug("Widgets in List")
                for widget in self.get_list_widget_items():
                    self.logger.debug(widget.getConnectionID())
        return False

    def get_QListWidgetItem_by_client_id(self, con_id):
        """
        returns the QListWidgetItem from a client
        the widget itself is connected to that Item
        """
        for index in range(self.ui.listWidget.count()):
            item = self.ui.listWidget.item(index)
            # get the linked object back
            mycustomwidget = item.data(QtCore.Qt.UserRole)
            # print("%s <> %s" % (con_id, mycustomwidget.getConnectionID()))
            if con_id == mycustomwidget.getConnectionID():
                return item
        # there are items in list
        if self.ui.listWidget.count() > 0:
            self.log("Error: list widget NOT found for client connectionId %s" % con_id)
        return False

    def get_list_widget_by_client_name(self, client_name):
        """ returns the widget from a client """
        for widget in self.get_list_widget_items():
            if client_name == widget.getName():
                return widget
        # there are items in list
        if self.ui.listWidget.count() > 0:
            self.log("Error: list widget NOT found for client name %s" % client_name)
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

    def stopWidgetIconTimer(self):
        """ every Client Widget has a running Timer > stop them all """
        for widget in self.get_list_widget_items():
            widget.close()

    def _onAbbrechen(self):  # Exit button
        self.msg = QtWidgets.QMessageBox()
        self.msg.setIcon(QtWidgets.QMessageBox.Information)
        self.msg.setText("Wollen sie das Programm\nLIFE Exam Server \nbeenden?")

        self.msg.setWindowTitle("LiFE Exam")
        self.msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        retval = self.msg.exec_()   # 16384 = yes, 65536 = no

        if str(retval) == "16384":
            # Threads Shutdown
            # self.jobs.stop()
            self.stopWidgetIconTimer()

            # if in root mode than change log Files to student User
            self.log("Shuting down > root?: uid: %s" % os.getuid())
            if os.getuid() == 0:
                # root has uid = 0
                os.system("cd %s && chown %s:%s *.log" % (self.rootDir, USER, USER))

            # save the UI Config
            self.configUI.saveConfig(self.ui)

            mutual_functions.deletePidFile()
            self.ui.close()
            # otherwise only the gui is closed and connections are kept alive
            os._exit(0)  # noqa
        else:
            self.msg = False

    @QtCore.pyqtSlot(list)
    def silentClientsUpdate(self, silent_clients):
        """
        fired from HeartbeatServer.py when a time limit is reached
        :param silent_clients: list of IP's which clients are silent
        """
        # these are the silent client
        for client in silent_clients:
            how_long_offline = client[1]
            client = self.get_list_widget_by_client_IP(client[0])
            if client:
                client.setOffline()
                if DEBUG_PIN != "":
                    self.logger.info("Client \"%s\" is silent ...." % client.getName())

                if how_long_offline > MAX_SILENT_TIME_OFf_CLIENT:
                    # too long silent, remove it
                    self._removeClientWidget(client.getConnectionID())

    @QtCore.pyqtSlot(list)
    def checkOnlineClients(self, silent_clients):
        """ are there clients that must remove the Offline Banner? """
        online_clients = []
        for widget in self.get_list_widget_items():
            found = False
            for client in silent_clients:
                # compare IP's
                if widget.getIP() in client[0]:
                    found = True
                    break
            if found is False:
                online_clients.append(widget)

        # set Online
        for widget in online_clients:
            widget.setOnline()
        # print("Silent: %s" % silent_clients)

    def _setInfoColor(self, col):
        """sets the TextLabel Color in Info Area"""
        self.ui.info_label.setStyleSheet("QLabel { color : %s; }" % col)

    def _resetInfoColor(self):
        """resets the TextLabel Color in Info Area to black"""
        self.ui.info_label.setStyleSheet("QLabel { color : black; }")

    def testGGB(self):
        """
        search fpr Geogebra WebApp in /var/www/html/geogebra
        fire a reminder if not existent
        """
        if os.path.join(WEB_ROOT, GEOGEBRA_PATH) is False:
            self._setInfoColor("#ff0000")

            self.ui.info_label.setText("Geogebra Web App missing in %s !" % GEOGEBRA_PATH)
            self.ui.working.show()

            QTimer.singleShot(5000, self._hideGGBError)

    def _hideGGBError(self):
        """ hide GGB missing msg """
        self.ui.info_label.setText("")
        self.ui.working.hide()

    def prepareDesktopStarter(self):
        """
        prepare Desktop Starter for Exam Mode
        Server prepares the plasma-org.kde.plasma.desktop-appletsrc
        examclient_plugin copys the Desktop Starter
        """
        plasmaTool = PlasmaRCTool()
        plasmaTool.addStarter()
