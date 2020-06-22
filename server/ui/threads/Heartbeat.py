#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann
import time
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from server.ui.threads.PeriodicTimer import PeriodicTimer
from config.config import HEARTBEAT_INTERVALL, HEARTBEAT_START_AFTER
from server.ui.threads.Beat import Beat


class Heartbeat(QtCore.QThread):
    """a Thread that checks if a Client is still alive"""
    client_is_dead = pyqtSignal()
    request_heartbeat = pyqtSignal(str)
    retry_heartbeat = pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        self.setObjectName("Heartbeat")
        self.running = False
        self.running = False
        self._clients = parent.ui.listWidget
        # eigene Liste für die clients mit heartbeat Versuchen
        self._heartbeats = []

        # start after xs than every xs
        self.timer = PeriodicTimer(self, HEARTBEAT_START_AFTER, HEARTBEAT_INTERVALL, self.checkClients)

        # This Timer is used, if a client didn't response even more > check n times before deleting the client
        # start after 10sec than every 2min
        self.hbRetryTimer = PeriodicTimer(self, 20, 60 * 2, self.checkHBAgain)

    def start(self, *args, **kwargs):
        erg = QtCore.QThread.start(self, *args, **kwargs)
        # start the Timer the first time
        self.timer.first_start()
        # start the Timer the first time
        self.hbRetryTimer.first_start()
        return erg

    def __del__(self):
        self.wait()

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
        return items

    def _cleanUpHeartBeats(self):
        """verwaiste HB entfernen"""
        for i in range(len(self._heartbeats)):
            hb = self._heartbeats[i]
            found = False
            for widget in self.get_list_widget_items():
                if hb.getID() == widget.getID():
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
            wid = widget.getConnectionID()  # remark ID = Name!!
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
        server_to_client = self.parent.factory.server_to_client
        for i in range(len(self._heartbeats)):
                hb = self._heartbeats[i]
                print("HB: %s" % hb.getID())
                #server_to_client.request_heartbeat()
                
                self.request_heartbeat.emit(hb.getID())

    def checkHBAgain(self):
        """ re-test HB of not responding Clients """
        print("Re Check HB")
        server_to_client = self.parent.factory.server_to_client
        for i in range(len(self._heartbeats)):
            hb = self._heartbeats[i]
            if hb.isResponding() is False:
                server_to_client.request_heartbeat(hb.getID())

    def isAlive(self):
        if self.running:
            return True
        else:
            return False

    def stop(self):
        self.running = False
        self.timer.stop()
        self.hbRetryTimer.stop()
        self.parent.log("Heartbeat Thread stopped ...")

    def run(self):
        """
        this thread waits for all Clients to sent their OK for different
        operations, an event() will be fired
        """
        self.running = True
        while(self.running):
            time.sleep(0.01)

    def fireEvent_Heartbeat(self, who):
        """ client has sended a heartbeat """
        for i in range(len(self._heartbeats)):
            hb = self._heartbeats[i]
            item = self.parent.get_list_widget_by_client_name(who)
            if hb.getID() == item.getID():
                hb.setResponding()
                break

