#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from enum import Enum
import copy
from classes.OvelayIcons.Icon import Icon
from classes.OvelayIcons.OpenCVLib import OpenCVLib


class Icons(Enum):
    FILE_OK = "file_ok.png"
    FILE_ERROR = "file_error.png"
    EXAM_ON = "exam_on.png"
    EXAM_OFF = "exam_off.png"


class IconStack(object):
    """
    stores the visible Icons from an Image
    the IconStack is bound to a QPixmap
    the position is from right top > left top
    stores also the time that the Icon is displayed
    """

    def __init__(self, widget, iconpath, margin=2):
        """
        :param widget: the widget that holds a pixmap
        :param iconpath: where to find the Icons
        :param margin: margin-top and margin-right of each icon
        """
        self.icons = []
        self._loaded_icons = []
        self.widget = widget
        self.iconpath = iconpath
        self.iconSize = (64, 64)
        self.loadIcons()
        self.margin = margin
        self.hasbanner = False

        self.cv = OpenCVLib()
        # store the original pixmap
        self._original = self.widget.pixmap().copy()

    def loadIcons(self):
        """ load all Icons from file to preload stack"""
        for i in (Icons):
            icon = Icon(self.iconpath, i.value)
            icon.resizeTo(self.iconSize[0], self.iconSize[1])
            self._loaded_icons.append(icon)

    def _repaint(self):
        """ draw all Overlay Icons with OpenCV """
        pixmap = self._original
        x = pixmap.width() - 2 * self.margin
        y = self.margin

        for i in self.icons:
            x -= i.getWidth()
            # place all icons from top right to the left
            pixmap = self.cv.overlayIcon(pixmap, i.getCVImg(), x, y)
            x -= self.margin
            
        if self.hasbanner:
            pixmap = self.drawOffline(pixmap)

        # write back to widget
        self.widget.setPixmap(pixmap)

    def clearIcons(self):
        """ clear all status icons """
        del self.icons[:]
        self.icons = []
        self._repaint()
        
    def printArray(self, arr):
        for i in arr:
            print(i.getName())

    def add(self, icon):
        """ adds a icon to the stack and displays it """
        for i in self._loaded_icons:
            # search the right one
            if i.getName() == icon.value:
                # make a full copy of that
                icon = copy.deepcopy(i)
                self.icons.append(icon)
                break
        self._repaint()
        
    def remove(self, icon):
        """ removes a icon from the stack """
        for i in self.icons:
            # search the right one
            if i.getName() == icon.value:
                self.icons.remove(i)
                break
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
        banner_height = 20
        ypos = pixmap.height() - banner_height
        color = (0, 0, 255)
        pixmap = self.cv.overlayBanner(pixmap, "Offline", ypos, banner_height, color, 0.5)
        return pixmap
        
    def addOffline(self):
        self.hasbanner = True
        self._repaint()
        
    def removeOffline(self):
        self.hasbanner = False
        self._repaint()
        
