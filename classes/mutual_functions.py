#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Thomas Michael Weissel
#
# This software may be modified and distributed under the terms
# of the GPLv3 license.  See the LICENSE file for details.

import hashlib
import logging
import os
import subprocess
import webbrowser

from pathlib import Path
from config.config import SCRIPTS_DIRECTORY, EXAMCONFIG_DIRECTORY,\
    WORK_DIRECTORY, CLIENTFILES_DIRECTORY, SERVERFILES_DIRECTORY,\
    CLIENTSCREENSHOT_DIRECTORY, CLIENTUNZIP_DIRECTORY, CLIENTZIP_DIRECTORY,\
    SERVERSCREENSHOT_DIRECTORY, SERVERUNZIP_DIRECTORY, SERVERZIP_DIRECTORY,\
    SHARE_DIRECTORY, USER
import stat

logger = logging.getLogger(__name__)

import ipaddress
import shutil

from random import randint

import time


def generatePin(n):
    """generates a random number in the given length n """
    range_start = 10**(n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


def checkIfFileExists(filename):
    if os.path.isfile(filename):
        logger.info("file with the same name found")   # since we mount a fat32 partition file and folder with same name are not allowed .. catch that cornercase
        newname = "%s-%s" % (filename, generatePin(6))
        if os.path.isfile(newname):
            checkIfFileExists(newname)
        else:
            os.rename(filename, newname)
            return
    else:
        return


def checkFirewall(firewall_ip_list):
    result = subprocess.check_output("iptables -L |grep DROP|wc -l", shell=True).rstrip()
    if result != "0":
        scriptfile = os.path.join(SCRIPTS_DIRECTORY, "exam-firewall.sh")
        startcommand = "exec %s stop &" % (scriptfile)
        os.system(startcommand)

    ipstore = os.path.join(EXAMCONFIG_DIRECTORY, "EXAM-A-IPS.DB")
    lines = [line.rstrip('\n') for line in open(ipstore)]

    count = 0
    for i in firewall_ip_list:
        try:
            lineslist = [x.strip() for x in lines[count].split(':')]
            i[0].setText(lineslist[0])
            i[1].setText(lineslist[1])
        except IndexError:
            continue
        count += 1


def checkIP(iptest):
    try:
        ipaddress.ip_address(iptest)
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
    for b in read_bytes_from_file(file):
        md5_hash.update(b)

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


def clean_and_split_input(input_str):
    """ Removes carriage return and line feed characters and splits input on a single whitespace. """
    input_str = input_str.strip()
    return input_str.split()


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
            logger.error(e)


def prepareDirectories():
    # rootDir of Application
    rootDir = Path(__file__).parent.parent

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
        os.utime(SHARE_DIRECTORY, (settime, settime))

    copycommand = "cp -r %s/DATA/scripts %s" % (rootDir, WORK_DIRECTORY)
    os.system(copycommand)

    if not os.path.exists(EXAMCONFIG_DIRECTORY):  # this is important to NOT overwrite an already customized exam desktop stored in the workdirectory on the server
        logger.info("Copying default examconfig to workdirectory")
        copycommand = "cp -r %s/DATA/EXAMCONFIG %s" % (rootDir, WORK_DIRECTORY)
        os.system(copycommand)
    else:
        # leave the EXAM-A-IPS.DB alone - it stores firewall information which must not be reset on every update
        # leave lockdown folder (plasma-EXAM, etc.) as it is to preserve custom changes
        # but always provide a new copy of startexam.sh (will be updated more frequently)
        logger.info("Old examconfig found - keeping old config")  # friendly reminder to the devs ;-)
        copycommand2 = "cp -r %s/DATA/EXAMCONFIG/startexam.sh %s" % (rootDir, EXAMCONFIG_DIRECTORY)
        os.system(copycommand2)

    fixFilePermissions(WORK_DIRECTORY)
    fixFilePermissions(SHARE_DIRECTORY)


def fixFilePermissions(folder):
    """ FIXME ?? both scripts are running as root
    in order to be able to start exam mode and survive Xorg restart - therefore all transferred files belong to root
    """
    if folder:
        if folder.startswith('/home/'):  # don't EVER change permissions outside of /home/
            if folder == WORK_DIRECTORY:
                chowncommand = "find %s ! -name \"server.pid\" | xargs -I {} chown %s:%s {}" % (folder, USER, USER)
            else:
                chowncommand = "chown -R %s:%s %s" % (USER, USER, folder)

            os.system(chowncommand)
        else:
            logger.error("Exam folder location outside of /home/ is not allowed")
    else:
        logger.error("no folder given")


def changePermission(path, octal):
    """
    change the permission to ... see man 2 open
    stat.S_ISUID − Set user ID on execution.
    stat.S_ISGID − Set group ID on execution.
    stat.S_ENFMT − Record locking enforced.
    stat.S_ISVTX − Save text image after execution.
    stat.S_IREAD − Read by owner.
    stat.S_IWRITE − Write by owner.
    stat.S_IEXEC − Execute by owner.
    stat.S_IRWXU − Read, write, and execute by owner.
    stat.S_IRUSR − Read by owner.
    stat.S_IWUSR − Write by owner.
    stat.S_IXUSR − Execute by owner.
    stat.S_IRWXG − Read, write, and execute by group.
    stat.S_IRGRP − Read by group.
    stat.S_IWGRP − Write by group.
    stat.S_IXGRP − Execute by group.
    stat.S_IRWXO − Read, write, and execute by others.
    stat.S_IROTH − Read by others.
    stat.S_IWOTH − Write by others.
    stat.S_IXOTH − Execute by others.
    """
    st = os.stat(path)
    if octal == "777":
        mode = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO
    os.chmod(path, st.st_mode | mode)


def writePidFile():
    file = os.path.join(WORK_DIRECTORY, 'server.pid')
    pid = str(os.getpid())

    f = open(file, 'w+')
    f.write(pid)
    f.close()
    changePermission(file, "777")


def deletePidFile():
    file = os.path.join(WORK_DIRECTORY, 'server.pid')
    os.remove(file)


def writeLockFile():
    """ lock File indicates that client has started EXAM Mode """
    file = os.path.join(WORK_DIRECTORY, 'client.lock')

    f = open(file, 'w+')
    f.write("Client has started EXAM Mode")
    f.close()
    changePermission(file, "777")


def lockFileExists():
    my_file = Path(WORK_DIRECTORY).joinpath('client.lock')
    if my_file.is_file():
        # file exists
        return True
    else:
        return False


def createFakeZipFile():
    """ Create an empty zip File, its a dummy """
    my_file = Path(CLIENTZIP_DIRECTORY).joinpath('dummy')
    # create dummy dir to zip
    my_path = Path(CLIENTZIP_DIRECTORY).joinpath('dummydir')
    my_path.mkdir()
    shutil.make_archive(my_file, 'zip', my_path)


def showDesktopMessage(msg):
    """uses a passivepopup to display messages from the daemon"""
    message = "Exam Server: %s " % (msg)
    command = "runuser -u %s -- kdialog --title 'EXAM' --passivepopup '%s' 5 " % (USER, message)
    os.system(command)


def openFileManager(path):
    """ cross OS """
    if os.path.exists(path):
        webbrowser.open('file:///' + path)
