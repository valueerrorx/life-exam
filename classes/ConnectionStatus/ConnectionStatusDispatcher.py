#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 Stefan Hagmann
import sys
from PyQt5.QtWidgets import QApplication
from classes.ConnectionStatus.ConnectionStatus import ConnectionStatus


def close_app():
    QApplication.quit()


def printhelp():
    msg = '''
python3 ConnectionStatusDispatcher.py type server
    type = 1 ... connected else NOT connected
    server   ... Server Id
    
example:
python3 ConnectionStatusDispatcher.py 1 exam-123

Shows an Connection Icon and some Info. If there is an Pid File found, first it will 
close the the actual showing ConnectionStatus. After that, it will show
the new one. 
'''
    print(msg)
    sys.exit(0)
  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    """
    print(sys.argv)
    if len(sys.argv) != 3:
        print("Argument mismatch...")
        printhelp()
    typ = sys.argv[1]
    s = sys.argv[2]
    """
    typ = 1
    s = "1234"

    status = ConnectionStatus()     
    status.setServerID(s)  
    status.setType(typ)
    status.show()
    
    app.exec_()
