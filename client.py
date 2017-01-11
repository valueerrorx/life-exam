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
        filename = self.file_data[0]
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
            
            if validate_file_md5_hash(file_path, self.file_data[1]):
                print 'File %s has been successfully transfered and saved' % (filename)
            else:
                os.unlink(file_path)
                print 'File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename)
        else:
            self.file_handler.write(data)


    #twisted
    def lineReceived(self, line):
        if line == 'ENDMSG':
            
            print '%s' % ' '.join(map(str, self.buffer))
            self.buffer = []
        
        elif line.startswith('HASH'):
            # Received a file name and hash, server is sending us a file
            data = clean_and_split_input(line)
            filename = data[1]
            file_hash = data[2]
            self.file_data = (filename, file_hash)
            self.setRawMode()   #this is a file - set to raw mode
        
        elif line.startswith('GETFILE'):  # the server wants a file.. send it !
            self._sendFile(line)
            
            
        else:
            self.buffer.append(line)
           


    def _sendFile(self, line):
        """send a file to the server"""
        try:
            filename = "clientfile.txt"
        except IndexError:
            self.transport.write('Missing filename\n')
            self.transport.write('ENDMSG\n')
            return
        
        if not self.factory.files:
            self.factory.files = self._get_file_list()  #should probably be generated every time .. in case something changes in the directory
            
        if not filename in self.factory.files:
            print ('filename not found in directory')
            self.setLineMode() 
            self.sendLine('filename not found in client directory') 
            return
        
        print ('Sending file: %s (%d KB)' % (filename, self.factory.files[filename][1] / 1024))
        self.transport.write('HASH %s %s\n' % (filename, self.factory.files[filename][2]))
        self.setRawMode()
        
        for bytes in read_bytes_from_file(os.path.join(self.factory.files_path, filename)):
            self.transport.write(bytes)
        
        self.transport.write('\r\n')
        self.setLineMode()  # When the transfer is finished, we go back to the line mode 

    
    def _get_file_list(self):
        """ Returns a list of the files in the specified directory as a dictionary:
            dict['file name'] = (file path, file size, file md5 hash)
        """
        
        file_list = {}
        for filename in os.listdir(self.factory.files_path):
            file_path = os.path.join(self.factory.files_path, filename)
            
            if os.path.isdir(file_path):
                continue
            
            file_size = os.path.getsize(file_path)
            md5_hash = get_file_md5_hash(file_path)

            file_list[filename] = (file_path, file_size, md5_hash)

        return file_list











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





