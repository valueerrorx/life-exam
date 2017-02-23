import datetime
import ntpath
import os

from common import get_file_md5_hash, read_bytes_from_file
from server import MyServerProtocol
from config.enums import Command, DataType


class ClientList:
    def __init__(self):
        self.clients = dict()   # type: dict

    def get_client(self, key):
        client = self.clients.get(key, None)  # type: MyServerProtocol
        return client

    def add_client(self, client):
        self.clients.update({str(client.transport.client[1]): client})

    def remove_client(self, client):
        del self.clients[client.clientConnectionID]

    def request_screenshots(self, who):

        if not self.clients:
            return False

        line = "%s %s %s %s.jpg none" % (Command.FILETRANSFER, Command.SEND, DataType.SCREENSHOT, "%s")
        if who is "all":
            self.broadcast_line(line)
        else:
            client = self.get_client(who)
            client.sendLine(line % client.clientConnectionID)

        return True

    def request_abgabe(self, who):
        if not self.clients:
            return False

        filename = "Abgabe-%s-%s" % (datetime.datetime.now().strftime("%H:%M:%S"), "%s")
        line = "%s %s %s %s none" % (Command.FILETRANSFER, Command.SEND, DataType.ABGABE, filename)

        if who is "all":
            self.broadcast_line(line)
        else:
            client = self.get_client(who)
            client.sendLine(line % client.clientName)

        return True

    def send_file(self, file_path, who):
        if file_path:
            filename = ntpath.basename(file_path)  # get filename without path
            file_size = os.path.getsize(file_path)
            md5_hash = get_file_md5_hash(file_path)

            if who is 'all':
                self.broadcast_file(file_path, filename, md5_hash)
            else:
                client = self.get_client(who)
                client.sendLine('%s %s %s %s %s' % (Command.FILETRANSFER, Command.GET, DataType.FILE, str(filename), md5_hash))  # trigger clienttask type filename filehash)
                client.setRawMode()
                who = client.clientName
                self.send_bytes(client, file_path)
                client.setLineMode()

            return [True, filename, file_size, who]

        return [False, None, None, who]

    def broadcast_line(self, line):
        for client in self.clients.itervalues():
            client.sendLine(line % client.clientConnectionID)
            #TODO: pass last substitute for %s in line (might be id, might be name ) as key for the ServerProtocol attribute dictionary

    def broadcast_file(self, file_path, filename, md5_hash):
        for client in self.clients.values():
            client.sendLine('%s %s %s %s %s' % (Command.FILETRANSFER, Command.GET, DataType.FILE, str(filename), md5_hash))  # trigger clienttask type filename filehash)
            client.setRawMode()
            self.send_bytes(client, file_path)
            client.setLineMode()


    def send_bytes(self, client, file_path): # TODO: this can probably go in common.py
        for bytes in read_bytes_from_file(file_path):
            client.transport.write(bytes)

        client.transport.write('\r\n')

    def kick_client(self, client_id):
        client = self.get_client(client_id)
        if client:
            client.refused = True
            client.sendLine("%s" % Command.REMOVED)
            client.transport.loseConnection()
            return client.clientName
        return False
