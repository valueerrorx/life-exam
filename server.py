#! /usr/bin/env python
# -*- coding: utf-8 -*-
# TEACHER - SERVER #
import qt5reactor
import os
import sys
import ipaddress
import datetime
import pprint
import sip
import shutil
import zipfile

from twisted.internet import protocol
from twisted.protocols import basic
from common import *
from config import *

from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtGui import *






class MyServerProtocol(basic.LineReceiver):
    """every new connection builds one MyServerProtocol object"""
    def __init__(self,factory):
        self.factory = factory
        self.delimiter = '\n'
     
     
    #twisted
    def connectionMade(self):
        self.factory.clients.append(self)  # only the factory (MyServerFactory) is the persistent thing.. therefore we save the clients ( MyServerProtocol object) on factory.clients
        self.file_handler = None
        self.file_data = ()
        self.clientID = str(self.transport.client[1])
        self.factory._log('Client connected..')
        self.transport.write('Connection established!\n')
        self.transport.write('ENDMSG\n')
        self.factory._log('Connection from: %s (%d clients total)' % (self.transport.getPeer().host, len(self.factory.clients)))
        self.sendLine("FILETRANSFER SEND SHOT %s.jpg none" %(self.transport.client[1]) ) 
    
    #twisted
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        self.factory._deleteClientScreenshot(self.clientID)
        self.file_handler = None
        self.file_data = ()
        self.factory._log('Connection from %s lost (%d clients left)' % (self.transport.getPeer().host, len(self.factory.clients)))
        # destroy this instance ?

    #twisted
    def rawDataReceived(self, data):
        filename = self.file_data[2]
        file_path = os.path.join(self.factory.files_path, filename)
        self.factory._log('Receiving file chunk (%d KB)' % (len(data)/1024))
        
        if not self.file_handler:
            self.file_handler = open(file_path, 'wb')
        
        if data.endswith('\r\n'): # Last chunk
            data = data[:-2]
            self.file_handler.write(data)
            self.file_handler.close()
            self.file_handler = None
            self.setLineMode()
            
            if validate_file_md5_hash(file_path, self.file_data[3]):   #everything ok..  file received
                self.factory._log('File %s has been successfully transfered' % (filename))
                
                if self.file_data[1] == "SCREENSHOT":  #screenshot is received on initial connection
                    screenshot_file_path = os.path.join(SERVERSCREENSHOT_DIRECTORY, filename)
                    os.rename(file_path, screenshot_file_path)  # move image to screenshot folder
                    self._createListItem(screenshot_file_path)  # make the clientscreenshot visible in the listWidget
                
                elif self.file_data[1] == "FOLDER":
                    extract_dir = os.path.join(SERVERUNZIP_DIRECTORY,self.clientID ,filename[:-4])  #extract to unzipDIR / clientID / foldername without .zip (cut last four letters #shutil.unpack_archive(file_path, extract_dir, 'tar')   #python3 only but twisted RPC is not ported to python3 yet
                    with zipfile.ZipFile(file_path,"r") as zip_ref:
                        zip_ref.extractall(extract_dir)
                    os.unlink(file_path)   #delete zip file

            else:   # wrong file hash
                os.unlink(file_path)
                self.transport.write('File was successfully transfered but not saved, due to invalid MD5 hash\n')
                self.transport.write('ENDMSG\n')
                self.factory._log('File %s has been successfully transfered, but deleted due to invalid MD5 hash' % (filename))
        
        else:
            self.file_handler.write(data)


    #twisted
    def lineReceived(self, line):
        """whenever the client sends something """
        self.factory._log('Received the following line from the client [%s]: %s' % (self.transport.getPeer().host, line))
        self.file_data = clean_and_split_input(line)
        if len(self.file_data) == 0 or self.file_data == '':
            return 

        if line.startswith('FILETRANSFER'):
            # Received a file name and hash, client is sending us a file
            trigger = self.file_data[0]
            filetype = self.file_data[1]
            filename = self.file_data[2]
            file_hash = self.file_data[3]
            
            self.factory._log('Preparing File Transfer from Client...' )
            self.setRawMode()   #this is a file - set to raw mode
    
    
    
    def _createListItem(self,screenshot_file_path):
        """generates new listitem that displays the clientscreenshot"""
        items = []  # create a list of items out of the listwidget items (the widget does not provide an iterable list
        for index in xrange(self.factory.ui.listWidget.count()):
            items.append(self.factory.ui.listWidget.item(index))
        
        existingItem = False
        for item in items:
            if item.id == self.clientID:
                existingItem = item   #there should be only one matching item
        
        self.label1 = QtWidgets.QLabel()
        self.label2 = QtWidgets.QLabel('client ID: %s' %(self.clientID) )
        self.label1.Pixmap = QPixmap(screenshot_file_path)
        self.label1.setPixmap(self.label1.Pixmap)
        # generate a widget that combines the labels
        self.widget = QtWidgets.QWidget()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(4)
        self.grid.addWidget(self.label1, 1, 0)
        self.grid.addWidget(self.label2, 2, 0)
        self.widget.setLayout(self.grid)
        
        #generate a listitem
        if existingItem:
            self.item = existingItem
        else:
            self.item = QtWidgets.QListWidgetItem()
            self.item.setSizeHint( QtCore.QSize( 140, 100) );
            self.item.id = self.clientID   #store clientID as itemID for later use (delete event)
            
        # add the listitem to the factorys listwidget and set the widget as it's widget
        self.factory.ui.listWidget.addItem(self.item)
        self.factory.ui.listWidget.setItemWidget(self.item,self.widget)








