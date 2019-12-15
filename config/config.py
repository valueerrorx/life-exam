#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.

import os
import subprocess


SERVER_IP = "localhost"
SERVER_PORT = 11411   #according to wikipedia and IANA no other service uses this port.. so this is ours ;)

VERSION = '3.1'

#Debugging Stuff, set Name of Client and a fix Pin Code
#if empty, then we are NOT debugging
DEBUG_ID="TestUser"
DEBUG_PIN="1234"
DEBUG_SHOW_NETWORKTRAFFIC=False

SCREENSHOTINTERVALL = 30

# these apps will try to autosave your work before "abgabe" via xdotool or qdbus 
SAVEAPPS = ['calligrawords', 'calligrasheets', 'words', 'sheets', 'writer', 'kate', 'unbenannt', 'geogebra', 'calc', 'spreadsheets'];

# find username and set user home directory
USER = subprocess.check_output("logname", shell=True).rstrip().decode()
USER_HOME_DIR = os.path.join("/home", str(USER))
WORK_DIRECTORY = os.path.join(USER_HOME_DIR, ".life/EXAM")

# work directory sub-dirs
#TODO wo werden diese gebraucht? es handelt sich ausserdem bei nachstehender liste nicht nur um subs sondern auch um subsubs - SHARE ist gar nicht dort
SCRIPTS = "scripts"
EXAMCONFIG = "EXAMCONFIG"
CLIENT = "CLIENT"
SHOTS = "screenshots"
UNZIP = "unzip"
ZIP = "zip"
SERVER = "SERVER"

SHARE = "SHARE"   # im home verzeichnis wird der ordner SHARE angelegt - dieser dient als arbeitsverzeichnis für lehrer und schüler


# work directory for client and server  - absolute paths 

SCRIPTS_DIRECTORY = os.path.join(WORK_DIRECTORY, SCRIPTS)
EXAMCONFIG_DIRECTORY = os.path.join(WORK_DIRECTORY, EXAMCONFIG)

CLIENTFILES_DIRECTORY = os.path.join(WORK_DIRECTORY, CLIENT)
CLIENTSCREENSHOT_DIRECTORY = os.path.join(CLIENTFILES_DIRECTORY, SHOTS)
CLIENTUNZIP_DIRECTORY = os.path.join(CLIENTFILES_DIRECTORY, UNZIP)
CLIENTZIP_DIRECTORY = os.path.join(CLIENTFILES_DIRECTORY, ZIP)

SERVERFILES_DIRECTORY = os.path.join(WORK_DIRECTORY, SERVER)
SERVERSCREENSHOT_DIRECTORY = os.path.join(SERVERFILES_DIRECTORY, SHOTS)
SERVERUNZIP_DIRECTORY = os.path.join(SERVERFILES_DIRECTORY, UNZIP)
SERVERZIP_DIRECTORY = os.path.join(SERVERFILES_DIRECTORY, ZIP)

SHARE_DIRECTORY = os.path.join(USER_HOME_DIR, SHARE)
PRINTERCONFIG_DIRECTORY = "/etc/cups"

PLASMACONFIG = os.path.join(EXAMCONFIG_DIRECTORY,"lockdown/plasma-EXAM") # (this should be the config file that is then transferred to the clients and used for the exam desktop)


# relative paths
DATA_DIRECTORY = "./DATA"
