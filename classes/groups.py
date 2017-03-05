from classes.clients import *
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import *

from common import *

class GroupList:
    def __init__(self):
        self.groups = []   # type: list

    def get_group(self, key):
        for group in self.groups:
            if key == group.name:
                return group
        return None

    def add_group(self, group):
        self.groups.append(group)

    def remove_group(self, group):
        self.groups.remove(group)


    def create_groupwidget(self, group):
        group.item = QtWidgets.QListWidgetItem()
        group.item.name = group.name  # store clientName as itemID for later use (delete event)
        group.item.info = QtWidgets.QLabel('%s' % (group.name))
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(4)
        grid.addWidget(group.item.info, 1, 0)
        group.widget = QtWidgets.QWidget()
        group.widget.setLayout(grid)

        return

    def remove_groupwidget(self, group):
        return



class Group:
    def __init__(self):
        self.clients = []   # type: list
        self.name = "NamelessGroup"
        self.pin = generatePin(4)

    def get_client(self, key):
        for client in self.clients:
            if key == client.name:
                return client
        return None

    def add_client(self, client):
        self.clients.append(client)

    def update_client(self,client):
        self.clients[client.name]

    def remove_client(self, client):
        self.clients.remove(client)

    def create_clientwidget(self, client):
        client.item = QtWidgets.QListWidgetItem()
        client.item.name = client.name  # store clientName as itemID for later use (delete event)
        client.item.info = QtWidgets.QLabel('%s' % (client.name))
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(4)
        grid.addWidget(client.item.info, 1, 0)
        client.widget = QtWidgets.QWidget()
        client.widget.setLayout(grid)
        return



class Client:
    def __init__(self):
        self.name = "NamelessClient"
        self.clientConnection = None




