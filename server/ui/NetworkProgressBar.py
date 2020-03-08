#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

""" Just a Class to handle the Progressbar for network operations """
class NetworkProgressBar:
    
    def __init__(self, progress):
        self.progress = progress
        self.progress.hide()
        
    def show(self, clients_count):
        """ shows a ProgressBar for Network operations, the size equals number of clients """
        self.progress.setMaximum(clients_count)
        self.progress.setValue(clients_count)
        self.progress.show()
        
    def hide(self):
        self.progress.hide()
        
    def value(self):
        return self.progress.value()
        
    def decrement(self, value=1):
        """ decrement Progressbar by value """
        v = self.progress.value()
        v-=value
        if v>0:
            self.progress.setValue(v)
        elif v==0:
            self.hide()
    