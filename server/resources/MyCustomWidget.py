#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from pathlib import Path

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSize


class MyCustomWidget (QtWidgets.QWidget):
    """
    Creates a Item for the Client
    """
    # from UI Designer
    width = 140
    height = 93
    img_width = 120
    img_height = 67

    # Status Icons
    max_status_icons = 5
    statusIcons = []
    # stores Image Name/False if Icon is set/not
    statusIcons_on = [False, False, False, False, False]

    def __init__(self, client, screenshot_file_path):
        super(MyCustomWidget, self).__init__()

        # rootDir of Application
        self.rootDir = Path(__file__).parent.parent.parent

        self.client = client
        self.screenshot_file_path = screenshot_file_path

        # store clientName as itemID for later use (delete event)
        self.id = client.clientName
        self.pID = client.clientConnectionID
        self.disabled = False
        self.setMinimumSize(self.width, self.height)
        self.setMaximumSize(self.width, self.height)

        self.set_ui()
        self.setText('%s' % (client.clientName))
        self.clearStatusIcons()
        self.show()

    def sizeHint(self, *args, **kwargs):
        """
        this is our default size
        """
        return QSize(self.width, self.height)

 


    def set_ui(self):
        """
        designed wit QT Designer, converted with pyuic5
        - replace: self.mywidget > self.
        - self.setGeometry( to 0,0 
        """
        self.setGeometry(QtCore.QRect(0, 0, 182, 116))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setStyleSheet("border-width: 1px; border-style: solid; border-color: #AAA; margin-top: 4px; margin-left:4px;")
        self.setObjectName("mywidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
        self.image.setSizePolicy(sizePolicy)
        self.image.setMinimumSize(QtCore.QSize(180, 100))
        self.image.setMaximumSize(QtCore.QSize(180, 100))
        self.image.setStyleSheet("padding:0;margin:0;border:0;")
        self.image.setText("")
        self.image.setScaledContents(False)
        self.image.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.image.setObjectName("image")
        self.verticalLayout.addWidget(self.image)
        self.info = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.info.sizePolicy().hasHeightForWidth())
        self.info.setSizePolicy(sizePolicy)
        self.info.setMinimumSize(QtCore.QSize(180, 14))
        self.info.setMaximumSize(QtCore.QSize(180, 14))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.info.setFont(font)
        self.info.setStyleSheet("padding:0;margin:0;border:0;")
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        self.info.setObjectName("info")
        self.verticalLayout.addWidget(self.info)
        self.horizontalLayout.addLayout(self.verticalLayout)

    def setImage(self, screenshot_file_path):
        """
        sets the screenshot image
        screenshot_file_path ... path to jpg file
        """
        icon = self.rootDir.joinpath(screenshot_file_path).as_posix()
        pixmap = QtGui.QPixmap(icon)
        pixmap = pixmap.scaled(QtCore.QSize(self.img_width, self.img_height))
        self.image.setPixmap(pixmap)

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

    def setDisabled(self):
        """ Client is disabled """
        self.disabled = True

    def setEnabled(self):
        """ Client is enabled """
        self.disabled = False

    def isEnabled(self):
        return not self.disabled

    def setText(self, text):
        """
        set the text at bottom of Item
        """
        self.info.setText(text)

    def setExamIconON(self):
        """ set all Status Exam Icons to on """
        self.removeStatusIcon("pixmaps/exam_off.png")
        self.setStatusIcon("pixmaps/exam_on.png")

    def setExamIconOFF(self):
        """ set all Status Exam Icons to off """
        self.removeStatusIcon("pixmaps/exam_on.png")
        self.setStatusIcon("pixmaps/exam_off.png")

    def setFileReceivedOK(self):
        """ set all File received Icon """
        self.removeStatusIcon("pixmaps/file_cancel.png")
        self.removeStatusIcon("pixmaps/file_ok.png")
        self.setStatusIcon("pixmaps/file_ok.png")

    def setFileReceivedERROR(self):
        """ set all File NOT Received icon """
        self.removeStatusIcon("pixmaps/file_ok.png")
        self.removeStatusIcon("pixmaps/file_cancel.png")
        self.setStatusIcon("pixmaps/file_cancel.png")
