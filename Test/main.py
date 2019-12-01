'''
@author: Mag. Stefan Hagmann
'''

import sys
#Logging Stuff
import logging

from twistedServer import start_server

from utils.hello import hello

#My Libs------------------------------------------------------------------------
from utils.logger import * 
    
def main():
    configure_logging('logfilepath')
    #hello()


    #configure_logging('logfile_path.txt')
    #log = logging.getLogger(__name__)
    
       
    start_server()
    
    log.warning('Watch out!')  # will print a message to the console
    log.info('I told you so')  # will not print anything
    
    
    
    
    
""" Hauptprogramm """
if __name__ == '__main__':
    main()