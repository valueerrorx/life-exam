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
        for existinggroup in self.groups:
            if existinggroup.name == group.name:
                print existinggroup.name
                print group.name
                pin = generatePin(4)
                group.name = "%s-%s" % (group.name, pin)
                self.add_group(group)
                return

        self.groups.append(group)

    def remove_group(self, group):
        self.groups.remove(group)


    def create_groupwidget(self, group, serverui):
        """creates a widget for a group, adds it to the grouplistwidget and adds a mousevent"""
        group.item = QtWidgets.QListWidgetItem()
        group.item.name = group.name  # store clientName as itemID for later use (delete event)
        group.item.info = QtWidgets.QLabel('%s' % (group.name))
        grid = QtWidgets.QVBoxLayout()
        grid.addWidget(group.item.info)
        group.widget = QtWidgets.QWidget()
        group.widget.setLayout(grid)
        serverui.ui.grouplist.addItem(group.item)  # add the listitem to the listwidget
        serverui.ui.grouplist.setItemWidget(group.item, group.widget)  # set the widget as the listitem's widget
        group.widget.mouseReleaseEvent = lambda event: serverui._updateGroupInfo(group)


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

    def create_clientwidget(self, client, serverui):
        """creates a widget for a client, adds it to the clientlistwidget and adds a mousevent"""
        client.item = QtWidgets.QListWidgetItem()
        client.item.name = client.name  # store clientName as itemID for later use (delete event)
        client.item.info = QtWidgets.QLabel('%s' % (client.name))
        grid = QtWidgets.QVBoxLayout()
        grid.addWidget(client.item.info)
        client.widget = QtWidgets.QWidget()
        client.widget.setLayout(grid)
        serverui.ui.clientlist.addItem(client.item)  # add the listitem to the listwidget
        serverui.ui.clientlist.setItemWidget(client.item, client.widget)  # set the widget as the listitem's widget
        client.widget.mouseReleaseEvent=lambda event: serverui._updateClientInfo(client)



class Client:
    def __init__(self):
        self.name = "NamelessClient"
        self.clientConnection = None




