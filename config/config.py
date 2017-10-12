#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess

SERVER_IP = "localhost"
SERVER_PORT = 5000


VERSION = '1.0'

PRESERVE_WORKDIR = False    ## TODO -  wir sollten hier die versions nummer im WORKDIR ablegen und checken und im falle eines updates das workdir mit den neuen files überschreiben - nicht erhalten


# these apps will try to autosave your work before "abgabe" via xdotool
SAVEAPPS = ['calligrawords', 'calligrasheets', 'words', 'sheets', 'writer', 'kate', 'geogebra', 'calc', 'spreadsheets'];

# find username and set user home directory
USER = subprocess.check_output("logname", shell=True).rstrip()
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



SERVER_PIDFILE = os.path.join(WORK_DIRECTORY,'server.pid')

# relative paths
DATA_DIRECTORY = "./DATA"
