#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from enum import Enum
from Qt.OvelayIcons.Icon import Icon
import copy
from Qt.OvelayIcons.OpenCVLib import OpenCVLib


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

        # write back to widget
        self.widget.setPixmap(pixmap)

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
                self.icons.append(icon)
                break
        self._repaint()

    def setExamIconON(self):
        """ set all Status Exam Icons to on """
        self.add(Icons.EXAM_ON)

    def setExamIconOFF(self):
        """ set all Status Exam Icons to off """
        self.add(Icons.EXAM_OFF)

    def setFileReceivedOK(self):
        """ set all File received Icon """
        self.add(Icons.FILE_OK)

    def setFileReceivedERROR(self):
        """ set all File NOT Received icon """
        self.add(Icons.FILE_ERROR)
