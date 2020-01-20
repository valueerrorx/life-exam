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


class ServerToClient:
    def __init__(self):
        self.clients = dict()           # type: dict
        # we will store the time of the last (try) to connect with.. check it against the screenshot 
        # intervall (our heartbeat) and disconnect client if the timespan is twice the heartbeat intervall
        self.clientlifesigns = dict()   #type: dict       

    ## client handling ##
    def get_client(self, key):
        client = self.clients.get(key, None)  # type: MyServerProtocol
        return client

    def add_client(self, client):
        """
        Client has made a connection
        """
        self.clients.update({str(client.transport.client[1]): client})

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
    
    
    

    ## client instructions ##
    def exit_exam(self, who, onexit_cleanup_abgabe="none"):
        if not self.clients:
            return False
        line = "%s %s %s" % (Command.EXITEXAM.value, onexit_cleanup_abgabe, "%s")
        if who is "all":
            self.broadcast_line(line)
        else:
            client = self.get_client(who)
            client.sendEncodedLine(line % client.clientConnectionID)    #replace %s in line with connectionID
        return True
    

    def lock_screens(self, who):
        if not self.clients:
            return False
        line = "%s %s" % (Command.LOCK.value, "%s")
        if who is "all":
            for clientid in self.clients:
                client = self.get_client(clientid)
                client.sendEncodedLine(line % client.clientConnectionID)
        else:
            client = self.get_client(who)
            client.sendEncodedLine(line % client.clientConnectionID)
        return True


    def unlock_screens(self, who):
        if not self.clients:
            return False
        line = "%s %s" % (Command.UNLOCK.value, "%s")
        if who is "all":
            for clientid in self.clients:
                client = self.get_client(clientid)
                client.sendEncodedLine(line % client.clientConnectionID)
        else:
            client = self.get_client(who)
            client.sendEncodedLine(line % client.clientConnectionID)

        return True


    def request_screenshots(self, who):
        """ client file requests (get from client) """
        if not self.clients:
            return False

        line = "%s %s %s %s.jpg none none" % (Command.FILETRANSFER.value, Command.SEND.value, DataType.SCREENSHOT.value, "%s")
        if who is "all":
            self.broadcast_line(line)
        else:
            client = self.get_client(who)
            client.sendEncodedLine(line % client.clientConnectionID  )
        return True


    def request_abgabe(self, who):
        if not self.clients:
            return False

        filename = "Abgabe-%s-%s" % (datetime.datetime.now().strftime("%H-%M-%S"), "%s")
        line = "%s %s %s %s none none" % (Command.FILETRANSFER.value, Command.SEND.value, DataType.ABGABE.value, filename)
        
        if who is "all":
            self.broadcast_line(line)
        else:
            client = self.get_client(who)          
            client.sendEncodedLine(line % client.clientConnectionID) # filename still has an empty %s to fill with client id

        return True

    
    ## client file transfer (send to client)
    def send_file(self, file_path, who, datatype, cleanup_abgabe="none"):
        """
        Dispatches Method to prepare requested file transfer and sends file
        :param file_path: absolute filepath
        :param who: all or client id
        :param args: (cleanup_abgabe) for exam mode
        """
        if file_path:
            filename = ntpath.basename(file_path)  # get filename without path
            filename = str(filename).replace(" ", "_")
            file_size = os.path.getsize(file_path)
            md5_hash = mutual_functions.get_file_md5_hash(file_path)

            if who is 'all':
                self.broadcast_file(file_path, filename, md5_hash, datatype, cleanup_abgabe)
            else:
                client = self.get_client(who)
                client.sendEncodedLine('%s %s %s %s %s %s' % (Command.FILETRANSFER.value, Command.GET.value, datatype, str(filename), md5_hash, cleanup_abgabe ))  # trigger clienttask type filename filehash)
                client.setRawMode()
                who = client.clientName
                self.send_bytes(client, file_path)
                client.setLineMode()
                client.factory.rawmode = False  # UNLOCK all fileoperations 

            return [True, filename, file_size, who]

        return [False, None, None, who]


    def broadcast_line(self, line):
        for client in self.clients.values():
            newline = line % client.clientConnectionID    #substitue the last %s in line with clientConnectionID (don't overwrite line)
            client.sendEncodedLine(newline)


    def broadcast_file(self, file_path, filename, md5_hash, datatype, cleanup_abgabe):
        for client in self.clients.values():
            client.sendEncodedLine('%s %s %s %s %s %s' % (Command.FILETRANSFER.value, Command.GET.value, datatype, str(filename), md5_hash, cleanup_abgabe))  # trigger clienttask type filename filehash)
            client.setRawMode()
            self.send_bytes(client, file_path)
            client.setLineMode()
            client.factory.rawmode = False  # UNLOCK all fileoperations 



    ## send bytes ##
    def send_bytes(self, client, file_path): 
        for b in mutual_functions.read_bytes_from_file(file_path):
            client.transport.write(b)
        client.transport.write(b'\r\n')
    