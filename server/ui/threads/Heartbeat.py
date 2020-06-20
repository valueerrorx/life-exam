#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann
import time
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from server.ui.threads.Job import Job
from classes import PeriodicTimer


class Thread_Jobs(QtCore.QThread): 
    """
    a Thread that controlls jobs within the system
    if a job fails for some reason, it will retry n times before giving up
    """
    jobs_done = pyqtSignal()

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.parent = parent
        self.setObjectName("Jobs")
        self.running = False
        self.running = False
        self._jobs = []
        # start after xs than every xs
        self.timer = PeriodicTimer(1, 1, self.checkJobs)
        # start the Timer the first time
        self.timer.first_start()

    def __del__(self):
        self.wait()

    def addClient(self, ID, func):
        """ adds a job for a client """
        self._jobs.append(Job(ID, func))

    def delClient(self, ID):
        """ removes a Job from the list """
        for i in range(len(self._jobs)):
            job = self._jobs[i]
            if job.getID() == ID:
                del self.jobs[i]
                break

    def checkJobs(self):
        """ check all outstanding jobs or retry them """
        print("Job")

    def isAlive(self):
        if self.running:
            return True
        else:
            return False

    def stop(self):
        print("stopping Timer")
        self.timer.stop()
        self.running = False
        print("stopping")

    def run(self):
        """
        this thread waits for all Clients to sent their OK for different
        operations, an event() will be fired
        """
        self.running = True
        while(self.running):
            time.sleep(0.01)
        return 0
