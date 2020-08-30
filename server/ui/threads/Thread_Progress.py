#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import time
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog
from server.resources.MyCustomWidget import MyCustomWidget


class Thread_Progress(QtCore.QThread):
    """ a Thread that controlls the progressbar, if clients are contacted """
    client_finished = pyqtSignal(QDialog, str)
    client_received_file = pyqtSignal(QDialog, MyCustomWidget)
    client_lock_screen = pyqtSignal(QDialog, MyCustomWidget)
    client_unlock_screen = pyqtSignal(QDialog, MyCustomWidget)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.parent = parent
        self.running = False
        self.clients = []

    def __del__(self):
        self.wait()

    def fireEvent_Lock_Screen(self, who):
        """ client has locked the screen """
        print("Clients: %s -1" % (len(self.clients)))
        if len(self.clients) > 0:
            self.client_lock_screen.emit(self.parent, who)

    def fireEvent_UnLock_Screen(self, who):
        """ client has unlocked the screen """
        if len(self.clients) > 0:
            self.client_unlock_screen.emit(self.parent, who)

    def fireEvent_Abgabe_finished(self, who):
        """ client has sended his Files """
        self.client_finished.emit(self.parent, who)

    def fireEvent_File_received(self, clientWidget):
        """ client has received a file """
        # delete client from list
        if len(self.clients) > 0:
            self.deleteItemFromList(clientWidget.getName())
            self.client_received_file.emit(self.parent, clientWidget)

    def deleteItemFromList(self, who):
        """ delete an Item from the client list """
        index = -1
        for x in range(len(self.clients)):
            if self.clients[x].id == who:
                index = x
                break
        # remove Element
        # time critical only if you find an index
        if index != -1:
            self.clients = self.clients[:index] + self.clients[index + 1:]

    def isAlive(self):
        if self.running:
            return True
        else:
            return False

    def stop(self):
        self.running = False
        self.quit()

    def setClients(self, clients):
        """ a list within all clients to actually work with """
        self.clients = []
        self.clients = clients  # evtl. noch die art des progresses mitnehmen

    def run(self):
        """
        this thread waits for all Clients to sent their OK for different
        operations, an event() will be fired
        """
        self.running = True
        while(self.running):
            time.sleep(0.01)

        return 0

    def restart(self, clients):
        """ clears all clients and restarts the Thread """
        self.setClients(clients)
