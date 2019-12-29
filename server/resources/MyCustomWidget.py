#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from pathlib import Path

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSize

"""
Creates a Item for the Client
"""
class MyCustomWidget (QtWidgets.QWidget):
    width=140
    height=100
    
    def __init__(self, client, screenshot_file_path):
        super(MyCustomWidget, self).__init__()
        
        #rootDir of Application
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
        self.show()
    
    def sizeHint(self, *args, **kwargs):
        """
        this is our default size
        """
        return QSize(self.width, self.height)
                    
    def set_ui(self):
        """
        designed wit QT Designer, convertet with pyuic5
        dropped self.gridLayoutWidget 
        """
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        
        self.image = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
        self.image.setSizePolicy(sizePolicy)
        self.image.setText("")
        
        icon = self.rootDir.joinpath("pixmaps/Test.jpg").as_posix()
        self.image.setPixmap(QtGui.QPixmap(icon))
        self.image.setAlignment(QtCore.Qt.AlignCenter)
        self.image.setObjectName("image")
        self.gridLayout.addWidget(self.image, 0, 0, 1, 1)
        
        self.info = QtWidgets.QLabel()
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        self.info.setObjectName("info")
        self.gridLayout.addWidget(self.info, 1, 0, 1, 1)
        
        self.status = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status.sizePolicy().hasHeightForWidth())
        self.status.setSizePolicy(sizePolicy)
        self.status.setText("")
        icon = self.rootDir.joinpath("pixmaps/fileok.png").as_posix()
        self.status.setPixmap(QtGui.QPixmap(icon))
        self.status.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.status.setObjectName("status")
        self.gridLayout.addWidget(self.status, 0, 1, 1, 1)
        
        
        
        #self.project_title = QtWidgets.QLabel("Learn Python")
        #self.task_title = QtWidgets.QLabel("Learn more about forms, models and include")
        #self.gridLayout.addWidget(self.project_title, 0, 0)
        #self.gridLayout.addWidget(self.task_title, 1, 0)
        self.setStyleSheet("background-color: red;")

        self.setLayout(self.gridLayout)
        
        
       
    def setText (self, text):
        """
        set the text at bottom of Item
        """
        pass
        #self.status.setText(text)

    def setIcon (self, imagePath):
        self.iconQLabel.setPixmap(QtGui.QPixmap(imagePath))
        
    def setStatusIcon (self, imagePath):
        self.iconQLabel.setPixmap(QtGui.QPixmap(imagePath))
        