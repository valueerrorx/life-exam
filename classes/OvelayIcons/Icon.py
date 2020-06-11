#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import cv2
import pathlib


class Icon(object):
    """ the Icon as an OpenCV Mat Image """

    def __init__(self, path, filename):
        self.filename = filename
        img = pathlib.Path(path, filename).as_posix()
        self.cvImg = cv2.imread(img, cv2.IMREAD_UNCHANGED)

    def resizeTo(self, width, height):
        """ resize the Mat to this width and height in px """
        h, w = self.cvImg.shape[:2]
        fac_w = width / w
        fac_h = height / h
        width = int(fac_w * w)
        height = int(fac_h * h)

        self.cvImg = cv2.resize(self.cvImg, (width, height), interpolation=cv2.INTER_CUBIC)

    def getName(self):
        return self.filename

    def getCVImg(self):
        return self.cvImg

    def getWidth(self):
        return self.cvImg.shape[1]

    def getHeight(self):
        return self.cvImg.shape[0]
