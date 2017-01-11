#! /usr/bin/env python
# -*- coding: utf-8 -*-
# TEACHER - SERVER #
import qt5reactor
import os
import sys
import ipaddress
import datetime
from twisted.internet import protocol
from twisted.protocols import basic
from common import *
from PyQt5 import uic, QtWidgets
from PyQt5.QtGui import *



SERVER_PORT = 5000
FILES_DIRECTORY = "./FILESSERVER/"


class MyServerProtocol(QtWidgets.QDialog, basic.LineReceiver):
    """every new connection builds one MyServerProtocol object"""
    def __init__(self,factory):
        QtWidgets.QDialog.__init__(self)
        self.ui = uic.loadUi("teacher.ui")        # load UI
        self.ui.setWindowIcon(QIcon("drive.png"))  # definiere icon für taskleiste
        self.ui.exit.clicked.connect(self._onAbbrechen)      # setup Slots
        self.ui.doit_1.clicked.connect(lambda: self._onDoit_1())    #button x   (lambda is not needed - only if you wanna pass a variable to the function)
        self.ui.doit_2.clicked.connect(lambda: self._onDoit_2())    #button y
        self.ui.doit_3.clicked.connect(lambda: self._onDoit_3()) 
        self.ui.doit_4.clicked.connect(lambda: self._onDoit_4()) 
        self.ui.doit_5.clicked.connect(lambda: self._onDoit_5()) 
        
        self.factory = factory
        self.delimiter = '\n'
     
     
   
    #twisted
    def connectionMade(self):
        self.factory.clients.append(self)  # only the factory (MyServerFactory) is the persistent thing.. therefore we save the clients ( MyServerProtocol object) on factory.clients
        self.file_handler = None
        self.file_data = ()
        self._log('Client connected..')
        
        self.transport.write('Welcome\n')
        self.transport.write('ENDMSG\n')
        
        self._log('Connection from: %s (%d clients total)' % (self.transport.getPeer().host, len(self.factory.clients)))
    
    #twisted
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        self.file_handler = None
        self.file_data = ()
        
        self._log('Connection from %s lost (%d clients left)' % (self.transport.getPeer().host, len(self.factory.clients)))


    #twisted
    def rawDataReceived(self, data):
        filename = self.file_data[0]
        file_path = os.path.join(self.factory.files_path, filename)
        
        self._log('Receiving file chunk (%d KB)' % (len(data)))
        
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
                self.transport.write('File was successfully transfered and saved\n')
                self.transport.write('ENDMSG\n')
                
                self._log('File %s has been successfully transfered' % (filename))
            else:
                os.unlink(file_path)
                self.transport.write('File was successfully transfered but not saved, due to invalid MD5 hash\n')
                self.transport.write('ENDMSG\n')
            
                self.log('File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename))
        else:
            self.file_handler.write(data)


    #twisted
    def lineReceived(self, line):
        """whenever the client sends something """
        self._log('Received the following line from the client [%s]: %s' % (self.transport.getPeer().host, line))
        data = clean_and_split_input(line)
        if len(data) == 0 or data == '':
            return 
        command = data[0].lower()
        
        #check command - this way the client could trigger an action on the server
        
        if line.startswith('HASH'):
            # Received a file name and hash, server is sending us a file
            data = clean_and_split_input(line)

            filename = data[1]
            file_hash = data[2]
            
            self.file_data = (filename, file_hash)
            self._log('Preparing File Transfer from Client...' )
            self.setRawMode()   #this is a file - set to raw mode
       

    """
    onDoit_x checkt nicht ob eine connection vorhanden ist und crashed das programm fall keine conneciton da
    prinzipiell muss noch aussortiert werden an welche clients was gesendet wird bzw. an alle (broadcast)
    
    """

    def _onDoit_1(self):
        """send a file to the client"""
        try:
            filename = "serverfile.txt"
        except IndexError:
            self.transport.write('Missing filename\n')
            self.transport.write('ENDMSG\n')
            return
        
        if not self.factory.files:
            self.factory.files = self._get_file_list()
            
        if not filename in self.factory.files:
            self.log('filename not found in directory')
            return
        
        self._log('Sending file: %s (%d KB)' % (filename, self.factory.files[filename][1] / 1024))
        
        self.transport.write('HASH %s %s\n' % (filename, self.factory.files[filename][2]))
        self.setRawMode()
        
        for bytes in read_bytes_from_file(os.path.join(self.factory.files_path, filename)):
            self.transport.write(bytes)
        
        self.transport.write('\r\n')
        self.setLineMode()  # When the transfer is finished, we go back to the line mode 
        

    def _onDoit_2(self): #triggered on button click
        self.sendLine("GETFILE ./FILESCLIENT/clientfile.txt test")
      
      
    def _onDoit_3(self): #triggered on button click
        self._log('I schick an text.. mit ENDMSG')
        self.sendLine("Welcome")
        self.sendLine("to")
        self.sendLine("this session!")
        self.sendLine('ENDMSG')   #leert den line buffer des clients
    
    def _onDoit_4(self):
        for i in self.factory.clients:
            print "------------------------"
            print i.__dict__
            print "------------------------"
            print i.transport.__dict__
            i.sendLine("des geht nur an i")
            i.sendLine("ENDMSG")
      
        return
        
    def _onDoit_5(self):
        self._log("hä?")
        return


    def _onAbbrechen(self):    # Exit button
        self.ui.close()
        os._exit(0)  #otherwise only the gui is closed and connections are kept alive
    
    
    def _log(self, msg):
        timestamp = '[%s]' % datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.logwidget.append(timestamp + ' ' + str(msg))


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
            










class MyServerFactory(protocol.ServerFactory):
    def __init__(self, files_path):
        self.files_path = files_path
        self.clients = []
        self.files = None
        self.mainwindow = MyServerProtocol(self) 
        self.mainwindow.ui.show()
    
    def buildProtocol(self, addr):  # http://twistedmatrix.com/documents/12.1.0/api/twisted.internet.protocol.Factory.html#buildProtocol
        return self.mainwindow
        


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    qt5reactor.install()   # imported from file and needed for Qt to function properly in combination with twisted reactor
    
    from twisted.internet import reactor
    print ('Listening on port %d, serving files from directory: %s' % (SERVER_PORT, FILES_DIRECTORY))
    reactor.listenTCP(SERVER_PORT, MyServerFactory(FILES_DIRECTORY))  # start the server on SERVER_PORT
    reactor.run()





