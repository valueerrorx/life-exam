#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
from logging.config import dictConfig

from twisted.python.failure import Failure
from twisted.python import log as twisted_log

logger = logging.getLogger(__name__)

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'twisted':{
            'level': 'ERROR',
        }
    }
}
def failure_to_exc_info(failure):
    """Extract exc_info from Failure instances"""
    if isinstance(failure, Failure):
        return (failure.type, failure.value, failure.getTracebackObject())

def configure_logging(logfile_path):
    """
    Initialize logging defaults, also for a twisted server
    :param logfile_path: rotated logfile used for logging
    :type logfile_path: string

    This function does:
    - Assign INFO and DEBUG level to logger file handler and console handler
    - Route warnings and twisted logging through Python standard logging

    """
    observer = twisted_log.PythonLoggingObserver('twisted')
    observer.start()

    dictConfig(DEFAULT_LOGGING)

    #format, dateformat
    default_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s,%(funcName)s():%(lineno)s] %(message)s",
        "%H:%M:%S")

    file_handler = logging.handlers.RotatingFileHandler(logfile_path, maxBytes=10485760,backupCount=300, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    file_handler.setFormatter(default_formatter)
    console_handler.setFormatter(default_formatter)

    logging.root.setLevel(logging.DEBUG)
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)
