#! /usr/bin/env python
# -*- coding: utf-8 -*-
# TEACHER - SERVER #
from twisted.internet.protocol import DatagramProtocol

import os
import sys
sys.path.append( os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ) )  #add application root to python path for imports

import qt5reactor
import ipaddress
import datetime
import sip
import zipfile
import ntpath

from twisted.internet import protocol
from twisted.protocols import basic
from twisted.internet.task import LoopingCall
from config.config import *
from common import *


from PyQt5 import uic, QtWidgets,QtCore
from PyQt5.QtGui import *






class MyServerProtocol(basic.LineReceiver):
    """every new connection builds one MyServerProtocol object"""
    def __init__(self,factory):
        self.factory = factory
        self.delimiter = '\n'
        self.clientID = ""
     
     
    #twisted
    def connectionMade(self):
        self.factory.clients.append(self)  # only the factory (MyServerFactory) is the persistent thing.. therefore we save the clients ( MyServerProtocol object) on factory.clients
        self.file_handler = None
        self.file_data = ()
        self.refused = False
        self.clientConnectionID = str(self.transport.client[1])
        self.transport.write('Connection established!\n')
        self.transport.write('ENDMSG\n')
        self.factory._log('Connection from: %s (%d clients total)' % (self.transport.getPeer().host, len(self.factory.clients)))

    
    #twisted
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        self.file_handler = None
        self.file_data = ()
        self.factory._log('Connection from %s lost (%d clients left)' % (self.transport.getPeer().host, len(self.factory.clients)))
        
        if not self.refused:
            self.factory._disableClientScreenshot(self.clientID)  
        

    #twisted
    def rawDataReceived(self, data):
        """ handle incoming byte data """
        filename = self.file_data[2]
        file_path = os.path.join(self.factory.files_path, filename)
        #self.factory._log('Receiving file chunk (%d KB)' % (len(data)/1024))
        
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
                    fixFilePermissions(SERVERSCREENSHOT_DIRECTORY)  # fix filepermission of transfered file 
                    self._createListItem(screenshot_file_path)  # make the clientscreenshot visible in the listWidget
                
                elif self.file_data[1] == "FOLDER":
                    extract_dir = os.path.join(SERVERUNZIP_DIRECTORY,self.clientID ,filename[:-4])  #extract to unzipDIR / clientID / foldername without .zip (cut last four letters #shutil.unpack_archive(file_path, extract_dir, 'tar')   #python3 only but twisted RPC is not ported to python3 yet
                    with zipfile.ZipFile(file_path,"r") as zip_ref:
                        zip_ref.extractall(extract_dir)     #derzeitiges verzeichnis ist .life/SERVER/unzip
                    os.unlink(file_path)   #delete zip file
                    fixFilePermissions(SERVERUNZIP_DIRECTORY) # fix filepermission of transfered file 
                
                elif self.file_data[1] == "ABGABE":
                    extract_dir = os.path.join(ABGABE_DIRECTORY,self.clientID ,filename[:-4])  #extract to unzipDIR / clientID / foldername without .zip (cut last four letters #shutil.unpack_archive(file_path, extract_dir, 'tar')   #python3 only but twisted RPC is not ported to python3 yet
                    with zipfile.ZipFile(file_path,"r") as zip_ref:
                        zip_ref.extractall(extract_dir)     #derzeitiges verzeichnis ist .life/SERVER/unzip
                    os.unlink(file_path)   #delete zip file
                    fixFilePermissions(ABGABE_DIRECTORY) # fix filepermission of transfered file 

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
        self.file_data = clean_and_split_input(line)
        if len(self.file_data) == 0 or self.file_data == '':
            return 
        #trigger=self.file_data[0] type=self.file_data[1] filename=self.file_data[2] filehash=self.file_data[3] (( clientID=self.file_data[4] ))
        if line.startswith('AUTH'):
            newID = self.file_data[1]   #AUTH is sent immediately after a connection is made and transfers the clientID
            self._checkClientID(newID)  # check if this custom client id (entered by the student) is already taken
        elif line.startswith('FILETRANSFER'):           
            self.factory._log('Preparing File Transfer from Client...' )
            self.setRawMode()   #this is a file - set to raw mode
    
    
    
    def _checkClientID(self,newID):
        """searches for the newID in factory.clients and rejects the connection if found"""
        ids = []
        for i in self.factory.clients:
            ids.append(i.clientID)
            
        if newID in ids:
            print "this user already exists and is connected" 
            self.refused = True
            self.sendLine('REFUSED\n')
            self.transport.loseConnection()
            self.factory._log('Client Connection from %s has been refused. User already exists' % (newID))
        
            return 
        else:  #otherwise ad this unique id to the client protocol instance and request a screenshot
            self.clientID = newID
            self.sendLine("FILETRANSFER SEND SHOT %s.jpg none" %(self.transport.client[1]) ) 
            return


    
    def _createListItem(self,screenshot_file_path):
        """generates new listitem that displays the clientscreenshot"""
        items = []  # create a list of items out of the listwidget items (the widget does not provide an iterable list
        for index in xrange(self.factory.ui.listWidget.count()):
            items.append(self.factory.ui.listWidget.item(index))
        
        existingItem = False
        for item in items:
            if item.id == self.clientID:
                print "exists"
                existingItem = item   #there should be only one matching item
        
        if existingItem :   # just update screenshot
            Pixmap = QPixmap(screenshot_file_path)
            existingItem.picture.setPixmap(Pixmap)
            existingItem.info.setText('%s \n%s' %(self.clientID, self.clientConnectionID) )
            existingItem.pID = self.clientConnectionID  # in case this is a reconnect - update clientConnectionID in order to address the correct connection
        else:    #create item - create labels - create gridlayout - addlabels to gridlayout - create widget - set widget to item
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint( QtCore.QSize( 140, 140) );
            item.id = self.clientID   #store clientID as itemID for later use (delete event)
            item.pID = self.clientConnectionID
            item.disabled=False
            
            Pixmap = QPixmap(screenshot_file_path)
            item.picture = QtWidgets.QLabel()
            item.picture.setPixmap(Pixmap)
            item.picture.setAlignment(QtCore.Qt.AlignCenter)
            item.info = QtWidgets.QLabel('%s \n%s' %(self.clientID, self.clientConnectionID) )
            item.info.setAlignment(QtCore.Qt.AlignCenter)
            
            grid = QtWidgets.QGridLayout()
            grid.setSpacing(4)
            grid.addWidget(item.picture, 1, 0)
            grid.addWidget(item.info, 2, 0)
            
            widget = QtWidgets.QWidget()
            widget.setLayout(grid)
            widget.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
            widget.customContextMenuRequested.connect(lambda: self.on_context_menu(item.pID) )
           
            self.factory.ui.listWidget.addItem(item)  #add the listitem to the listwidget
            self.factory.ui.listWidget.setItemWidget(item,widget)   # set the widget as the listitem's widget
            
       
    def on_context_menu(self, clientConnectionID):
        menu = QtWidgets.QMenu()
        
        action_1 = QtWidgets.QAction("Abgabe holen", menu, triggered = lambda: self.factory._onAbgabe(clientConnectionID) )
        action_2 = QtWidgets.QAction("Screenshot updaten", menu, triggered = lambda: self.factory._onScreenshots(clientConnectionID) )
        action_3 = QtWidgets.QAction("Verbindung beenden, menu, triggered = lambda: self.factory._removeClient(clientConnectionID) )
        
        menu.addActions([action_1, action_2, action_3])
        handled = True
        cursor=QCursor()
        menu.exec_(cursor.pos())
    
        return
       














class MyServerFactory(QtWidgets.QDialog, protocol.ServerFactory):
    def __init__(self, files_path):
        self.files_path = files_path
        self.clients = []  #store all client connections in this array
        self.files = None
        
        QtWidgets.QDialog.__init__(self)
        self.ui = uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.ui"))        # load UI
        self.ui.setWindowIcon(QIcon("pixmaps/windowicon.png"))  # definiere icon für taskleiste
        self.ui.exit.clicked.connect(self._onAbbrechen)      # setup Slots
        self.ui.sendfile.clicked.connect(lambda: self._onSendfile())    #button x   (lambda is not needed - only if you wanna pass a variable to the function)
        self.ui.showip.clicked.connect(self._onShowIP)    #button y
        self.ui.abgabe.clicked.connect(lambda: self._onAbgabe("all")) 
        self.ui.screenshots.clicked.connect(lambda: self._onScreenshots("all")) 
        self.ui.startexam.clicked.connect(self._onStartExam) 
        self.ui.starthotspot.clicked.connect(self._onStartHotspot) 
        self.ui.startconfig.clicked.connect(self._onStartConfig)
        self.ui.testfirewall.clicked.connect(self._onTestFirewall)
        self.ui.loaddefaults.clicked.connect(self._onLoadDefaults)
        self.ui.autoabgabe.clicked.connect(self._onAutoabgabe)
        self.ui.closeEvent = self.closeEvent   #links the window close event to our custom ui

        checkFirewall(self)  #deactivates all iptable rules if any
        self.lc = LoopingCall(self._onAbgabe)   # _onAbgabe kann durch lc.start(intevall) im intervall ausgeführt werden
        
        self.ui.show()


    def closeEvent(self, evnt):
        self.ui.showMinimized()
        evnt.ignore()



    def buildProtocol(self, addr):  # http://twistedmatrix.com/documents/12.1.0/api/twisted.internet.protocol.Factory.html#buildProtocol
        return MyServerProtocol(self)     #wird bei einer eingehenden client connection aufgerufen - erstellt ein object der klasse MyServerProtocol für jede connection und übergibt self (die factory)



    def _onAutoabgabe(self):
        intervall = self.ui.aintervall.value()
        minute_intervall = intervall * 60  #minuten nicht sekunden
        if self.lc.running:
           
            self.ui.autoabgabe.setIcon(QIcon("pixmaps/chronometer-off.png"))
            self.lc.stop()
        if intervall is not 0:
            self.ui.autoabgabe.setIcon(QIcon("pixmaps/chronometer.png"))
            self._log("Auto-Abgabe im Intervall %s aktiviert"    %(str(intervall))   )
            self.lc.start(minute_intervall)
        else:
            self._log("Abgabe-Intervall ist 0 - Auto-Abgabe deaktiviert")



    def _onLoadDefaults(self):
        self._log('Standard Konfiguration für EXAM Desktop wurde wiederhergestellt.')
        copycommand = "sudo cp -r ./DATA/EXAMCONFIG %s" %(WORK_DIRECTORY)
        os.system(copycommand)



    def _onSendfile(self):
        """send a file to all clients"""
        if not self.clients:
            self._log("no clients connected")
            return
        # show filepicker
        filedialog = QtWidgets.QFileDialog()
        filedialog.setDirectory(SERVERFILES_DIRECTORY)  #set default directory
        file_path = filedialog.getOpenFileName()   # get filename
        file_path = file_path[0] 
   
        if file_path:
            filename = ntpath.basename(file_path)   #get filename without path
            file_size = os.path.getsize(file_path)
            md5_hash = get_file_md5_hash(file_path)
        
            for i in self.clients:
                self._log('Sending file: %s (%d KB)' % (filename, file_size / 1024))
                i.transport.write('FILETRANSFER GET FILE %s %s\n' % (str(filename), md5_hash))  #trigger clienttask type filename filehash
                i.setRawMode()
                for bytes in read_bytes_from_file(file_path):
                    i.transport.write(bytes)
                
                i.transport.write('\r\n')
                i.setLineMode()  # When the transfer is finished, we go back to the line mode 



    def _onShowIP(self):
        scriptfile = os.path.join(SCRIPTS_DIRECTORY,"gui-getmyip.sh" )
        startcommand = "exec %s &" %(scriptfile)
        os.system(startcommand) 
        
   
   
    def _onAbgabe(self, who):  
        """get ABGABE folder"""
        if not self.clients:
            self._log("no clients connected")
            return
        
        self._log('Client Folder zB. ABGABE holen')
        if who == "all":
            for i in self.clients:
                # i.sendLine("FILETRANSFER SEND FOLDER %s none" %(folder)  )
                filename = "Abgabe-%s" %(datetime.datetime.now().strftime("%H-%M-%S"))
                i.sendLine("FILETRANSFER SEND ABGABE %s none" %(filename)  )
        else:
            for i in self.clients:
                if i.clientConnectionID == who:
                    filename = "Abgabe-%s" %(datetime.datetime.now().strftime("%H-%M-%S"))
                    i.sendLine("FILETRANSFER SEND ABGABE %s none" %(filename)  )


    def _onStartHotspot(self):
        scriptfile = os.path.join(SCRIPTS_DIRECTORY,"gui-activate-lifehotspot-root.sh" )
        startcommand = "exec %s &" %(scriptfile)
        os.system(startcommand) 


    
    def _onScreenshots(self, who):
        if not self.clients:
            self._log("no clients connected")
            return
       
        self._log("Updating screenshots")
        if who == "all":
            for i in self.clients:
                i.sendLine("FILETRANSFER SEND SHOT %s.jpg none" %(i.transport.client[1]) )   #the clients id is used as filename for the screenshot
        else:
            for i in self.clients:
                if i.clientConnectionID == who:
                    i.sendLine("FILETRANSFER SEND SHOT %s.jpg none" %(i.transport.client[1]) )

  
    def _onStartExam(self):
        """ 
        ZIP examconfig folder
        send configuration-zip to clients - unzip there
        invoke startexam.sh file on clients 
        
        """
        if not self.clients:
            self._log("no clients connected")
            return
        
        self._log('Folder examconfig senden')
        target_folder = EXAMCONFIG_DIRECTORY     
        filename = "EXAMCONFIG"
        output_filename = os.path.join(SERVERZIP_DIRECTORY,filename )
        shutil.make_archive(output_filename, 'zip', target_folder)
        filename = "%s.zip" %(filename)
        
        for i in self.clients:
            self.files = get_file_list(self.files_path)
            if not filename in self.files:
                self.log('filename not found in directory')
                return
            
            self._log('Sending file: %s (%d KB)' % (filename, self.files[filename][1] / 1024))
            
            i.transport.write('FILETRANSFER GET EXAM %s %s\n' % (filename, self.files[filename][2]))  #trigger clienttask type filename filehash
            i.setRawMode()
            print self.files[filename][0]
            for bytes in read_bytes_from_file(self.files[filename][0]):
                i.transport.write(bytes)
            
            i.transport.write('\r\n')
            i.setLineMode() 



    def _onTestFirewall(self):      
        if self.ui.testfirewall.text() == "&Stoppe Firewall":
            os.system("kdialog --passivepopup 'Die Firewall wird gestoppt!' 3 2> /dev/null & ")
            
            scriptfile = os.path.join(SCRIPTS_DIRECTORY,"exam-firewall.sh" )
            startcommand = "exec %s stop &" %(scriptfile)
            os.system(startcommand) 
            self.ui.testfirewall.setText("Firewall testen")

            ipfields = [self.ui.firewall1,self.ui.firewall2,self.ui.firewall3,self.ui.firewall4]
            for i in ipfields:
                palettedefault = i.palette()
                palettedefault.setColor(QPalette.Active, QPalette.Base, QColor(255, 255, 255))
                i.setPalette(palettedefault)
            
        elif self.ui.testfirewall.text() == "&Firewall testen":
            ipstore = os.path.join(EXAMCONFIG_DIRECTORY, "EXAM-A-IPS.DB")
            openedexamfile = open(ipstore, 'w+')  #erstelle die datei neu
            ipfields = [self.ui.firewall1,self.ui.firewall2,self.ui.firewall3,self.ui.firewall4]
            number = 0
            for i in ipfields:
                ip = i.text()
                if checkIP(ip):
                    thisexamfile = open(ipstore, 'a+')   #anhängen
                    number = number + 1
                    if not number is 1:  #zeilenumbruch einfügen ausser vor erster zeile (keine leerzeilen in der datei erlaubt)
                        thisexamfile.write("\n")
                    thisexamfile.write("%s" % ip)
                else:
                    if ip !="":
                        palettewarn = i.palette()
                        palettewarn.setColor(i.backgroundRole(), QColor(200, 80, 80))
                        #palettewarn.setColor(QPalette.Active, QPalette.Base, QColor(200, 80, 80))
                        i.setPalette(palettewarn)
            
            os.system("kdialog --passivepopup 'Die Firewall wird aktiviert!' 3 2> /dev/null & ")
            
            scriptfile = os.path.join(SCRIPTS_DIRECTORY,"exam-firewall.sh" )
            startcommand = "exec %s start &" %(scriptfile)
            os.system(startcommand) 
            self.ui.testfirewall.setText("Stoppe Firewall")



    def _onStartConfig(self):
        scriptfile = os.path.join(EXAMCONFIG_DIRECTORY,"startexam.sh" )
        startcommand = "exec %s config &" %(scriptfile)
        os.system(startcommand) 
        self.ui.close()



    def _onAbbrechen(self):    # Exit button
        os.remove(SERVER_PIDFILE) 
        self.ui.close()
        os._exit(0)  #otherwise only the gui is closed and connections are kept alive
    
    
    
    def _log(self, msg):
        timestamp = '[%s]' % datetime.datetime.now().strftime("%H:%M:%S")
        self.ui.logwidget.append(timestamp + " " + str(msg))



    def _removeClient(self,clientID):
        items = []  # create a list of items out of the listwidget items (the widget does not provide an iterable list
        for index in xrange(self.ui.listWidget.count()):
            items.append(self.ui.listWidget.item(index))
        
        for item in items:
            if item.id == clientID:
                sip.delete(item)   #delete all ocurrances of this screenshotitem (the whole item with the according widget and its labels)
        
        for client in self.clients:
                if client.clientConnectionID == clientID:
                    client.refused = True
                    client.sendLine('REMOVED\n')
                    client.transport.loseConnection()
                    client.factory._log('Client Connection has been removed.')
        



    def _disableClientScreenshot(self,clientID):
        items = []  # create a list of items out of the listwidget items (the widget does not provide an iterable list
        for index in xrange(self.ui.listWidget.count()):
            items.append(self.ui.listWidget.item(index))
        
        for item in items:
            if clientID == item.id:
                pixmap = QPixmap("pixmaps/nouserscreenshot.png")
                item.picture.setPixmap(pixmap)
                item.info.setText('%s \ndisconnected' %(clientID)  )
                item.disabled=True
                


class MultcastLifeServer(DatagramProtocol):

    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(5)
        # Join a specific multicast group:
        self.transport.joinGroup("228.0.0.5")
        # self.transport.write("SERVER: Assimilate", ("228.0.0.5", 8005))

    def datagramReceived(self, datagram, address):
        print "Datagram %s received from %s" % (repr(datagram), repr(address))
        if "CLIENT" in datagram:
            # Rather than replying to the group multicast address, we send the
            # reply directly (unicast) to the originating port:
            self.transport.write('SERVER: Assimilate', ("228.0.0.5", 8005))
            self.transport.write("SERVER: Assimilate", address)


if __name__ == '__main__':
    
    prepareDirectories()  #cleans everything and copies some scripts     
    killscript = os.path.join(SCRIPTS_DIRECTORY, "terminate-exam-process.sh")
    os.system("sudo %s %s" %(killscript, 'server') )  #make sure only one client instance is running per client
    #time.sleep(1)
    writePidFile()
    
    app = QtWidgets.QApplication(sys.argv)
    qt5reactor.install()   # imported from file and needed for Qt to function properly in combination with twisted reactor
    
    from twisted.internet import reactor
   
    reactor.listenTCP(SERVER_PORT, MyServerFactory(SERVERFILES_DIRECTORY))  # start the server on SERVER_PORT

    reactor.listenMulticast(8005, MultcastLifeServer(),
                            listenMultiple=True)

    print ('Listening on port %d' % (SERVER_PORT))
    reactor.run()
        
   




