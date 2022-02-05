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

#DEBUG_ID = "TestUser"
#DEBUG_PIN = "1234"
#DEBUG_SHOW_NETWORKTRAFFIC = True


# these apps will try to autosave your work before "abgabe" via xdotool or qdbus
"""
SAVEAPPS = ['calligrawords', 'calligrasheets', 'writer', 'kate',
            'unbenannt', 'geogebra', 'calc', 'spreadsheets', 'wxmaxima']
"""

# which apps must not be listed in apps-list you will provide during EXAM
BLACKLIST_APPS = ["LIFE Student", "LIFE Teacher", "EXAM"]
# During EXAM, which Apps will be visible on Desktop
# you find them in DATA/starter/
EXAM_DESKTOP_APPS = ["Exam Student.desktop", "STOP.desktop", "GeoGebra.desktop"]

# in which directory are datas from clients are stored
DELIVERY_DIRECTORY = "ABGABE/"

# DON'T CHANGE ==========================================================================================================
SERVER_IP = "localhost"
SERVER_PORT = 11411   # according to wikipedia and IANA no other service uses this port.. so this is ours ;)

# Heartbeat Section
# be sure to enable in /DATA/scripts/exam-firewall.sh
HEARTBEAT_PORT = 43278
# Clients send Heartbeats in x sec
HEARTBEAT_INTERVALL = 4
# Server checks offline/online clients x sec
HEARTBEAT_CLEANUP = 2
# how long may a client be silent, after that it is marked as zombie x sec
MAX_HEARTBEAT_DELTA_TIME = 120
# how long may a client be silent until removed from Server
MAX_SILENT_TIME_OFf_CLIENT = 2 * MAX_HEARTBEAT_DELTA_TIME

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
