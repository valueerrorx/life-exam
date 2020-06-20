#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

class Beats(object):
    """ Data for a Client """
    def __init__(self, ID):
        self.ID = ID
        self._retries = 0

    def getID(self):
        return self._ID
