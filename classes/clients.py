import datetime

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

    def broadcast_line(self, line):
        for client in self.clients.itervalues():
            client.sendLine(line % client.clientConnectionID)
            #TODO: pass last substitute for %s in line (might be id, might be name ) as key for the ServerProtocol attribute dictionary

