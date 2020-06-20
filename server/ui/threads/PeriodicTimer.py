#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

from threading import Timer


# https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds
class PeriodicTimer(object):
    def __init__(self, first_interval, interval, func, *args, **kwargs):
        self.timer = None
        self.first_interval = first_interval
        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.running = False
        self.is_started = False

    def first_start(self):
        try:
            # if already started will not start again
            if not self.is_started:
                self.is_started = True
                self.timer = Timer(self.first_interval, self.run)
                self.running = True
                self.timer.start()
        except Exception as e:
            print("PeriodicTimer first_start failed %s" % (e.message))
            raise

    def run(self):
        # if not stopped start again
        if self.running:
            self.timer = Timer(self.interval, self.run)
            self.timer.start()
        self.func(*self.args, **self.kwargs)

    def stop(self):
        """
        cancel current timer in case failed it's still OK
        if already stopped doesn't matter to stop again
        """
        if self.timer:
            self.timer.cancel()
        self.running = False
