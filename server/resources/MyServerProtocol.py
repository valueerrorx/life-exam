#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging

import classes.mutual_functions as mutual_functions
from twisted.protocols import basic
from config.enums import DataType, Command
from config.config import SERVERSCREENSHOT_DIRECTORY, SHARE_DIRECTORY,\
    DEBUG_SHOW_NETWORKTRAFFIC, DELIVERY_DIRECTORY
import zipfile
from server.ui.ServerUI import MsgType
from classes.Hasher import Hasher


class MyServerProtocol(basic.LineReceiver):
    """every new connection builds one MyServerProtocol object"""

    def __init__(self, factory):
        self.factory = factory  # type: MyServerFactory
        self.clientName = ""
        self.file_handler = None
        self.line_data_list = ()
        self.refused = False
        self.clientConnectionID = ""
        self.filetransfer_fail_count = 0

        self.logger = logging.getLogger(__name__)

    # twisted-Event: A Connection is made
    def connectionMade(self):  # noqa        
        self.file_handler = None
        self.line_data_list = ()
        self.refused = False
        self.clientConnectionID = str(self.transport.client[1])
        self.transport.setTcpKeepAlive(1)
        self.factory.window.log(
            'Connection from: %s (%d clients total)' % (
                self.transport.getPeer().host, len(self.factory.server_to_client.clients)), MsgType.AllwaysDebug)

    # twisted-Event: A Connection is lost
    def connectionLost(self, reason):  # noqa
        """
        maybe give it another try if connection closed unclean? ping it ? send custom keepalive? or even a reconnect call?
        """

        self.factory.server_to_client.remove_client(self)
        self.file_handler = None
        self.line_data_list = ()
        """we deactivate the rawmode FT block here in case the disconnect interrupted an ongoing filetransfer
        which would never send \r\n and therefore never unblock
        (worst case scenario: an other FT could be started during an ongoing FT - because notblocked -
        and lead to a corrupted (and therefore removed) FT)
        """
        self.factory.rawmode = False

        self.factory.window.log(
            'Connection from %s lost (%d clients left)' % (
                self.transport.getPeer().host, len(self.factory.server_to_client.clients)), MsgType.AllwaysDebug)

        if not self.refused:
            self.factory.window.disableClientScreenshot(self)

    # twisted-Event: Data Received
    def rawDataReceived(self, data):
        """ is handled, if Server is set in RawMode """
        filename = self.line_data_list[2]
        file_path = os.path.join(self.factory.files_path, filename)
        # self.factory.window.log('Receiving file chunk (%d KB)' % (len(data)/1024))
        # print('Receiving file chunk (%d KB)' % (len(data)/1024))

        if not self.file_handler:
            try:
                self.file_handler = open(file_path, 'wb')
            except FileNotFoundError:
                self.logger.error("Cannot create File %s" % file_path)

        if data.endswith(b'\r\n'):  # Last chunk
            data = data[:-2]
            self.file_handler.write(data)
            self.file_handler.close()
            self.file_handler = None
            self.setLineMode()
            # filetransfer finished "UNLOCK" fileopertions
            self.factory.rawmode = False

            # everything ok..  file received
            if mutual_functions.validate_file_md5_hash(file_path, self.line_data_list[3]):
                msg = 'File %s has been successfully transferred' % (filename)
                self.factory.window.log(msg)
                self.filetransfer_fail_count = 0

                """
                Client is connecting
                """
                if self.line_data_list[1] == DataType.SCREENSHOT.value:
                    # screenshot is received on initial connection
                    screenshot_file_path = os.path.join(SERVERSCREENSHOT_DIRECTORY, filename)
                    # move image to screenshot folder
                    os.rename(file_path, screenshot_file_path)
                    # fix file permission of transferred file
                    mutual_functions.fixFilePermissions(SERVERSCREENSHOT_DIRECTORY)
                    # make the client screenshot visible in the listWidget
                    self.factory.window.createOrUpdateListItem(self, screenshot_file_path)
                   
                    if hasattr(self.factory.window.screenshotwindow, 'clientname'):
                        if self.factory.window.screenshotwindow.clientname in filename:
                            self.factory.window.screenshotwindow.setScreenshotFilePath(screenshot_file_path)
                            self.factory.window.screenshotwindow.updateUI()

                elif self.line_data_list[1] == DataType.ABGABE.value:
                    """ Request for all Data of a client """
                    # extract to unzipDIR / clientName / foldername without .zip (cut last four letters
                    # shutil.unpack_archive(file_path, extract_dir, 'tar')

                    user_dir = os.path.join(SHARE_DIRECTORY, DELIVERY_DIRECTORY, self.clientName)
                    extract_dir = os.path.join(user_dir, filename[:-4])

                    # be sure directory exists
                    os.system("mkdir -p %s" % extract_dir)

                    # checks if filename is taken and renames this file in order to make
                    # room for the userfolder
                    mutual_functions.checkIfFileExists(user_dir)

                    if os.path.isfile(file_path):
                        if "-empty".lower() in file_path.lower():
                            # empty Abgabe, dont extract, just inform
                            fp = "%s/NoDataFromClient.txt" % extract_dir
                            os.system("touch %s" % fp)
                            os.system('echo "No Data was received from Client!" >> %s' % fp)
                        else:
                            with zipfile.ZipFile(file_path, "r") as zip_ref:
                                zip_ref.extractall(extract_dir)
                    # fix filepermission of transferred file
                    mutual_functions.fixFilePermissions(SHARE_DIRECTORY)

                    # delete zip file
                    os.unlink(file_path)

                    # the network progress is allways handled
                    # Send Event to Wait Thread with Client Name
                    ui = self.factory.window

                    # Flags to String
                    aA = '0'
                    if ui.autoAbgabe:
                        aA = '1'

                    print("Autoabgabe: %s" % (aA))

                    if ui.progress_thread:
                        ui.progress_thread.fireEvent_Abgabe_finished(self.line_data_list[4], aA)

            else:  # wrong file hash
                os.unlink(file_path)
                self.transport.write(b'File was successfully transferred but not saved, due to invalid MD5 hash\n')

                # string.encode()
                # return an encoded version of the string as a bytes object
                msg = Command.ENDMSG.value + "\r\n"
                self.transport.write(msg.encode())
                msg = 'File %s has been successfully transferred, but deleted due to invalid MD5 hash' % (filename)
                self.factory.window.log(msg)
                self.logger.error(msg)

                # request file again if filerequest was ABGABE (we don't care about a missed screenshotupdate)
                if self.line_data_list[1] == DataType.ABGABE.value and self.filetransfer_fail_count <= 1:
                    self.filetransfer_fail_count += 1
                    msg = 'Failed transfers: %s' % (self.filetransfer_fail_count)
                    self.factory.window.log(msg)
                    self.logger.info(msg)
                    # True means AutoAbgabe
                    self.factory.window.onAbgabe(self.clientName, True)
                else:
                    self.filetransfer_fail_count = 0

        else:
            self.file_handler.write(data)

    def sendEncodedLine(self, line):
        # twisted
        self.sendLine(line.encode())

    # twisted-Event: Line Received
    def lineReceived(self, line):
        """whenever the CLIENT sent something """
        line = line.decode()  # we get bytes but need strings
        self.line_data_list = mutual_functions.clean_and_split_input(line)

        if DEBUG_SHOW_NETWORKTRAFFIC:
            self.logger.debug(self.line_data_list)

        self.line_dispatcher()

    def line_dispatcher(self):
        if len(self.line_data_list) == 0 or self.line_data_list == '':
            return
        """
        FILETRANSFER    (ist immer getfile, der client kann derzeit noch keine files anfordern)
        command = self.line_data_list[0]
        filetype = self.line_data_list[1]
        filename = self.line_data_list[2]
        filehash = self.line_data_list[3]
        (( clientName = self.line_data_list[4] ))

        AUTH
        command = self.line_data_list[0]
        id = self.line_data_list[1]
        pincode = self.line_data_list[2]

        FILE_OK
        command = self.line_data_list[0]
        clientName = self.line_data_list[1]

        """
        try:
            # Dictionary
            command = {
                Command.AUTH.value: self._checkclientAuth,
                Command.FILETRANSFER.value: self._get_file_request,
                Command.FILE_OK.value: self._file_ok,
                Command.LOCKSCREEN_OK.value: self._lockscreen_ok,
                Command.UNLOCKSCREEN_OK.value: self._unlockscreen_ok,
            }

            # Default is None if nothing is found
            line_handler = command.get(self.line_data_list[0], None)
            line_handler()
        except Exception as e:
            self.logger.error("line_dispatcher: Command [%s] NOT Found ... doing nothing!" % self.line_data_list[0])
            self.logger.error(e)

    def _lockscreen_ok(self):
        """ a client has locked the screen and sends OK """
        # fire Event to Thread
        ui = self.factory.window
        # get the client item from QListWidget
        print("_lockscreen_ok %s" % self.line_data_list[1])
        clientWidget = ui.get_list_widget_by_client_ConID(self.line_data_list[1])
        # Maybe new Widget is not Registered
        if clientWidget:
            ui.progress_thread.fireEvent_Lock_Screen(clientWidget)
            # Update Screenshot
            ui.onScreenshots(self.line_data_list[1])

    def _unlockscreen_ok(self):
        """ a client has locked the screen and sends OK """
        # fire Event to Thread
        ui = self.factory.window
        # get the client item from QListWidget
        clientWidget = ui.get_list_widget_by_client_ConID(self.line_data_list[1])
        # Maybe new Widget is not Registered
        if clientWidget:
            ui.progress_thread.fireEvent_UnLock_Screen(clientWidget)
            # Update Screenshot
            ui.onScreenshots(self.line_data_list[1])

    def _file_ok(self):
        """ a client has received a file sends OK """
        # fire Event to Thread
        ui = self.factory.window
        # get the client item from QListWidget
        clientWidget = ui.get_list_widget_by_client_name(self.line_data_list[1])

        ui.progress_thread.fireEvent_File_received(clientWidget)
        # filetransfer finished "UNLOCK" fileopertions
        self.factory.rawmode = False

    def _get_file_request(self):
        """
        Puts server into raw mode to receive files
        """
        msg = 'Incoming File Transfer from Client <b>%s</b>' % (self.clientName)
        self.factory.window.log(msg)
        self.setRawMode()  # this is a file - set to raw mode

    def _checkDoubleClientName(self, name):
        """
        check for if Client name exists > rename it
        Connection is unique with connectionID!
        """
        newName = name
        index = 1
        widget = self._testName(name)
        if widget:
            found = True
            # search as long Name is Unique
            while found:
                newName = "%s[%s]" % (name, index)
                found = self._testName(newName)
                index += 1
        return newName

    def _testName(self, name):
        """just a helper"""
        ui = self.factory.window
        for widget in ui.get_list_widget_items():
            if name == widget.getName():
                return widget
        return False

    def _checkclientAuth(self):
        """
        searches for the newID in factory.clients and rejects the connection if found or wrong pincode
        :param newID: string Username
        :param pincode: int
        :return:
        """
        newID = self.line_data_list[1]
        newID = self._checkDoubleClientName(newID)

        pincode = self.line_data_list[2]
        # self.factory.server_to_client.clients.keys there we store clientConnectionID's
        conID = self.clientConnectionID

        hasher = Hasher()
        uniqueID = hasher.getUniqueConnectionID(newID, conID)

        if uniqueID in self.factory.server_to_client.clients.keys():
            self.refused = True
            self.sendEncodedLine(Command.REFUSED.value)
            self.transport.loseConnection()
            msg = 'Client Connection from %s has been refused. User already exists' % (newID)
            self.factory.window.log(msg)
            return
        else:
            self.factory.server_to_client.add_client(self, uniqueID)
            if int(pincode) != int(self.factory.pincode):
                self.refused = True
                self.sendEncodedLine(Command.REFUSED.value)
                self.transport.loseConnection()
                msg = 'Client Connection from %s has been refused. Wrong pincode given' % (newID)
                self.factory.window.log(msg)
                return
            else:  # otherwise ad this unique id to the client protocol instance and request a screenshot
                self.clientName = newID
                msg = 'New Connection from <b>%s</b>' % (newID)
                self.factory.window.log(msg)
                # transfer, send, screenshot, filename, hash, clean Abgabe
                line = "%s %s %s %s.jpg none none" % (Command.FILETRANSFER.value, Command.SEND.value, DataType.SCREENSHOT.value, self.clientName)
                self.sendEncodedLine(line)
                return
