#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import logging
import threading
import time

def thread_wait_for_all_clients(clients):
    """
    on exit Exam, this thread waits for all Clients to send their files
    """
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)
    # then send the exam exit signal
    if not self.factory.server_to_client.exit_exam(who, onexit_cleanup_abgabe):
        self.log("No clients connected")