#! /usr/bin/env python
# -*- coding: utf-8 -*-
# STUDENT - CLIENT #

import os
import sys
import shutil
import zipfile
import time

from twisted.internet import reactor, protocol, stdio, defer
from twisted.protocols import basic
from common import *
from config import *


try:
    SERVER_IP = sys.argv[1] 
    STUDENT_ID = sys.argv[2] 
except:
    print "No IP Address given! Using localhost"
    SERVER_IP = "127.0.0.1"
    STUDENT_ID = "Unknown User"



class MyClientProtocol(basic.LineReceiver):
    def __init__(self,factory):
        self.factory = factory
        self.delimiter = '\n'
        prepareDirectories()  # cleans everything and copies script files 
        
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
                
                if self.file_data[2] == "EXAM":     # initialize exam mode.. unzip and start exam 
                    self._startExam(filename,file_path)
                elif self.file_data[2] == "FILE":
                    #FIXME try if destination already exists - save with timecode
                    shutil.move(file_path, ABGABE_DIRECTORY)
                    fixFilePermissions(ABGABE_DIRECTORY)
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
                    scriptfile = os.path.join(SCRIPTS_DIRECTORY,'screenshot.sh')
                    screenshotfile = os.path.join(CLIENTSCREENSHOT_DIRECTORY,filename)
                    command = "%s %s" %(scriptfile,screenshotfile)
                    os.system(command)
                elif filetype == 'FOLDER':
                    if filename in self.factory.files:  # if folder exists create a zip out of it
                        target_folder = self.factory.files[filename][0] #get full path
                        output_filename = os.path.join(CLIENTZIP_DIRECTORY,filename )  #save location/filename #always save to root dir.
                        shutil.make_archive(output_filename, 'zip', target_folder)   #create zip of folder
                        filename = "%s.zip" %(filename)   #this is the filename of the zip file
                elif filetype == 'ABGABE':
                    self._triggerAutosave()
                    time.sleep(2)   # give it some time to save the document
            
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



    def _triggerAutosave(self):
        """this function uses xdotool to find windows and trigger ctrl+s shortcut on them
            which will show the save dialog the first time and silently save the document the next time
        """
        app_id_list=[]
        for app in SAVEAPPS:
            command = "xdotool search --name %s &" %(app)
            app_ids = subprocess.check_output(command, shell=True).rstrip()
            if app_ids:
                app_ids = app_ids.split('\n')
                for app_id in app_ids:
                    app_id_list.append(app_id)
            
        for application_id in app_id_list:
            command = "xdotool windowactivate %s && xdotool key ctrl+s &" %(application_id)
            os.system(command)
            print "ctrl+s sent to %s" %(application_id)
        
        #try the current active window too in order to catch other applications not in config.py
        command = "xdotool getactivewindow && xdotool key ctrl+s &"
        os.system(command)



    def _sendFile(self, filename, filetype):
        """send a file to the server"""
        self.factory.files = get_file_list(self.factory.files_path)  #rebuild here just in case something changed (zip/screensho created )
        if not filename in self.factory.files:  # if folder exists
            self.sendLine('filename not found in client directory') 
            return

        if filetype == 'FILE':
            self.transport.write('FILETRANSFER FILE %s %s\n' % (filename, self.factory.files[filename][2]))     #trigger type filename filehash
        elif filetype == 'SHOT':
            self.transport.write('FILETRANSFER SCREENSHOT %s %s %s\n' % (filename, self.factory.files[filename][2],STUDENT_ID ))     #trigger type filename filehash ID
        elif filetype == 'FOLDER' or filetype == 'ABGABE' :
            self.transport.write('FILETRANSFER %s %s %s\n' % (filetype, filename, self.factory.files[filename][2]))     #trigger type filename filehash
        else:
            return
        
        self.setRawMode()
        for bytes in read_bytes_from_file(self.factory.files[filename][0]):  #complete filepath as arg
            self.transport.write(bytes)
        self.transport.write('\r\n')  #send this to inform the server that the datastream is finished
        self.setLineMode()  # When the transfer is finished, we go back to the line mode 



    def _startExam(self,filename,file_path):
        """extracts the config folder and starts the startexam.sh script"""
    
        if SERVER_IP != "127.0.0.1":    #testClient running on the same machine
            extract_dir = os.path.join(WORK_DIRECTORY ,filename[:-4])  #extract to unzipDIR / clientID / foldername without .zip (cut last four letters #shutil.unpack_archive(file_path, extract_dir, 'tar')   #python3 only but twisted RPC is not ported to python3 yet
            with zipfile.ZipFile(file_path,"r") as zip_ref:
                zip_ref.extractall(extract_dir)
            os.unlink(file_path)   #delete zip file
            time.sleep(2)
            
            #add current server IP address to firewall exceptions
            ipstore = os.path.join(EXAMCONFIG_DIRECTORY, "EXAM-A-IPS.DB")
            thisexamfile = open(ipstore, 'a+')   #anhängen
            thisexamfile.write("%s\n" % SERVER_IP)
            
            command = "sudo chmod +x %s/startexam.sh &" %(EXAMCONFIG_DIRECTORY)   #make examscritp executable
            os.system(command)
            time.sleep(2)
            startcommand = "sudo %s/startexam.sh &" %(EXAMCONFIG_DIRECTORY)      
            os.system(startcommand)     #start script
        else:
            return   # running on the same machine.. do not start exam mode / do not copy zip content over original
        
        
        
    
    def _showDesktopMessage(self,msg):
        """uses a passivepopup to display messages from the daemon"""
        message = "Exam Server: %s " %(msg)
        command = "sudo -u %s kdialog --title 'EXAM' --passivepopup '%s' 5" %(USER,message)
        os.system(command)














class MyClientFactory(protocol.ReconnectingClientFactory):  # ReconnectingClientFactory tries to reconnect automatically if connection fails
    def __init__(self, files_path):
        self.files_path = files_path
        self.deferred = defer.Deferred()
        self.files = None
        self.failcount = 0
        
    def clientConnectionFailed(self,connector, reason):  # in case of connection problems try 4 times then reshow student gui
        self.failcount += 1
        if self.failcount > 3:
            command = "sudo -u %s kdialog --title 'EXAM' --passivepopup 'Verbindungsaufbau fehlgeschlagen!' 8 &"  %(USER)
            os.system(command)
            command = "python student.py &" 
            os.system(command)
            os._exit(1)
        print('Connection failed. Reason:', reason)
        command = "sudo -u %s kdialog --title 'EXAM' --passivepopup 'Verbindungsaufbau fehlgeschlagen.\nÜberprüfen sie die Netzwerkeinstellungen \nsowie die Server IP Adresse!' 8 &" %(USER)
        os.system(command)
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

        
    def buildProtocol(self, addr):  # http://twistedmatrix.com/documents/12.1.0/api/twisted.internet.protocol.Factory.html#buildProtocol
        return MyClientProtocol(self) 



if __name__ == '__main__':
    print('Connecting to %s on port %s' % (SERVER_IP, SERVER_PORT) )
    reactor.connectTCP(SERVER_IP, SERVER_PORT, MyClientFactory(CLIENTFILES_DIRECTORY))
    reactor.run()    





