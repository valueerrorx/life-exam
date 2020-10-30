#! /usr/bin/env python3

import os
import shutil
import subprocess
import zipfile
import datetime
import pwd
import dbus
from config.config import SHARE_DIRECTORY
from classes import mutual_functions
from classes.Thread_Countdown import Thread_Countdown
from time import sleep
from classes.psUtil import PsUtil


def write_dbus_env_OS():
    """ capture the output of dbus-launch, parse the values, and use os.environ to write them to the environment """
    p = subprocess.Popen('dbus-launch', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for item in p.stdout:
        # decode byte to ...
        item = item.decode('UTF-8')
        sp = item.split('=', 1)
        os.environ[sp[0]] = sp[1][:-1]    
        
def export_to_shell():
    full_cmd =""
    p = subprocess.Popen('dbus-launch', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for item in p.stdout:
        # decode byte to ...
        item = item.decode('UTF-8')
        sp = item.split('=', 1)
        cmd ="export %s=\"%s\"" % (sp[0], sp[1][:-1])
        full_cmd += "%s && " % cmd
    return full_cmd

                
def demote(user_name, user_uid, user_gid):
    """Pass the function 'set_ids' to preexec_fn, rather than just calling
    setuid and setgid. This will change the ids for that subprocess only"""
    def set_ids():
        try:
            print("starting")
            #print ("uid, gid = %d, %d" % (os.getuid(), os.getgid()))
            #print (os.getgroups())
            # initgroups must be run before we lose the privilege to set it!
            os.initgroups(user_name, user_gid)
            #print("initgroups")
            os.setgid(user_gid)
            # this must be run last
            os.setuid(user_uid)
            #print("finished demotion")
            #print ("uid, gid = %d, %d" % (os.getuid(), os.getgid()))
            #print (os.getgroups())
            
            
        except Exception as error:
            print(error)
        
    return set_ids

def runAndWaittoFinishTest(cmd):
    """Runs a subprocess, and waits for it to finish"""
    """
    3 things we can do to not Use an X Server with DBus
    - use the system bus
    - use dbus-launch to create a bus and connect to that, of course the other clients must use the same bus to be useful
    - find out the dbus address for the existing bus you want to use.
    
    dbus-launch 
DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-M0Wnnf6pyv,guid=f8a747b3da797c7eba247c4d5f92ba1f
DBUS_SESSION_BUS_PID=5594
DBUS_SESSION_BUS_WINDOWID=119537665

    """

    
    ENV = "DBUS_SESSION_BUS_ADDRESS DBUS_SESSION_BUS_PID DBUS_SESSION_BUS_WINDOWID"

    
    
    stderr = ""
    stdout = ""
    user_name = "student"
    uid = pwd.getpwnam(user_name).pw_uid
    guid = pwd.getpwnam(user_name).pw_gid
    
    print(cmd)
    exported_cmd = "%s%s" % (export_to_shell(), cmd)
    print(exported_cmd)
    
    
    
    proc = subprocess.Popen(exported_cmd, 
                            shell=True, 
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            # bufsize=0, 
                            #preexec_fn=demote(user_name, uid, guid)
                            #env={'env_keep': ENV}
                            )
    for line in iter(proc.stderr.readline, b''):
        stderr += line.decode()

    for line in iter(proc.stdout.readline, b''):
        stdout += line.decode()
    # Wait for process to terminate and set the returncode attribute
    proc.communicate()
    
    return [proc.returncode, stderr, stdout]

def runAndWaittoFinish(cmd):
    """Runs a subprocess, and waits for it to finish"""
    """
    3 things we can do to not Use an X Server with DBus
    - use the system bus
    - use dbus-launch to create a bus and connect to that, of course the other clients must use the same bus to be useful
    - find out the dbus address for the existing bus you want to use.
    """
    stderr = ""
    stdout = ""
    proc = subprocess.Popen(cmd, 
                            shell=True, 
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            # bufsize=0, 
                            #preexec_fn=demote(user_name, uid, guid)
                            #env={'env_keep': ENV}
                            )
    for line in iter(proc.stderr.readline, b''):
        stderr += line.decode()

    for line in iter(proc.stdout.readline, b''):
        stdout += line.decode()
    # Wait for process to terminate and set the returncode attribute
    proc.communicate()
    
    return [proc.returncode, stderr, stdout]

def _getArrayAsString(arr):
    string = ""
    for val in arr:
        string += val + " "
    return string

def triggerAutosave():
    """
    this function uses xdotool to find windows and trigger ctrl + s shortcut on them
    which will show the save dialog the first time and silently save the document the next time
    """        
    app_id_list = []
    
    
    # these programs are qdbus enabled therefore we can trigger "save" directly from commandline
    app_str = "Calligrawords/Calligrasheets/Kate"
    savetrigger = "file_save"
    app="calligrawords"
    try:
        command = "pidof %s" % (app)
        # data = [exitcode, err, out]
        data = subprocess.check_output(command, shell=True).decode().rstrip()
        # clean               
        p = data.replace('\n', '')
        pids = p.split(' ')
        print("%s Pids: %s" % (app_str, _getArrayAsString(pids)))
        for pid in pids:
            qdbuscommand = "qdbus org.kde.%s-%s /%s/MainWindow_1/actions/%s trigger" % (app, pid, app, savetrigger)
            print(qdbuscommand)
            data = runAndWaittoFinish(qdbuscommand)
            print(data)
    except Exception as error:
        print(error)
        print("%s not running" % app_str)

"""  
print("Anzahl an Files in %s" % SHARE_DIRECTORY)
dir = SHARE_DIRECTORY
files_count = 0
dir_count = 0
for root, dirs, files in os.walk(dir, topdown=False):
    for name in files:
        print(os.path.join(root, name))
    for name in dirs:
        print(os.path.join(root, name))
    files_count = len(files)
    dir_count = len(dirs)
print(files_count)
"""

"""
def gurke(msg):
    print("Yeahhh %s" % msg)
    pass

countdown_thread = Thread_Countdown()
countdown_thread.setTime(5)
countdown_thread.finished_signal.connect()
countdown_thread.start()
sleep(10)
sleep(20)
"""

"""
triggerAutosave()
print(os.environ)
write_dbus_env_OS()
print(os.environ)
print(os.environ['DISPLAY'])

print(export_to_shell())
"""

# bus = dbus.SystemBus()
# session = bus.get_object("org.kde.calligrawords", "/calligrawords/MainWindow_1/actions")

                                                                                 
  
util = PsUtil()
pid = util.GetProcessByName("Test")
print(pid)




