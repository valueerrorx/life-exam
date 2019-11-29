'''
Created on 26.11.2019

@author: Mag. Stefan Hagmann
'''

import sys

#Logging Stuff
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from threading import Thread

#Serverthread
from Main.twigServer import runTwistedServer

#logger = logging.getLogger(__name__)


def createLogging():
    """ 
    initial the Logging System
    log to a file with rotating, also log to stdout
    """
    handlers = [
        RotatingFileHandler('log-rotating.txt', maxBytes=10000, backupCount=3),
        # Default stream=sys.stderr
        StreamHandler(sys.stdout),  
    ]
    logging.basicConfig(handlers=handlers, level=logging.DEBUG)

def start_server():
    """ start the server in a thread """
    t = Thread(target=runTwistedServer, args=())
    t.start()

    
def main():
    createLogging()
    start_server()
    logging.warning('Watch out!')  # will print a message to the console
    logging.info('I told you so')  # will not print anything
    
    
    
""" Hauptprogramm """
if __name__ == '__main__':
    main()
    


    
    

 
