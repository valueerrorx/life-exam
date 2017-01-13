#! /usr/bin/env python
# -*- coding: utf-8 -*-
# STUDENT - CLIENT #
import os
from twisted.internet import reactor, protocol, stdio, defer
from twisted.protocols import basic
from common import *



SERVER_IP = "localhost"
SERVER_PORT = 5000
FILES_DIRECTORY = "./FILESCLIENT/"




class MyClientProtocol(basic.LineReceiver):
      
    def __init__(self,factory):
        self.factory = factory
        self.delimiter = '\n'

    #twisted
    def connectionMade(self):
        self.buffer = []
        self.file_handler = None
        self.file_data = ()
        print 'Connected to the server'

    #twisted
    def connectionLost(self, reason):
        self.file_handler = None
        self.file_data = ()
        print 'Connection to the server has been lost'
        #reactor.stop()  #this would terminate the connection - even if ReconnectingClientFactory would normally try to re-establish the connection

    #twisted
    def rawDataReceived(self, data):
        filename = self.file_data[3]
        file_path = os.path.join(self.factory.files_path, filename)
        
        print 'Receiving file chunk (%d KB)' % (len(data))
        
        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')
            
        if data.endswith('\r\n'):
            # Last chunk
            data = data[:-2]
            self.file_handler.write(data)
            self.setLineMode()
            
            self.file_handler.close()
            self.file_handler = None
            
            if validate_file_md5_hash(file_path, self.file_data[4]):
                print 'File %s has been successfully transfered and saved' % (filename)
            else:
                os.unlink(file_path)
                print 'File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename)
        else:
            self.file_handler.write(data)


    #twisted
    def lineReceived(self, line):
        if line == 'ENDMSG':
            message = '%s' % ' '.join(map(str, self.buffer))
            self._showDesktopMessage(message)
            self.buffer = []
        
        elif line.startswith('FILETRANSFER'):  # the server wants to get/send file..
            self.setRawMode()   #this is going to be a file transfer - set to raw mode
            self.file_data = clean_and_split_input(line)
            trigger = self.file_data[0]
            task = self.file_data[1]
            filetype = self.file_data[2]
            filename = self.file_data[3]
            file_hash = self.file_data[4]
            
            if task == 'SEND':
                self._sendFile(filename, filetype)

            elif task == 'GET':
                return

        else:
            self.buffer.append(line)
           




    def _sendFile(self, filename, filetype):
        """send a file to the server"""
        
        if filetype == 'SHOT':
            command = "./scripts/screenshot.sh %s" %(filename)
            os.system(command)
            
        self.factory.files = self._get_file_list()  #should probably be generated every time .. in case something changes in the directory
        
        if not filename in self.factory.files:
            print ('filename not found in directory')
            self.setLineMode() 
            self.sendLine('filename not found in client directory') 
            return
        
        print ('Sending file: %s (%d KB)' % (filename, self.factory.files[filename][1] / 1024))
        
        if filetype == 'FILE':
            self.transport.write('FILETRANSFER FILE %s %s\n' % (filename, self.factory.files[filename][2]))     #trigger type filename filehash
        elif filetype == 'SHOT':
            self.transport.write('FILETRANSFER SCREENSHOT %s %s\n' % (filename, self.factory.files[filename][2]))     #trigger type filename filehash
        
        self.setRawMode()
        
        for bytes in read_bytes_from_file(self.factory.files[filename][0]):  #complete filepath as arg
            self.transport.write(bytes)
        
        self.transport.write('\r\n')  #send this to inform the server that the datastream is finished
        self.setLineMode()  # When the transfer is finished, we go back to the line mode 

    
    
    
    def _get_file_list(self):
        """ Returns a list of the files in the specified directory as a dictionary:
            dict['file name'] = (file path, file size, file md5 hash)
        """
        file_list = {}
        for root, subdirs, files in os.walk(self.factory.files_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_size = os.path.getsize(file_path)
                md5_hash = get_file_md5_hash(file_path)
                file_list[filename] = (file_path, file_size, md5_hash)
        return file_list
    
    
    
    
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
    print 'Client started, incoming files will be saved to %s' % (FILES_DIRECTORY)
    reactor.connectTCP(SERVER_IP, SERVER_PORT, MyClientFactory(FILES_DIRECTORY))
    reactor.run()    





