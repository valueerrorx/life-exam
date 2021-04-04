#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess

# Debugging Stuff, set Name of Client and a fix Pin Code
# set both empty, then we are NOT debugging


# DEBUG OFF
DEBUG_ID = ""
DEBUG_PIN = ""
DEBUG_SHOW_NETWORKTRAFFIC = False

DEBUG_ID = "TestUser"
DEBUG_PIN = "1234"
DEBUG_SHOW_NETWORKTRAFFIC = True


# these apps will try to autosave your work before "abgabe" via xdotool or qdbus
SAVEAPPS = ['calligrawords', 'calligrasheets', 'writer', 'kate',
            'unbenannt', 'geogebra', 'calc', 'spreadsheets', 'wxmaxima']

# which apps must not be listed in apps-list you will provide during EXAM
BLACKLIST_APPS = ["LIFE Student", "LIFE Teacher", "EXAM"]
# During EXAM, which Apps will be visible on Desktop
# you find them in DATA/starter/
EXAM_DESKTOP_APPS = ["Exam Student.desktop", "STOP.desktop", "GeoGebra.desktop"]

# in which directory are datas from clients are stored
DELIVERY_DIRECTORY = "ABGABE/"

# Web Server Root Directory
WEB_ROOT = "/var/www/html/"
# Subdirectory to Geogebra
GEOGEBRA_PATH = "geogebra"


# DON'T CHANGE ==========================================================================================================
SERVER_IP = "localhost"
SERVER_PORT = 11411   # according to wikipedia and IANA no other service uses this port.. so this is ours ;)

# Heartbeat Section
HEARTBEAT_INTERVALL = 10     # sec
HEARTBEAT_START_AFTER = 5   # sec
MAX_HEARTBEAT_FAILS = 3     # maximum number of Heartbeats missing, until a Client is marked as offline
MAX_HEARTBEAT_KICK = 8      # maximum number of Heartbeats missing, until a Client is removed


# find username and set user home directory
USER = subprocess.check_output("logname", shell=True).rstrip().decode()
USER_HOME_DIR = os.path.join("/home", str(USER))
WORK_DIRECTORY = os.path.join(USER_HOME_DIR, ".life/EXAM")

# work directory for client and server  - absolute paths
SCRIPTS_DIRECTORY = os.path.join(WORK_DIRECTORY, "scripts")
EXAMCONFIG_DIRECTORY = os.path.join(WORK_DIRECTORY, "EXAMCONFIG")

SHOTS = "screenshots"
UNZIP = "unzip"
ZIP = "zip"

CLIENTFILES_DIRECTORY = os.path.join(WORK_DIRECTORY, "CLIENT")
CLIENTSCREENSHOT_DIRECTORY = os.path.join(CLIENTFILES_DIRECTORY, SHOTS)
CLIENTUNZIP_DIRECTORY = os.path.join(CLIENTFILES_DIRECTORY, UNZIP)
CLIENTZIP_DIRECTORY = os.path.join(CLIENTFILES_DIRECTORY, ZIP)

SERVERFILES_DIRECTORY = os.path.join(WORK_DIRECTORY, "SERVER")
SERVERSCREENSHOT_DIRECTORY = os.path.join(SERVERFILES_DIRECTORY, SHOTS)
SERVERUNZIP_DIRECTORY = os.path.join(SERVERFILES_DIRECTORY, UNZIP)
SERVERZIP_DIRECTORY = os.path.join(SERVERFILES_DIRECTORY, ZIP)

SHARE_DIRECTORY = os.path.join(USER_HOME_DIR, "SHARE")
PRINTERCONFIG_DIRECTORY = "/etc/cups"

# (this should be the config file that is then transferred to the clients and used for the exam desktop)
PLASMACONFIG = os.path.join(EXAMCONFIG_DIRECTORY, "lockdown/plasma-EXAM")

# relative paths
DATA_DIRECTORY = "./DATA"
