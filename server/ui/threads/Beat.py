#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann
from argparse import _StoreFalseAction


class Beat():
    """ Data for a Client """
    def __init__(self, ID):
        self._ID = ID   # connection ID
        self._retries = 0
        self._pending = True

    def getConnectionID(self):
        return self._ID

    def setRetries(self, r):
        self._retries = r

    def getRetries(self):
        return self._retries

    def isPending(self):
        """ is there a Request all ready sent for Heartbeat? """
        return self._pending

    def setPending(self, to):
        self._pending = to

    def incCounter(self):
        """trying to contact client"""
        self._retries += 1

    def resetCounter(self):
        self._retries = 0
        self._pending = False
