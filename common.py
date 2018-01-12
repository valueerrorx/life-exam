#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.

import hashlib
import os
import subprocess

import ipaddress
import shutil

from config.config import *
from random import randint

import datetime
import time

import sys, os, subprocess
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from client.lockscreen import ScreenlockWindow



def lockScreen(client, line):
    """opens lockscreen.py or kills it """
    lines = clean_and_split_input(line)
    # FIXME check if client.app already exists !!
    if lines[0] == "LKS":
        print "locking screen"

        ##check if a serverprocess is running and do not lock screen if any (dirty hack to prevent locking yourself as a teacher when connected at the same time
        #answer = subprocess.Popen(["ps aux|grep server.py|wc -l"],shell=True, stdout=subprocess.PIPE)
        #answer = str(answer.communicate()[0])
        #print answer
        #if not answer == "0":
            #return

        command = "exec sudo -u %s -H qdbus org.kde.kglobalaccel /kglobalaccel blockGlobalShortcuts true" %(USER)
        os.system(command)

        startcommand = "exec sudo -u %s -H python client/lockscreen.py &" %(USER) #kill it if it already exists
        os.system(startcommand)

    else:
        print "closing lockscreen"
        startcommand = "exec sudo pkill -9 -f lockscreen.py &"
        os.system(startcommand)






def generatePin(n):
    """generates a random number in the given length n """
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def checkIfFileExists(filename):
    if os.path.isfile(filename):
        print "file with the same name found"   # since we mount a fat32 partition file and folder with same name are not allowed .. catch that cornercase
        newname = "%s-%s" %(filename, generatePin(6))
        if os.path.isfile(newname):
            checkIfFileExists(newname)
        else:
            os.rename(filename, newname)
            return
    else:
        return


def checkFirewall(firewall_ip_list):
    result = subprocess.check_output("sudo iptables -L |grep DROP|wc -l", shell=True).rstrip()
    print result
    if result != "0":
        print "stopping ip tables"
        scriptfile = os.path.join(SCRIPTS_DIRECTORY, "exam-firewall.sh")
        startcommand = "exec %s stop &" % (scriptfile)
        os.system(startcommand)

    ipstore = os.path.join(EXAMCONFIG_DIRECTORY, "EXAM-A-IPS.DB")
    lines = [line.rstrip('\n') for line in open(ipstore)]


    count = 0
    for i in firewall_ip_list:
        try:
            lineslist = [x.strip() for x in lines[count].split(':')]
            ip = i[0].setText(lineslist[0])
            port = i[1].setText(lineslist[1])
        except IndexError:
            continue
        count += 1



def checkIP(iptest):
    try:
        ip = ipaddress.ip_address(iptest)
        return True
    except ValueError:
        return False
    except:
        return False


def validate_file_md5_hash(file, original_hash):
    """ Returns true if file MD5 hash matches with the provided one, false otherwise. """
    filehash = get_file_md5_hash(file)
    if filehash == original_hash:
        return True

    return False


def get_file_md5_hash(file):
    """ Returns file MD5 hash"""

    md5_hash = hashlib.md5()
    for bytes in read_bytes_from_file(file):
        md5_hash.update(bytes)

    return md5_hash.hexdigest()


def read_bytes_from_file(file, chunk_size=8100):
    """ Read bytes from a file in chunks. """
    with open(file, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)

            if chunk:
                yield chunk
            else:
                break


def clean_and_split_input(input):
    """ Removes carriage return and line feed characters and splits input on a single whitespace. """
    input = input.strip()
    input = input.split()

    return input


def get_file_list(folder):
    """ Returns a list of the files in the specified directory as a dictionary:
            dict['file name'] = (file path, file size, file md5 hash)
        """
    # what if filename or foldername exists twice in tree ??  FIXME => http://stackoverflow.com/a/10665285
    file_list = {}
    for root, subdirs, files in os.walk(folder):
        for filename in files:  # add all files to the list
            file_path = os.path.join(root, filename)
            file_size = os.path.getsize(file_path)
            md5_hash = get_file_md5_hash(file_path)
            file_list[filename] = (file_path, file_size,
                                   md5_hash)  # probably better to use path as index and filename as first value to make sure its unique ?
        for subdir in subdirs:  # add folders to the list
            dir_path = os.path.join(root, subdir)
            file_list[subdir] = (dir_path, 0, 0)
    return file_list


def deleteFolderContent(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path) and the_file != ".stickyfolder":
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def prepareDirectories():
    if not os.path.exists(WORK_DIRECTORY):  # scripts just need to be on a specific location for plasma configfiles
        os.makedirs(WORK_DIRECTORY)
        os.makedirs(CLIENTFILES_DIRECTORY)
        os.makedirs(SERVERFILES_DIRECTORY)
    else:  # cleanup
        deleteFolderContent(CLIENTFILES_DIRECTORY)
        deleteFolderContent(SERVERFILES_DIRECTORY)  # deletes all transferred files from previous session

    os.makedirs(CLIENTSCREENSHOT_DIRECTORY)
    os.makedirs(CLIENTUNZIP_DIRECTORY)
    os.makedirs(CLIENTZIP_DIRECTORY)

    os.makedirs(SERVERSCREENSHOT_DIRECTORY)
    os.makedirs(SERVERUNZIP_DIRECTORY)
    os.makedirs(SERVERZIP_DIRECTORY)

    if not os.path.exists(SHARE_DIRECTORY):
        os.makedirs(SHARE_DIRECTORY)
    else:
        settime = time.time()  # zip does not support filetimes before 1980 .. WTF ??
        os.utime(SHARE_DIRECTORY, (settime,settime))
        

    

    copycommand = "cp -r ./DATA/scripts %s" % (WORK_DIRECTORY)
    os.system(copycommand)

    if not os.path.exists(EXAMCONFIG_DIRECTORY):  # this is important to NOT overwrite an already customized exam desktop stored in the workdirectory on the server
        print "copying default examconfig to workdirectory"
        copycommand = "cp -r ./DATA/EXAMCONFIG %s" % (WORK_DIRECTORY)
        os.system(copycommand)
    else:
        # leave the EXAM-A-IPS.DB alone - it stores firewall information which must not be reset on every update
        # leave lockdown folder as it is to preserve custom changes but always provide a new copy of startexam.sh (could be updated)
        copycommand2 = "cp -r ./DATA/EXAMCONFIG/startexam.sh %s" % (EXAMCONFIG_DIRECTORY)
        os.system(copycommand2)

    fixFilePermissions(WORK_DIRECTORY)
    fixFilePermissions(SHARE_DIRECTORY)



def fixFilePermissions(folder):
    """ FIXME ?? both scripts are running as root 
    in order to be able to start exam mode and survive Xorg restart - therefore all transferred files belong to root"""
    if folder:
        if folder.startswith('/home/'):  # don't EVER change permissions outside of /home/
            print "fixing file permissions"
            chowncommand = "sudo chown -R %s:%s %s" % (USER, USER, folder)
            os.system(chowncommand)
        else:
            print "exam folder location outside of /home/ is not allowed"
    else:
        print "no folder given"


def writePidFile():
    pid = str(os.getpid())

    f = open(SERVER_PIDFILE, 'w+')
    f.write(pid)
    f.close()


def showDesktopMessage(msg):
    """uses a passivepopup to display messages from the daemon"""
    message = "Exam Server: %s " % (msg)
    command = "sudo -u %s kdialog --title 'EXAM' --passivepopup '%s' 5" % (USER, message)
    os.system(command)
