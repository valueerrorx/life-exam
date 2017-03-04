import os

from config.config import *


def show_ip():
    scriptfile = os.path.join(SCRIPTS_DIRECTORY, "gui-getmyip.sh")
    startcommand = "exec %s &" % scriptfile
    os.system(startcommand)


def start_exam():
    scriptfile = os.path.join(EXAMCONFIG_DIRECTORY, "startexam.sh")
    startcommand = "exec %s config &" % scriptfile
    os.system(startcommand)

#TODO use systemcommander in examclient and add startexam EXAM (only CONFIG mode available right now)

def start_hotspot():
    scriptfile = os.path.join(SCRIPTS_DIRECTORY, "gui-activate-lifehotspot-root.sh")
    startcommand = "exec %s &" % scriptfile
    os.system(startcommand)


def copy(source, target):
    copycommand = "sudo cp -r %s %s" % (source, target)
    os.system(copycommand)


def dialog_popup(msg):
    command = "kdialog --passivepopup '%s' 3 2> /dev/null & " % msg
    os.system(command)


def cleanup(folder):
    cleanupcommand = "sudo rm -rf %/* " % folder
    os.system(cleanupcommand)
    cleanuphiddencommand = "sudo rm -rf %/.* " % folder
    os.system(cleanuphiddencommand)

