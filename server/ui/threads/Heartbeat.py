#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann
import time
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from server.ui.threads.PeriodicTimer import PeriodicTimer
from config.config import HEARTBEAT_INTERVALL, HEARTBEAT_START_AFTER


class Heartbeat(QtCore.QThread):
    """a Thread that checks if a Client is still alive"""
    client_is_dead = pyqtSignal()

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        self.setObjectName("Heartbeat")
        self.running = False
        self.running = False
        self._clients = parent.ui.listWidget
        # eigene Liste für die clients mit heartbeatversuchen
        self._heartbeats = []
        
        # start after xs than every xs
        self.timer = PeriodicTimer(HEARTBEAT_START_AFTER, HEARTBEAT_INTERVALL, self.checkClients)
        # start the Timer the first time
        self.timer.first_start()

    def __del__(self):
        self.wait()

    def updateClientHeartbeats(self, ID, func):
        """ compares Client List with here stored Beats Client List """
        for i in range(len(self._clients)):
            beat = self._clients[i]
            print(beat)

    def delClient(self, ID):
        """ removes a Job from the list """
        for i in range(len(self._jobs)):
            job = self._jobs[i]
            if job.getID() == ID:
                del self.jobs[i]
                break

    def checkClients(self):
        """ check all outstanding jobs or retry them """
        print("Clients: %s" % self._clients.count())
        server_to_client = self.parent.factory.server_to_client
        # server_to_client.request_heartbeat(file_path, who, DataType.EXAM.value, cleanup_abgabe)

    def isAlive(self):
        if self.running:
            return True
        else:
            return False

    def stop(self):
        self.running = False
        self.timer.stop()
        self.parent.log("Heartbeat Thread stopped ...")

    def run(self):
        """
        this thread waits for all Clients to sent their OK for different
        operations, an event() will be fired
        """
        self.running = True
        while(self.running):
            time.sleep(0.01)
