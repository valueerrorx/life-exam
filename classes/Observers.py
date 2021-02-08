#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inherit Observer in a class and afterwards use observe(event_name, callback_fn) to listen for a specific event.
Whenever that specific event is fired anywhere in the code (ie. Event('USB connected')),
the corresponding callback will fire.
"""


class Observers():
    _observers = []

    def __init__(self):
        self._observers.append(self)
        self._observed_events = []

    def observe(self, event_name, callback_fn):
        self._observed_events.append({'event_name': event_name, 'callback_fn': callback_fn})
    
    def getObservers(self):
        return self._observers
