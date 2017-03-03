#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess

SERVER_IP = "localhost"
SERVER_PORT = 5000

PRESERVE_WORKDIR = True

# these apps will try to autosave your work before "abgabe" via xdotool
SAVEAPPS = ['calligrawords', 'calligrasheets', 'words', 'sheets', 'writer', 'kate', 'geogebra', 'calc', 'spreadsheets'];

# find username and set user home directory
USER = subprocess.check_output("logname", shell=True).rstrip()
USER_HOME_DIR = os.path.join("/home", str(USER))
WORK_DIRECTORY = os.path.join(USER_HOME_DIR, ".life/EXAM")

# work directory sub-dirs
SCRIPTS = "scripts"
EXAMCONFIG = "EXAMCONFIG"
CLIENT = "CLIENT"
SHOTS = "screenshots"
UNZIP = "unzip"
ZIP = "zip"
SERVER = "SERVER"
ABGABE = "ABGABE"




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

ABGABE_DIRECTORY = os.path.join(USER_HOME_DIR, ABGABE)

SERVER_PIDFILE = os.path.join(WORK_DIRECTORY,'server.pid')

# relative paths
DATA_DIRECTORY = "./DATA"
