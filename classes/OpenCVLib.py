#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import cv2
import numpy as np
from PyQt5.Qt import QImage, qRgb
from PyQt5 import QtGui


class OpenCVLib(object):
    """
    for inspiration have a look at
    https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html
    """

    def readPNG(self, img):
        """ preserver all channels """
        return cv2.imread(img, cv2.IMREAD_UNCHANGED)

    def QImage2MAT(self, qimg):
        """Converts a QImage into an opencv MAT format"""
        incomingImage = qimg.convertToFormat(4)  # RGB32
        width = incomingImage.width()
        height = incomingImage.height()

        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  # copies the data
        return arr

    def MAT2QPixmap(self, cvImg):
        """ convert CV Image to QPixmap """
        return QtGui.QPixmap.fromImage(self.MAT2QImage(cvImg))

    def QImage2QPixmap(self, img):
        """ convert QImage to QPixmap """
        return QtGui.QPixmap.fromImage(img)

    def MAT2QImage(self, im, copy=False):
        """ convert CV MAT to QImage
        see https://gist.github.com/smex/5287589 """
        """
        Because OpenCV uses BGR order by default, you should first use
        cvtColor(src, dst, CV_BGR2RGB)
        to get an image layout that Qt understands
        """
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)  # important!
        gray_color_table = [qRgb(i, i, i) for i in range(256)]
        if im is None:
            return QImage()
        if im.dtype == np.uint8:
            if len(im.shape) == 2:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
                qim.setColorTable(gray_color_table)
                return qim.copy() if copy else qim

            elif len(im.shape) == 3:
                if im.shape[2] == 3:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888)
                    return qim.copy() if copy else qim
                elif im.shape[2] == 4:
                    qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32)
                    return qim.copy() if copy else qim

    def resizeTo(self, img, width, height):
        """ resize the Mat to this width and height in px """
        h, w = img.shape[:2]
        fac_w = width / w
        fac_h = height / h
        # print("%s x %s" % (fac_w * w, fac_h * h))
        return cv2.resize(img, (int(fac_w * w), int(fac_h * h)), interpolation=cv2.INTER_CUBIC)

    def transparentOverlay(self, src, overlay, x, y):
        """
        Place a overlay PNG Image onto background on position x, y
        :param src: Input Color Background Image
        :param overlay: transparent Image
        :param pos:  position where the image to be
        :return: Resultant Image
        """
        overlay = cv2.cvtColor(overlay, cv2.COLOR_RGB2BGRA)  # important
        src = cv2.cvtColor(src, cv2.COLOR_RGB2BGRA)
        # Convert overlay to it to 8-bit
        self.map_uint16_to_uint8(overlay)  # important

        # Size of foreground
        h, w, _ = overlay.shape
        # Size of background Image
        rows, cols, _ = src.shape
        # loop over all pixels and apply alpha
        for i in range(h):
            for j in range(w):
                if (x + i) >= rows or (y + j) >= cols:
                    continue
                # read the alpha channel
                alpha = float(overlay[i][j][3] / 255.0)
                try:
                    src[x + i][y + j] = alpha * overlay[i][j] + (1 - alpha) * src[x + i][y + j]
                except ValueError:
                    print("Pixeldata mismatch, e.g. RGB and RGBA")
        return src

    def filter(self, cvImg):
        """
        see https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html
        """
        # return cv2.medianBlur(cvImg, 5)
        # tuppel positiv an odd!
        return cv2.GaussianBlur(cvImg, (3, 3), 0)

    def overlayIcon(self, pixmap, icon, x=0, y=0):
        """
        place icon onto pixmap
        :param pixmap: an QPixmap Image
        :param icon: smaller Image
        :param x,y:  position where the image to be
        :return: Resultant QPixmap
        """
        # Glätten
        icon = self.filter(icon)
        Qimg = pixmap.toImage()
        img = self.QImage2MAT(Qimg)
        output = img.copy()

        output = self.transparentOverlay(output, icon, y, x)
        output = cv2.cvtColor(output, cv2.COLOR_BGRA2RGB)
        return self.MAT2QPixmap(output)

    def map_uint16_to_uint8(self, img, lower_bound=None, upper_bound=None):
        '''
        Map a 16-bit image trough a lookup table to convert it to 8-bit.
        :param img: numpy.ndarray[np.uint16] image that should be mapped
        :param lower_bound: int, optional
            lower bound of the range that should be mapped to ``[0, 255]``,
            value must be in the range ``[0, 65535]`` and smaller than `upper_bound`
            (defaults to ``numpy.min(img)``)
        :param upper_bound: int, optional
           upper bound of the range that should be mapped to ``[0, 255]``,
           value must be in the range ``[0, 65535]`` and larger than `lower_bound`
           (defaults to ``numpy.max(img)``)
        '''
        if lower_bound is not None and not(0 <= lower_bound < 2**16):
            raise ValueError(
                '"lower_bound" must be in the range [0, 65535]')
        if upper_bound is not None and not(0 <= upper_bound < 2**16):
            raise ValueError(
                '"upper_bound" must be in the range [0, 65535]')
        if lower_bound is None:
            lower_bound = np.min(img)
        if upper_bound is None:
            upper_bound = np.max(img)
        if lower_bound >= upper_bound:
            raise ValueError(
                '"lower_bound" must be smaller than "upper_bound"')
        lut = np.concatenate([
            np.zeros(lower_bound, dtype=np.uint16),
            np.linspace(0, 255, upper_bound - lower_bound).astype(np.uint16),
            np.ones(2**16 - upper_bound, dtype=np.uint16) * 255
        ])
        return lut[img].astype(np.uint8)
