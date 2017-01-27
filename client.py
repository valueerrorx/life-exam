#! /usr/bin/env python
# -*- coding: utf-8 -*-
# STUDENT - CLIENT #

import os
import shutil
import zipfile
import time

from twisted.internet import reactor, protocol, stdio, defer
from twisted.protocols import basic
from common import *
from config import *




class MyClientProtocol(basic.LineReceiver):
      
    def __init__(self,factory):
        self.factory = factory
        self.delimiter = '\n'
        deleteFolderContent(CLIENTSCREENSHOT_DIRECTORY)
        deleteFolderContent(CLIENTZIP_DIRECTORY)
        deleteFolderContent(CLIENTUNZIP_DIRECTORY)
        deleteFolderContent(CLIENT_EXAMCONFIG_DIRECTORY)
        
        
        if not os.path.exists(SOURCE_DIRECTORY):   #some scripts just need to be on a specific location otherwise plasma configfiles will not work
            os.makedirs(SOURCE_DIRECTORY)
            scriptsdirectory = os.path.join(SOURCE_DIRECTORY,"scripts/")
            os.makedirs(scriptsdirectory)
        shutil.copy2("./scripts/stopexam.sh", "/home/student/.life/EXAM/scripts/stopexam.sh")    #.life/EXAM/ is going to be the root directory of the application (all life stuff will eventually go to .life (for now make sure this file is there)
        
    #twisted
    def connectionMade(self):
        self.buffer = []
        self.file_handler = None
        self.file_data = ()
        print('Connected to the server')

    #twisted
    def connectionLost(self, reason):
        self.file_handler = None
        self.file_data = ()
        print('Connection to the server has been lost')
        self._showDesktopMessage('Connection to the server has been lost')
        #reactor.stop()  #this would terminate the connection - even if ReconnectingClientFactory would normally try to re-establish the connection

    #twisted
    def rawDataReceived(self, data):
        filename = self.file_data[3]
        file_path = os.path.join(self.factory.files_path, filename)
        print('Receiving file chunk (%d KB)' % (len(data)) )
        
        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')
            
        if data.endswith('\r\n'): # Last chunk
            data = data[:-2]
            self.file_handler.write(data)
            self.file_handler.close()
            self.file_handler = None
            self.setLineMode()
            
            if validate_file_md5_hash(file_path, self.file_data[4]):
                print('File %s has been successfully transfered and saved' % (filename) )
                
                # initialize exam mode.. unzip and start exam 
                if self.file_data[2] == "EXAM":   
                    extract_dir = os.path.join(CLIENTFILES_DIRECTORY ,filename[:-4])  #extract to unzipDIR / clientID / foldername without .zip (cut last four letters #shutil.unpack_archive(file_path, extract_dir, 'tar')   #python3 only but twisted RPC is not ported to python3 yet
                    with zipfile.ZipFile(file_path,"r") as zip_ref:
                        zip_ref.extractall(extract_dir)
                    os.unlink(file_path)   #delete zip file
                    time.sleep(2)
                    
                    command = "sudo chmod +x %s/startexam.sh &" %(CLIENT_EXAMCONFIG_DIRECTORY)   #make examscritp executable
                    os.system(command)
                    startcommand = "sudo %s/startexam.sh &" %(CLIENT_EXAMCONFIG_DIRECTORY)      
                    print startcommand
                    
                    if SERVER_IP != "localhost":    #testClient running on the same machine
                        os.system(startcommand)     #start script
                
            else:
                os.unlink(file_path)
                print('File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename) )
        else:
            self.file_handler.write(data)


    #twisted
    def lineReceived(self, line):
        if line == 'ENDMSG':
            message = '%s' % ' '.join(map(str, self.buffer))
            self._showDesktopMessage(message)
            self.buffer = []
        
        elif line.startswith('FILETRANSFER'):  # the server wants to get/send file..
            self.file_data = clean_and_split_input(line)
            self.factory.files = get_file_list(self.factory.files_path)
            trigger = self.file_data[0]
            task = self.file_data[1]
            filetype = self.file_data[2]
            filename = self.file_data[3]
            file_hash = self.file_data[4]
            
            if task == 'SEND':
                if filetype == 'SHOT':  # files need to be created first
                    command = "./scripts/screenshot.sh %s" %(filename)
                    os.system(command)
                elif filetype == 'FOLDER':
                    if filename in self.factory.files:  # if folder exists create a zip out of it
                        target_folder = self.factory.files[filename][0] #get full path
                        output_filename = os.path.join(CLIENTZIP_DIRECTORY,filename )  #save location/filename #always save to root dir.
                        shutil.make_archive(output_filename, 'zip', target_folder)   #create zip of folder
                        filename = "%s.zip" %(filename)   #this is the filename of the zip file
                elif filetype == 'ABGABE':
                    target_folder = ABGABE_DIRECTORY
                    output_filename = os.path.join(CLIENTZIP_DIRECTORY,filename )  #save location/filename #always save to root dir.
                    shutil.make_archive(output_filename, 'zip', target_folder)   #create zip of folder
                    filename = "%s.zip" %(filename)   #this is the filename of the zip file
                
                self._sendFile(filename, filetype)
            elif task == 'GET':
                self.setRawMode()   #you are getting a file - set to raw mode (bytes instead of lines)
                return
        else:
            self.buffer.append(line)



    def _sendFile(self, filename, filetype):
        """send a file to the server"""
        self.factory.files = get_file_list(self.factory.files_path)  #rebuild here just in case something changed (zip/screensho created )
        if not filename in self.factory.files:  # if folder exists
            self.sendLine('filename not found in client directory') 
            return

        if filetype == 'FILE':
            self.transport.write('FILETRANSFER FILE %s %s\n' % (filename, self.factory.files[filename][2]))     #trigger type filename filehash
        elif filetype == 'SHOT':
            self.transport.write('FILETRANSFER SCREENSHOT %s %s\n' % (filename, self.factory.files[filename][2]))     #trigger type filename filehash
        elif filetype == 'FOLDER' or filetype == 'ABGABE' :
            self.transport.write('FILETRANSFER FOLDER %s %s\n' % (filename, self.factory.files[filename][2]))     #trigger type filename filehash
        else:
            return
        
        self.setRawMode()
        for bytes in read_bytes_from_file(self.factory.files[filename][0]):  #complete filepath as arg
            self.transport.write(bytes)
        self.transport.write('\r\n')  #send this to inform the server that the datastream is finished
        self.setLineMode()  # When the transfer is finished, we go back to the line mode 

    
    
    def _showDesktopMessage(self,msg):
        message = "Exam Server: %s " %(msg)
        command = "kdialog --title 'EXAM' --passivepopup '%s' 5" %(message)
        os.system(command)














class MyClientFactory(protocol.ReconnectingClientFactory):  # ReconnectingClientFactory tries to reconnect automatically if connection fails
    def __init__(self, files_path):
        self.files_path = files_path
        self.deferred = defer.Deferred()
        self.files = None
        
    def buildProtocol(self, addr):  # http://twistedmatrix.com/documents/12.1.0/api/twisted.internet.protocol.Factory.html#buildProtocol
        return MyClientProtocol(self) 

if __name__ == '__main__':
    print('Connecting to %s on port %s' % (SERVER_IP, SERVER_PORT) )
    reactor.connectTCP(SERVER_IP, SERVER_PORT, MyClientFactory(CLIENTFILES_DIRECTORY))
    reactor.run()    





