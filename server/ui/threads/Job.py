#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

class Job(object):
    """ Data for a job """

    def __init__(self, ID, func):
        self.ID = ID
        self._func = func
        self._retries = 0

    def getID(self):
        return self._ID
        
    def getFunction(self):
        return self._func
