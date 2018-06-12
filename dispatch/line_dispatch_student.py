#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time

from config.shell_scripts import SHOT

from common import *
from config.enums import Command, DataType



"""
Contains functions and dispatcher dictionaries for Lines sent from the server to the client. Lines are
patched through the dictionaries to return and call the proper function for the client to react to the servers
orders.
"""






"""
student_line_dispatcher
level 1
"""

def end_msg(client, line):
    """
    Shows Desktop popup of received message
    :param client: clientprotocol
    :param line: line received
    :return:
    """
    message = '%s' % ' '.join(map(str, client.buffer))
    showDesktopMessage(message)
    client.buffer = []


def connection_refused(client, line):
    """
    Shoes Desktopmessage for connection refused
    :param client: clientprotocol
    :param line: line recieived
    :return:
    """
    showDesktopMessage('Connection refused!\n Client ID already taken or wrong PIN!')
    client.factory.failcount = 100


def connection_removed(client, line):
    """
    Shoes Desktopmessage for connection refused
    :param client: clientprotocol
    :param line: line recieived
    :return:
    """
    showDesktopMessage('Connection aborted by the Teacher!')
    client.factory.failcount = 100

def lock_screen(client, line):
    """Just locks the client screens
    :param client: ClientProtocol
    :param line: Line received from server
    :return:
    """
    lockScreen(client, line)
    return

def exitExam(client, line):
    """start stopexam.sh
    :param client: ClientProtocol
    :param line: Line received from server
    :return:
    """
    print("stopping exam")
    startcommand = "sudo %s/scripts/stopexam.sh exam &" %(WORK_DIRECTORY) # start as user even if the twistd daemon is run by root
    os.system(startcommand)  # start script

    return



def file_transfer_request(client, line):
    """
    Decides if a GET or a SEND operation needs to be dispatched and unboxes relevant attributes to be used in the actual
    sending/receiving functions
    :param client: ClientProtocol
    :param line: Line received from server
    :return:
    """
    client.file_data = clean_and_split_input(line)
    client.factory.files = get_file_list(client.factory.files_path)
    
    # explizit ist besser als implizit.. der ganze linedispatcher verursacht einen overhead an komplexizität (simple if statements waren übersichtlicher)
    trigger = client.file_data[0]
    task = client.file_data[1]
    filetype = client.file_data[2]
    filename = client.file_data[3]
    file_hash = client.file_data[4]
    
    # not every line sendline statement needs to be updated if a new attribute is added
    try:
        cleanup_abgabe = client.file_data[5]
    except IndexError:
        cleanup_abgabe = "none"
    
    #(trigger, task, filetype, filename, file_hash, cleanup_abgabe) = client.file_data[0:6]
    
    student_file_request_dispatcher[task](client, filetype, filename, file_hash, cleanup_abgabe)







"""
student_file_request_dispatcher
level 2
"""


def send_file_request(client, filetype, *args):
    """
    Dispatches Method to prepare requested file transfer and sends file
    :param client: clientprotocol
    :param filetype: Filetype to be sent as in (File, Folder, Screenshot)
    :param args: (filename, file_hash)
    :return:
    """
    filename = student_prepare_filetype_dispatcher[filetype](client, *args)
    client._sendFile(filename, filetype)

    # TODO: maybe do the actual file sending in the level 1 dispatch (file_transfer_request) ? as in method file_transfer_request checks what is ordered, if get -> sendFile else setRawMode



def get_file_request(client, *args):
    """
    Puts client into raw mode to receive files
    :param client: clientprotocol
    :param args:
    :return:
    """
    client.setRawMode()










"""
student_prepare_filetype_dispatcher
level 3
"""

def prepare_screenshot(client, filename, *args):
    """
    Prepares a screenshot to be sent
    :param client: clientprotocol
    :param filename: screenshot filename
    :param args: (file_hash)
    :return: filename
    """
    scriptfile = os.path.join(SCRIPTS_DIRECTORY, SHOT)
    screenshotfile = os.path.join(CLIENTSCREENSHOT_DIRECTORY, filename)
    command = "%s %s" % (scriptfile, screenshotfile)
    os.system(command)
    return filename


def prepare_folder(client, filename, *args):
    """
    Prepares requested folder to be sent as zip file
    :param client: clientprotocol
    :param filename: folder archive filename
    :param args: (file_hash)
    :return: filename
    """
    if filename in client.factory.files:
        target_folder = client.factory.files[filename[0]]
        output_filename = os.path.join(CLIENTZIP_DIRECTORY, filename)
        shutil.make_archive(output_filename, 'zip', target_folder)
        return "%s.zip" % filename


def prepare_abgabe(client, filename, *args):
    """
    Prepares Abgabe to be sent as zip archive
    :param client: clientprotocol
    :param filename: filename of abgabe archive
    :param args: (file_hash)
    :return: filename
    """
    client._triggerAutosave()
    time.sleep(2)  # TODO: make autosave return that it is finished!
    target_folder = SHARE_DIRECTORY
    output_filename = os.path.join(CLIENTZIP_DIRECTORY, filename)
    shutil.make_archive(output_filename, 'zip', target_folder)  # create zip of folder
    return "%s.zip" % filename  # this is the filename of the zip file


"""
Dispatcher dictionaries, used to dispatch correct methods depending on Command/DataType received
Organisation into levels? Level 1 gets called directly from the ClientProtocol, calls level 2 depending on command,
level 2 calls level 3 functions according to datatype to do the actual preparation work for the command that has been set
"""

"""
Level 1 Dispatch
"""
student_line_dispatcher = {
    Command.ENDMSG: end_msg,
    Command.REFUSED: connection_refused,
    Command.REMOVED: connection_removed,
    Command.FILETRANSFER: file_transfer_request,
    Command.LOCK: lock_screen,
    Command.UNLOCK: lock_screen,
    Command.EXITEXAM: exitExam,
}

"""
Level 2 Dispatch
"""
student_file_request_dispatcher = {
    Command.SEND: send_file_request,
    Command.GET: get_file_request
}

"""
Level 3 Dispatch
"""
student_prepare_filetype_dispatcher = {
    DataType.SCREENSHOT: prepare_screenshot,
    DataType.FOLDER: prepare_folder,
    DataType.ABGABE: prepare_abgabe
}
