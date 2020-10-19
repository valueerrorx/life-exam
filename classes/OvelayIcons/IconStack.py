#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from enum import Enum
import copy
from classes.OvelayIcons.Icon import Icon
from classes.OvelayIcons.OpenCVLib import OpenCVLib
from PyQt5.QtCore import pyqtSignal, QObject
from pathlib import Path
import time
from classes.OvelayIcons.PeriodicTimer import PeriodicTimer


class Icons(Enum):
    FILE_OK = "file_ok.png"
    FILE_ERROR = "file_error.png"
    EXAM_ON = "exam_on.png"
    EXAM_OFF = "exam_off.png"


class IconStack(QObject):
    """
    - stores the visible Icons from an Image
    - the IconStack is bound to a QPixmap
    - the position is from right top > left top
    Usage:
    # set a Pixmap and a relative Path where to find Overlay Icons 
    self.stack = IconStack(self.ui.image.pixmap(), "overlay_icons/")
    # whenever a Pixmap changed, it will be emitted an event
    self.stack.repaint_event.connect(self.repaint_event)
    # there u set the new Pixmap
    self.ui.image.setPixmap(self.stack.getPixmap())
    """
    # pixmap was updated > repaint
    repaint_event = pyqtSignal()
    
    def __init__(self, pixmap, margin=2):
        """
        :param pixmap: a pixmap
        :param margin: margin-top and margin-right of each icon
        """
        super().__init__()
        self.rootDir = Path(__file__).parent
        self.iconpath = self.rootDir.joinpath('overlay_icons')
        
        # speichert Icon und timestamp ab
        self.icons = []
        self._loaded_icons = []
        self.pixmap = pixmap
        self.iconSize = (64, 64)
        self.loadIcons()
        self.margin = margin
        self.hasbanner = False

        self.cv = OpenCVLib()
        # store the original pixmap
        if self.pixmap != None:
            self._original = self.pixmap.copy()
        
        # Icon Timeout for hidding Icons
        self.hideIconsAfter = 20  # sec
        # start after x sec than every x sec
        self.timer = PeriodicTimer(self, 5, 4, self.timeoutIcons)
        self.timer.first_start()
        
    def close(self):
        """ closing """
        self.timer.stop()
            
    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        self._original = self.pixmap.copy()
        
    def getPixmap(self):
        """ get the changed pixmap """
        return self.pixmap

    def loadIcons(self):
        """ load all Icons from file to preload stack"""
        for i in (Icons):
            icon = Icon(self.iconpath, i.value)
            icon.resizeTo(self.iconSize[0], self.iconSize[1])
            self._loaded_icons.append(icon)
            
    def getIcon(self, data):
        """ returns from Array the Icon Part """
        return data[0]
    
    def getTS(self, data):
        """ returns from Array the TimestampPart Part """
        return data[1]

    def _repaint(self):
        """ draw all Overlay Icons with OpenCV """
        if self.pixmap != None:
            pixmap = self._original
            x = pixmap.width() - 2 * self.margin
            y = self.margin
    
            for i in self.icons:
                x -= self.getIcon(i).getWidth()
                # place all icons from top right to the left
                pixmap = self.cv.overlayIcon(pixmap, self.getIcon(i).getCVImg(), x, y)
                x -= self.margin
                
            if self.hasbanner:
                pixmap = self.drawOffline(pixmap)
                
            # save pixmap
            self.pixmap = pixmap
    
            # fire repaint event
            self.repaint_event.emit()

    def clearIcons(self):
        """ clear all status icons """
        del self.icons[:]
        self.icons = []
        self._repaint()

    def add(self, icon):
        """ adds a icon to the stack and displays it """
        for i in self._loaded_icons:
            # search the right one
            if i.getName() == icon.value:
                # make a full copy of that
                icon = copy.deepcopy(i)
                self.icons.append([icon, time.time()])
                break
        self._repaint()
        
    def remove(self, icon):
        """ removes a icon from the stack """
        for i in self.icons:
            # search the right one
            if self.getIcon(i).getName() == icon.value:
                self.icons.remove(i)
                break
        self._repaint()
        
    def timeoutIcons(self):
        """ Timer has made a tick, which Icons are to hide? """
        now = time.time()
        for i in self.icons:
            # search the right one
            delta = now - self.getTS(i)
            if delta > self.hideIconsAfter:
                self.icons.remove(i)
        self._repaint()
    
    def addExamIconON(self):
        """ show Exam Icons ON """
        self.add(Icons.EXAM_ON)

    def addExamIconOFF(self):
        """ show Exam Icons OFF """
        self.add(Icons.EXAM_OFF)

    def addFileReceivedOK(self):
        """ show File received Icon """
        self.add(Icons.FILE_OK)

    def addFileReceivedERROR(self):
        """ show File NOT Received icon """
        self.add(Icons.FILE_ERROR)
        
    def removeExamIconON(self):
        """ hide Exam Icons ON """
        self.remove(Icons.EXAM_ON)

    def removeExamIconOFF(self):
        """ hide Exam Icons OFF """
        self.remove(Icons.EXAM_OFF)

    def removeFileReceivedOK(self):
        """ hide File received Icon """
        self.remove(Icons.FILE_OK)

    def removeFileReceivedERROR(self):
        """ hide File NOT Received icon """
        self.remove(Icons.FILE_ERROR)
        
    def drawOffline(self, pixmap):
        """ draw Offline Banner at bottom """        
        pixmap = self.cv.drawBanner(pixmap, 16, 'OFFLINE', (0, 0, 255))
        return pixmap
        
    def addOffline(self):
        self.hasbanner = True
        self._repaint()
        
    def removeOffline(self):
        self.hasbanner = False
        self._repaint()
        
