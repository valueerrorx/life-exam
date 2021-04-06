#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann
import time
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from server.ui.threads.PeriodicTimer import PeriodicTimer
from config.config import HEARTBEAT_INTERVALL, HEARTBEAT_START_AFTER,\
    MAX_HEARTBEAT_FAILS, DEBUG_PIN
from server.ui.threads.Beat import Beat


class Heartbeat(QtCore.QThread):
    """a Thread that checks if a Client is still alive"""
    kick_zombie = pyqtSignal(str, str)
    request_heartbeat = pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        self.setObjectName("Heartbeat")
        self.running = False
        self._clients = parent.ui.listWidget
        # eigene Liste für die clients mit heartbeat Versuchen
        self._heartbeats = []

        # start after x sec than every x sec
        self.timer = PeriodicTimer(self, HEARTBEAT_START_AFTER, HEARTBEAT_INTERVALL, self.checkClients)

    def start(self, *args, **kwargs):
        erg = QtCore.QThread.start(self, *args, **kwargs)
        # start the Timer the first time
        self.timer.first_start()
        return erg

    def __del__(self):
        self.wait()

    def suspend(self):
        """ deactivate the Tick Timer """
        self.timer.stop()

    def resume(self):
        """ resume the Tick Timer """
        self.timer.first_start()

    def get_list_widget_items(self):
        """
        Creates an iterable list of all widget elements aka student screenshots
        :return: list of widget items
        """
        items = []
        for index in range(self._clients.count()):
            item = self._clients.item(index)
            # get the linked object back
            mycustomwidget = item.data(QtCore.Qt.UserRole)
            items.append(mycustomwidget)
            # print("HB cID: %s" % mycustomwidget.getConnectionID())
        return items

    def _cleanUpHeartBeats(self):
        """verwaiste HB entfernen"""
        for i in range(len(self._heartbeats)):
            hb = self._heartbeats[i]
            found = False
            for widget in self.get_list_widget_items():
                if hb.getConnectionID() == widget.getConnectionID():
                    found = True
                    break
            if found is False:
                # HB löschen
                del self._heartbeats[i]

    def updateClientHeartbeats(self):
        """ compares Client List with here stored Beats Client List """
        self._cleanUpHeartBeats()
        # neue Elemente suchen
        for widget in self.get_list_widget_items():
            wid = widget.getConnectionID()  
            found = False
            for i in range(len(self._heartbeats)):
                if self._heartbeats[i] == wid:
                    found = True
                    break
            if found is False:
                # client hat hier keinen Heartbeat Eintrag > anlegen
                self._heartbeats.append(Beat(wid))

    def checkClients(self):
        """ check HB of the clients """
        for hb in self._heartbeats:
            # inc counter, counter is set to 0 when client answers
            hb.incCounter()
            
            # send Request
            print("HB: %s %s" % (hb.getRetries(), hb.getConnectionID()))
            
            if hb.getRetries() >= MAX_HEARTBEAT_FAILS:
                self.kickZombie(hb)
            else:
                # is there all ready a Request for Heartbeat?
                if hb.isPending() is False:
                    hb.setPending(True)
                    self.request_heartbeat.emit(hb.getConnectionID())

    def isAlive(self):
        return self.running

    def stop(self):
        """ stop this Thread """
        self.running = False
        self.timer.stop()
        self.parent.log("Heartbeat Thread stopped ...")

    def run(self):
        """
        this thread waits for all Clients to sent their OK for different
        operations, an event() will be fired
        """
        self.running = True
        # make a panic Thread Shutdown

        while(self.running):
            time.sleep(0.01)

    def fireEvent_Heartbeat(self, who):
        """
        client has sended a heartbeat
        :param who: MyCustomWidget Object
        """
        for hb in self._heartbeats:
            print("HB received from %s" % who.getConnectionID())
            if hb.getConnectionID() == who.getConnectionID():
                hb.resetCounter()

    def kickZombie(self, hb):
        """HB Limit reached, kick clients"""
        count = "%s" % hb.getRetries()
        self.kick_zombie.emit(hb.getConnectionID(), count)

    def DebugPrint(self):
        for i in range(len(self._heartbeats)):
            hb = self._heartbeats[i]
            print("cID: %s, Tries: %s" % (hb.getConnectionID(), hb.getRetries()))
