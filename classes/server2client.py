#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.
import datetime
import ntpath
import os

import classes.mutual_functions as mutual_functions
from config.enums import Command, DataType
from config.config import DEBUG_PIN
from classes.Hasher import Hasher


class ServerToClient:
    def __init__(self):
        self.clients = dict()           # type: dict
        # we will store the time of the last (try) to connect with.. check it against the screenshot
        # intervall (our heartbeat) and disconnect client if the timespan is twice the heartbeat intervall
        self.clientlifesigns = dict()   # type: dict

    """client handling"""
    def get_client(self, key):
        client = self.clients.get(key, None)  # type: MyServerProtocol
        return client

    def add_client(self, client, uniqueID):
        """
        Client has made a connection
        :param uniqueID: is a created unique ID
        """
        self.clients.update({uniqueID: client})
        if DEBUG_PIN != "":
            print("**** Added ClientConnectionID %s" % uniqueID)

    def remove_client(self, client):
        del self.clients[client.clientConnectionID]

    def kick_client(self, client_id):
        client = self.get_client(client_id)
        if client:
            client.refused = True
            client.sendEncodedLine("%s" % Command.REMOVED.value)
            client.transport.loseConnection()
            return client.clientName
        return False

    def send_to_receivers(self, who, line):
        """ sends to all clients, or just to the selected """
        if who == "all":
            for clientid in self.clients:
                client = self.get_client(clientid)
                client.sendEncodedLine(line % clientid)
        else:
            client = self.get_client(who)
            try:
                hasher = Hasher()
                uniqueID = hasher.getUniqueConnectionID(client.clientName, client.clientConnectionID)
                client.sendEncodedLine(line % uniqueID)
            except Exception:
                print("server2client Error, clientID: %s, %s" % (client.clientConnectionID, line))

    """client instructions"""
    def exit_exam(self, who, onexit_cleanup_abgabe, spellcheck):
        if not self.clients:
            return False
        line = "%s %s %s %s" % (Command.EXITEXAM.value, onexit_cleanup_abgabe, spellcheck, "%s")
        self.send_to_receivers(who, line)
        return True

    def lock_screens(self, who):
        if not self.clients:
            return False
        line = "%s %s" % (Command.LOCK.value, "%s")
        self.send_to_receivers(who, line)
        return True

    def unlock_screens(self, who):
        if not self.clients:
            return False
        line = "%s %s" % (Command.UNLOCK.value, "%s")
        self.send_to_receivers(who, line)
        return True

    def request_heartbeat(self, who):
        if not self.clients:
            return False
        line = "%s %s" % (Command.HEARTBEAT.value, "%s")
        self.send_to_receivers(who, line)
        return True

    def request_screenshots(self, who):
        """ client file requests (get from client) """
        if not self.clients:
            return False
        line = "%s %s %s %s.jpg none none" % (Command.FILETRANSFER.value, Command.SEND.value, DataType.SCREENSHOT.value, "%s")
        self.send_to_receivers(who, line)
        return True

    def request_abgabe(self, who):
        if not self.clients:
            return False

        filename = "Abgabe-%s-%s" % (datetime.datetime.now().strftime("%H-%M-%S"), "%s")
        line = "%s %s %s %s none none" % (Command.FILETRANSFER.value, Command.SEND.value, DataType.ABGABE.value, filename)

        self.send_to_receivers(who, line)
        return True

    """client file transfer (send to client)"""
    def send_file(self, file_path, who, datatype, **kwargs):
        """
        Dispatches Method to prepare requested file transfer and sends file
        :param file_path: absolute filepath
        :param who: all or client id
        :param cleanup_abgabe: del Files on Startup
        :param spellcheck: is Spellcheck on?
        """

        # only used if EXAM is started or finished
        # Default 0 = do nothing
        cleanup_abgabe = kwargs.get("cleanup_abgabe", 0)
        # spellcheck = kwargs.get("spellcheck", 0)

        if file_path:
            filename = ntpath.basename(file_path)  # get filename without path
            filename = str(filename).replace(" ", "_")
            file_size = os.path.getsize(file_path)
            md5_hash = mutual_functions.get_file_md5_hash(file_path)

            if who == 'all':
                self.broadcast_file(file_path, filename, md5_hash, datatype, cleanup_abgabe)
            else:
                client = self.get_client(who)
                client.sendEncodedLine('%s %s %s %s %s %s' % (Command.FILETRANSFER.value, Command.GET.value, datatype, str(filename), md5_hash, cleanup_abgabe))  # trigger clienttask type filename filehash
                client.setRawMode()
                who = client.clientName
                self.send_bytes(client, file_path)
                client.setLineMode()
                client.factory.rawmode = False  # UNLOCK all fileoperations

            return [True, filename, file_size, who]

        return [False, None, None, who]

    def broadcast_line(self, line):
        for client in self.clients.values():
            newline = line % client.clientConnectionID    # substitue the last %s in line with clientConnectionID (don't overwrite line)
            client.sendEncodedLine(newline)

    def broadcast_file(self, file_path, filename, md5_hash, datatype, cleanup_abgabe):
        for client in self.clients.values():
            # trigger clienttask type filename filehash
            client.sendEncodedLine('%s %s %s %s %s %s' % (Command.FILETRANSFER.value, Command.GET.value, datatype, str(filename), md5_hash, cleanup_abgabe))
            client.setRawMode()
            self.send_bytes(client, file_path)
            client.setLineMode()
            client.factory.rawmode = False  # UNLOCK all fileoperations

    """ send bytes """
    def send_bytes(self, client, file_path):
        for b in mutual_functions.read_bytes_from_file(file_path):
            client.transport.write(b)
        client.transport.write(b'\r\n')
