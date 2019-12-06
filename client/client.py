#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.

from PyQt5 import uic, QtWidgets

import time
import sys
import os
import subprocess
from pathlib import Path
# add application root to python path for imports at position 0 
sys.path.insert(0, Path(__file__).parent.parent.as_posix())
#Logging System
from config.logger import configure_logging
from config.config import *

from client.ui.ClientUI import *
from client.resources.MulticastLifeClient import *

#from PyQt5.QtGui import QPixmap
#from PyQt5.QtGui import QIcon, QColor, QRegExpValidator
#from PyQt5.QtCore import QRegExp, Qt

application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, application_path)

import qt5reactor


# ATTENTION
# we need elevated rights for exam mode ! 
# we can stick to sudo at the beginning (starting this script) and then default to start everything without sudo 
# but we need to add env_keep += PYTHONPATH  to sudoers file  (sudo visudo) otherwise twistd will not find the exam plugin
# in order to set PYTHONPATH in the first place we add  
# PYTHONPATH="/home/student/.life/applications/life-exam" to /etc/environment or .bashrc


if __name__ == '__main__':
    #Set the Logging
    rootdir = Path(__file__).parent.parent.as_posix()
    configure_logging('%s' % (rootdir), False)       #True is Server

    app = QtWidgets.QApplication(sys.argv)
    dialog = ClientDialog()
    dialog.ui.show()
    qt5reactor.install()  # imported from file and needed for Qt to function properly in combination with twisted reactor

    from twisted.internet import reactor
    
    reactor.listenMulticast(8005, MulticastLifeClient(), listenMultiple=True)
    sys.exit(app.exec_())
