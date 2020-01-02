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
    #from UI Designer
    width=140
    height=93
    img_width=120
    img_height=67
    
    #Status Icons
    max_status_icons=5
    statusIcons=[]
    #stores Image Name/False if Icon is set/not
    statusIcons_on=[False,False,False,False,False]
        
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
        self.clearStatusIcons()
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
        self.setGeometry(QtCore.QRect(70, 10, 145, 94))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setStyleSheet("border-width: 1px; border-style: solid; border-color: #AAA; margin-top: 4px; margin-left:4px;")
        self.setObjectName("MyCustomWidget")
                
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.image = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
        self.image.setSizePolicy(sizePolicy)
        self.image.setStyleSheet("padding:0;margin:0;border:0;")
        self.image.setText("")
        icon = self.rootDir.joinpath("pixmaps/Test.jpg").as_posix()
        self.image.setPixmap(QtGui.QPixmap(icon))
        self.image.setScaledContents(False)
        self.image.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.image.setObjectName("image")
        self.verticalLayout.addWidget(self.image)
        
        self.info = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.info.sizePolicy().hasHeightForWidth())
        self.info.setSizePolicy(sizePolicy)
        self.info.setMinimumSize(QtCore.QSize(122, 18))
        self.info.setMaximumSize(QtCore.QSize(122, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.info.setFont(font)
        self.info.setStyleSheet("padding:0;margin:0;border:0;")
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        self.info.setObjectName("info")
        self.verticalLayout.addWidget(self.info)
        self.horizontalLayout.addLayout(self.verticalLayout)
        
        self.gridLayout_icons = QtWidgets.QGridLayout()
        self.gridLayout_icons.setHorizontalSpacing(0)
        self.gridLayout_icons.setVerticalSpacing(1)
        self.gridLayout_icons.setObjectName("gridLayout_icons")
        
        #5 status icons
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        for x in range(1, 6):
            status_icon = QtWidgets.QLabel()
            sizePolicy.setHeightForWidth(status_icon.sizePolicy().hasHeightForWidth())
            status_icon.setSizePolicy(sizePolicy)
            status_icon.setStyleSheet("padding:0;margin:0;border:0;")
            status_icon.setText("")
            icon = self.rootDir.joinpath("pixmaps/fileok.png").as_posix()
            status_icon.setPixmap(QtGui.QPixmap(icon))
            status_icon.setAlignment(QtCore.Qt.AlignCenter)
            status_icon.setObjectName("status_icon_%s" % x)
            #int r, int c, int rowspan, int columnspan
            self.gridLayout_icons.addWidget(status_icon, x, 0, 1, 1)
            self.statusIcons.append(status_icon)
        
        self.horizontalLayout.addLayout(self.gridLayout_icons)
        self.setLayout(self.horizontalLayout)
        
        
    def setImage (self, screenshot_file_path):
        """
        sets the screenshot image
        screenshot_file_path ... path to jpg file
        """   
        icon = self.rootDir.joinpath(screenshot_file_path).as_posix()
        pixmap = QtGui.QPixmap(icon)
        pixmap = pixmap.scaled(QtCore.QSize(self.img_width, self.img_height))
        self.image.setPixmap(pixmap)
        
    def getID(self):
        """ return the ID of the Client """
        return self.pID
    
    def setID(self,the_id):
        self.pID = the_id
        
    def setDisabled(self):
        """ Client is disabled """
        self.disabled = True
        
    def setEnabled(self):
        """ Client is enabled """
        self.disabled = False
        
    def isEnabled(self):
        return not self.disabled
        
    def setText (self, text):
        """
        set the text at bottom of Item
        """
        self.info.setText(text)

        
    def clearStatusIcons(self):
        """
        replace all status icons with empty dummy
        """
        for status_icon in self.statusIcons:
            icon = self.rootDir.joinpath("pixmaps/dummy.png").as_posix()
            status_icon.setPixmap(QtGui.QPixmap(icon))
            
        for x in range(0, self.max_status_icons-1):
            self.statusIcons_on[x] = False
        
       
    def setStatusIcon (self, imagePath):
        """
        sets a status icon in one of the 5 places
        """
        #choose next free slot
        index=0
        for isON in self.statusIcons_on:
            #there are 
            if isON == False and index < self.max_status_icons:
                #get the slot
                status_icon = self.statusIcons[index]
                icon = self.rootDir.joinpath(imagePath).as_posix()                
                status_icon.setPixmap(QtGui.QPixmap(icon))
                self.statusIcons_on[index]=imagePath
            else:
                index += 1
                
                
    def removeStatusIcon (self, imagePath):
        """
        search for the correct icon an remove it
        """
        for x in range(0, self.max_status_icons):
            #if icon is set, then its a string
            stored_img = self.statusIcons_on[x]
            if type(stored_img) == str:
                if stored_img == imagePath:
                    #Icon found delete
                    icon = self.rootDir.joinpath("pixmaps/dummy.png").as_posix()
                    self.statusIcons[x].setPixmap(QtGui.QPixmap(icon))
                    self.statusIcons_on[x]=False
            else:
                #Status Icons are a stack, firts False means, there are no more Icons
                return False
        
        
    def setExamIconON(self):
        """ set all Status Exam Icons to on """
        self.removeStatusIcon("pixmaps/exam_off.png")
        self.setStatusIcon("pixmaps/exam_on.png")
        
    def setExamIconOFF(self):
        """ set all Status Exam Icons to off """
        self.removeStatusIcon("pixmaps/exam_on.png")
        self.setStatusIcon("pixmaps/exam_off.png")
        
        