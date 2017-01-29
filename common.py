#! /usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import os
import ipaddress
import shutil

from config import *


def checkFirewall(self):
    result = os.system("sudo iptables -L |grep DROP|wc -l")
    if result != 0:
        print "stopping ip tables"
        os.system("./scripts/exam-firewall.sh stop &") 
    
    ipstore = os.path.join(EXAMCONFIG_DIRECTORY, "EXAM-A-IPS.DB")
    lines = [line.rstrip('\n') for line in open(ipstore)]
    
    ipfields = [self.ui.firewall1,self.ui.firewall2,self.ui.firewall3,self.ui.firewall4]
    count = 0
    for i in ipfields:
        try:
            ip = i.setText(lines[count])
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

    if get_file_md5_hash(file) == original_hash:
        return True
        
    return False



def get_file_md5_hash(file):
    """ Returns file MD5 hash"""
    
    md5_hash = hashlib.md5()
    for bytes in read_bytes_from_file(file):
        md5_hash.update(bytes)
        
    return md5_hash.hexdigest()



def read_bytes_from_file(file, chunk_size = 8100):
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
    input = input.split(' ')
        
    return input



def get_file_list(folder):
        """ Returns a list of the files in the specified directory as a dictionary:
            dict['file name'] = (file path, file size, file md5 hash)
        """
        # what if filename or foldername exists twice in tree ??  FIXME
        file_list = {}
        for root, subdirs, files in os.walk(folder):
            for filename in files:  # add all files to the list
                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                md5_hash = get_file_md5_hash(file_path)
                file_list[filename] = (file_path, file_size, md5_hash)  #probably better to use path as index and filename as first value
            for subdir in subdirs:  # add folders to the list
                dir_path = os.path.join(root,subdir)
                file_list[subdir] = (dir_path, 0, 0)
        return file_list
    
    
    
def deleteFolderContent(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path) and the_file != ".stickyfolder":
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)



def prepareDirectories():
   
    if not os.path.exists(WORK_DIRECTORY):   #some scripts just need to be on a specific location otherwise plasma configfiles will not work
        os.makedirs(WORK_DIRECTORY)
        os.makedirs(CLIENTFILES_DIRECTORY)
        os.makedirs(SERVERFILES_DIRECTORY)
    else:   #cleanup
        deleteFolderContent(CLIENTFILES_DIRECTORY)
        deleteFolderContent(SERVERFILES_DIRECTORY)
        
    os.makedirs(CLIENTSCREENSHOT_DIRECTORY)
    os.makedirs(CLIENTUNZIP_DIRECTORY)
    os.makedirs(CLIENTZIP_DIRECTORY)
    
    os.makedirs(SERVERSCREENSHOT_DIRECTORY)
    os.makedirs(SERVERUNZIP_DIRECTORY)
    os.makedirs(SERVERZIP_DIRECTORY)
    
    
    #FIXME  bei jedem start wird EXAMCONFIG ins workdirectory kopiert - neu gestalteter exam desktop wird überschrieben
    # die änderungen werden nicht ins data verzeichnis zurückgeführt
  
    copycommand = "sudo cp -r ./DATA/scripts %s" %(WORK_DIRECTORY)
    os.system(copycommand)
    
    if not os.path.exists(EXAMCONFIG_DIRECTORY):
        print "copying examconfig to workdirectory"
        copycommand = "sudo cp -r ./DATA/EXAMCONFIG %s" %(WORK_DIRECTORY)
        os.system(copycommand)
   
   #fix permissions
    chowncommand = "sudo chown -R student:student %s" %(WORK_DIRECTORY)
    os.system(chowncommand)


