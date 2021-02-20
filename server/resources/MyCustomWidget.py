#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from pathlib import Path

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSize
from classes.OvelayIcons.IconStack import IconStack


class MyCustomWidget (QtWidgets.QWidget):
    """
    Creates a Item for the Client
    """

    def __init__(self, client, screenshot_file_path):
        super(MyCustomWidget, self).__init__()

        # rootDir of Application
        self.rootDir = Path(__file__).parent.parent.parent

        self.client = client
        self.screenshot_file_path = screenshot_file_path

        # store clientName as itemID for later use (delete event)
        self.id = client.clientName             # eg TestUser
        self.pID = client.clientConnectionID    # eg 5508
        self.ip = client.transport.hostname     # eg 192.168.1.10

        self.image_width = 180
        self.image_height = 101
        self.widget_width = 204
        self.widget_height = 133

        self.set_ui()
        self.setText('%s' % (client.clientName))

        # Overlay IconsIconStack, hier noch kein Pixmap vorhanden
        self.iconStack = IconStack(None)
        self.iconStack.repaint_event.connect(self.repaint_event)

        self.show()

    def close(self):
        """ stop Timer for Icons """
        self.iconStack.close()

    def sizeHint(self):
        """ this is our default size """
        return QSize(self.widget_width, self.widget_height)

    def set_ui(self):
        """
        designed with QT Designer, converted with pyuic5
        - replace: self.mywidget > self.
        - suche: self.mywidget > self
        - dontuseLabel löschen
        """
        self.setGeometry(QtCore.QRect(0, 0, self.widget_width, self.widget_height))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(self.image_width, self.image_height))
        # self.setMaximumSize(QtCore.QSize(196, 125))
        self.setObjectName("mywidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.content = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.content.sizePolicy().hasHeightForWidth())
        self.content.setSizePolicy(sizePolicy)
        self.content.setStyleSheet("border-width: 1px; border-style: solid; border-color: #666666; margin: 5x 2px;")
        self.content.setObjectName("content")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.content)
        self.horizontalLayout_2.setContentsMargins(8, 5, 8, 5)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image = QtWidgets.QLabel(self.content)
        self.image.setStyleSheet("padding:0;margin:0;border:0;background-color: #ffff00;")
        self.image.setText("")
        self.image.setScaledContents(False)
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.image.setObjectName("image")
        self.verticalLayout.addWidget(self.image)
        self.info = QtWidgets.QLabel(self.content)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.info.sizePolicy().hasHeightForWidth())
        self.info.setSizePolicy(sizePolicy)
        self.info.setMinimumSize(QtCore.QSize(0, 14))
        self.info.setMaximumSize(QtCore.QSize(16777215, 14))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.info.setFont(font)
        self.info.setStyleSheet("padding:0;margin:0;border:0;")
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        self.info.setObjectName("info")
        self.verticalLayout.addWidget(self.info)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout.addWidget(self.content)

    def setImage(self, screenshot_file_path):
        """
        sets the screenshot image
        screenshot_file_path ... path to jpg file
        """
        icon = self.rootDir.joinpath(screenshot_file_path).as_posix()
        pixmap = QtGui.QPixmap(icon)
        pixmap = pixmap.scaled(self.image_width, self.image_height)
        self.image.setPixmap(pixmap)

        # Overlay Icons
        self.iconStack.setPixmap(pixmap)
        self.repaint()

    def repaint_event(self):
        """ Pixmap has changed > repaint """
        self.image.setPixmap(self.iconStack.getPixmap())

    def getConnectionID(self):
        """ return the ID of the Client """
        return self.pID

    def setID(self, the_id):
        self.pID = the_id

    def getID(self):
        """ return the ID of the Client """
        return self.getName()

    def getName(self):
        """ return the ID of the Client """
        return self.id

    def setIP(self, the_ip):
        self.ip = the_ip

    def getIP(self):
        """ return the IP Adr. of the Client """
        return self.ip

    def setText(self, text):
        """
        set the text at bottom of Item
        """
        self.info.setText(text)

    def setExamIconON(self):
        """ set all Status Exam Icons to on """
        pass

    def setExamIconOFF(self):
        """ set all Status Exam Icons to off """
        pass

    def setFileReceivedOK(self):
        """ set all File received Icon """
        self.iconStack.addFileReceivedOK()

    def setFileReceivedERROR(self):
        """ set all File NOT Received icon """
        self.iconStack.addFileReceivedERROR()

    def setOffline(self):
        """ set Client Offline, due to missing heartbeats """
        self.iconStack.addOffline()