class MyServerFactory(QtWidgets.QDialog, protocol.ServerFactory):
    def __init__(self, files_path):
        self.files_path = files_path
        self.clients = []  #store all client connections in this array
        self.files = None
        deleteFolderContent(SERVERSCREENSHOT_DIRECTORY)
        
        QtWidgets.QDialog.__init__(self)
        self.ui = uic.loadUi("teacher.ui")        # load UI
        self.ui.setWindowIcon(QIcon("drive.png"))  # definiere icon für taskleiste
        self.ui.exit.clicked.connect(self._onAbbrechen)      # setup Slots
        self.ui.doit_1.clicked.connect(lambda: self._onDoit_1())    #button x   (lambda is not needed - only if you wanna pass a variable to the function)
        self.ui.doit_2.clicked.connect(lambda: self._onDoit_2())    #button y
        self.ui.doit_3.clicked.connect(lambda: self._onDoit_3()) 
        self.ui.doit_4.clicked.connect(lambda: self._onDoit_4()) 
        self.ui.doit_5.clicked.connect(lambda: self._onDoit_5()) 
        
        self.ui.show()
    
    #twisted
    def buildProtocol(self, addr):  # http://twistedmatrix.com/documents/12.1.0/api/twisted.internet.protocol.Factory.html#buildProtocol
        return MyServerProtocol(self)     #wird bei einer eingehenden client connection aufgerufen - erstellt ein object der klasse MyServerProtocol für jede connection und übergibt self (die factory) 
        
        

    def _onDoit_1(self):
        """send a file to all clients"""
        if not self.clients:
            self._log("no clients connected")
            return
        
        for i in self.clients:
            try:
                filename = "serverfile.txt"
            except IndexError:
                i.transport.write('Missing filename\n')
                i.transport.write('ENDMSG\n')
                return
            
            self.files = get_file_list(self.files_path)
                
            if not filename in self.files:
                self.log('filename not found in directory')
                return
            
            self._log('Sending file: %s (%d KB)' % (filename, self.files[filename][1] / 1024))
            
            i.transport.write('FILETRANSFER GET FILE %s %s\n' % (filename, self.files[filename][2]))  #trigger clienttask type filename filehash
            i.setRawMode()
            
            for bytes in read_bytes_from_file(os.path.join(self.files_path, filename)):
                i.transport.write(bytes)
            
            i.transport.write('\r\n')
            i.setLineMode()  # When the transfer is finished, we go back to the line mode 



    def _onDoit_2(self): #triggered on button click
        """get the same file from all clients"""
        if not self.clients:
            self._log("no clients connected")
            return
        
        self._log("getting a file")
        for i in self.clients:
            i.sendLine("FILETRANSFER SEND FILE clientfile.txt none")    #trigger clienttask type filename filehash
        



    def _onDoit_3(self): #triggered on button click
        if not self.clients:
            self._log("no clients connected")
            return
        
        self._log('Client Folder zB. ABGABE holen')
        for i in self.clients:
            # i.sendLine("FILETRANSFER SEND FOLDER %s none" %(folder)  )
            filename = "Abgabe-%s" %(datetime.datetime.now().strftime("%H-%M-%S"))
            i.sendLine("FILETRANSFER SEND ABGABE %s none" %(filename)  )

    def _onDoit_4(self):
        if not self.clients:
            self._log("no clients connected")
            return
        
        print("------------------------")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.clients[0].__dict__)
        print("------------------------")
        pp.pprint(self.clients[0].transport.__dict__)
       

    
    def _onDoit_5(self):
        if not self.clients:
            self._log("no clients connected")
            return
       
        self._log("getting screenshot")
        for i in self.clients:
            i.sendLine("FILETRANSFER SEND SHOT %s.jpg none" %(i.transport.client[1]) )   #the clients id is used as filename for the screenshot
       


    def _onAbbrechen(self):    # Exit button
        self.ui.close()
        os._exit(0)  #otherwise only the gui is closed and connections are kept alive
    
    
    
    def _log(self, msg):
        timestamp = '[%s]' % datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.logwidget.append(timestamp + '\n' + str(msg))


    
    def _deleteClientScreenshot(self,clientID):
        items = []  # create a list of items out of the listwidget items (the widget does not provide an iterable list
        for index in xrange(self.ui.listWidget.count()):
            items.append(self.ui.listWidget.item(index))
        
        for item in items:
            if clientID == item.id:
                sip.delete(item)   #delete all ocurrances of this screenshotitem (the whole item with the according widget and its labels)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    qt5reactor.install()   # imported from file and needed for Qt to function properly in combination with twisted reactor
    
    from twisted.internet import reactor
    print ('Listening on port %d' % (SERVER_PORT))
    reactor.listenTCP(SERVER_PORT, MyServerFactory(SERVERFILES_DIRECTORY))  # start the server on SERVER_PORT
    reactor.run()





