#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann

import logging
import threading
import time

def getConnectionStr(clients, id):
    erg=""
    for item in clients:
        if id == item.id:
            erg = item.id
            break
    return erg

def delClient(clients, id):
    """ deletes a client from list """
    for item in clients:
        if id == item.id:
            clients.remove(item)
            break
    return clients

def thread_wait_for_all_clients(clients, e, factory, onexit_cleanup_abgabe):
    """
    on exit Exam, this thread waits for all Clients to send their files
    """
    #wait for first client to be ready
    e.wait()
    while(len(clients)>0):
        e.wait()
        #Get Event from MyServerProtocol
        logging.debug('Client finished transferring Abgabe')
        #remove from list
        who = getConnectionStr(clients, e.param)
        clients = delClient(clients, e.param)
        # then send the exam exit signal
        if not factory.server_to_client.exit_exam(who, onexit_cleanup_abgabe):
            pass

    return 0
    