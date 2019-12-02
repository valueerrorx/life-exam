#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from pathlib import Path 

import logging
import logging.handlers
import logging.config

from twisted.python.failure import Failure
from twisted.python import log as twisted_log

path_to_yml = "%s/%s" % (Path(__file__).parent.as_posix(), 'logger.yaml')
loggin_path = Path(__file__).parent.parent.as_posix()

def load_yml():
    """
    Handle the yaml file an add the logging path to filenames
    """
    with open(path_to_yml, 'rt') as f:
        yml_config = yaml.safe_load(f.read())
      
    el = yml_config['handlers']
   
    #Dateiname mit Pfad anpassen
    for item in yml_config['handlers']:
        part = yml_config['handlers'][item]
        if 'filename' in part:
            yml_config['handlers'][item]['filename'] = '%s/%s' % (loggin_path, part['filename']) 
    return yml_config


def load_logging_config(
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """
    Setup logging configuration from the yaml File config/logger
    """
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path_to_yml):
        with open(path_to_yml, 'rt') as f:
            config = load_yml()
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def configure_logging(logfile_path):
    """
    Initialize logging defaults, also for a twisted server
    :param logfile_path: path to store the file(s)
    """
     
    load_logging_config()
    logger = logging.getLogger(__name__)
        
    observer = twisted_log.PythonLoggingObserver('twisted')
    observer.start()
    logger.info("Logger Configured")