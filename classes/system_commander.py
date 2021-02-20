import socket
import os
from config.config import SCRIPTS_DIRECTORY, SHARE_DIRECTORY

# TODO use systemcommander in examclient and add startexam


def show_ip():
    scriptfile = os.path.join(SCRIPTS_DIRECTORY, "gui-getmyip.sh")
    startcommand = "exec %s &" % scriptfile
    os.system(startcommand)


def get_primary_ip():
    """ give the primary IP Adress of the host """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


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
