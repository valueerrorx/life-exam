import os

from config.config import *


def show_ip():
    scriptfile = os.path.join(SCRIPTS_DIRECTORY, "gui-getmyip.sh")
    startcommand = "exec %s &" % scriptfile
    os.system(startcommand)


#TODO use systemcommander in examclient and add startexam 

def start_hotspot():
    scriptfile = os.path.join(SCRIPTS_DIRECTORY, "gui-activate-lifehotspot-root.sh")
    startcommand = "exec %s &" % scriptfile
    os.system(startcommand)


def copy(source, target):
    copycommand = "cp -r %s %s" % (source, target)
    os.system(copycommand)


def dialog_popup(msg):
    command = "kdialog --passivepopup '%s' 3 2> /dev/null & " % msg
    os.system(command)


def cleanup(folder):
    cleanupcommand = "rm -rf %s/* " % folder
    os.system(cleanupcommand)
    cleanuphiddencommand = "rm -rf %s/.* " % folder
    os.system(cleanuphiddencommand)


def mountabgabe():
    mountcommand = "mount -o umask=002,uid=1000,gid=1000 /dev/disk/by-label/SHARE %s" % SHARE_DIRECTORY
    os.system(mountcommand)
