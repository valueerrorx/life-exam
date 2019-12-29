#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSize

"""
Creates a Item for the Client
"""
class MyCustomWidget (QtWidgets.QWidget):
    def __init__(self, client, screenshot_file_path):
        super(MyCustomWidget, self).__init__()
        
        self.client = client
        self.screenshot_file_path = screenshot_file_path
        
        # store clientName as itemID for later use (delete event)
        self.id = client.clientName  
        self.pID = client.clientConnectionID
        self.disabled = False
        
        self.set_ui()
        self.setText('%s' % (client.clientName))
        
    def sizeHint(self, *args, **kwargs):
        #QtCore.QSize(140, 100)
        width = self.horizontalLayoutWidget.geometry().width()
        height = self.horizontalLayoutWidget.geometry().height()
        return QSize(width, height)
                
    def set_ui(self):
        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        #x,y,size
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(270, 40, 151, 91))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image = QtWidgets.QLabel(self.horizontalLayoutWidget)
        
        self.image.setText("")
        self.image.setPixmap(QtGui.QPixmap("Test.jpg"))
        self.image.setObjectName("image")
        
        self.verticalLayout.addWidget(self.image)
        self.info = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        self.info.setObjectName("info")
        self.verticalLayout.addWidget(self.info)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.status = QtWidgets.QLabel(self.horizontalLayoutWidget)

        self.status.setPixmap(QtGui.QPixmap("LIFE-Dev/life-exam/pixmaps/fileok.png"))
        self.status.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.status.setObjectName("status")
        
        self.horizontalLayout.addWidget(self.status)
        
        
       
    def setText (self, text):
        """
        set the text at bottom of Item
        """
        self.status.setText(text)

    def setIcon (self, imagePath):
        self.iconQLabel.setPixmap(QtGui.QPixmap(imagePath))
        
    def setStatusIcon (self, imagePath):
        self.iconQLabel.setPixmap(QtGui.QPixmap(imagePath))
        