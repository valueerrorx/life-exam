#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inherit Observer in a class and afterwards use observe(event_name, callback_fn) to listen for a specific event.
Whenever that specific event is fired anywhere in the code (ie. Event('USB connected')),
the corresponding callback will fire.
"""
from classes.Observers import Observers


class Event():
    def __init__(self, event_name, *callback_args):
        for observer in Observers._observers:
            for observable in observer._observed_events:
                if observable['event_name'] == event_name:
                    observable['callback_fn'](*callback_args)
