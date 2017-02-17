import time

from config.shell_scripts import SHOT

from common import *
from config.enums import Command, DataType


def end_msg(client, *args):
    message = '%s' % ' '.join(map(str, client.buffer))
    showDesktopMessage(message)
    client.buffer = []


def connection_refused(client, *args):
    showDesktopMessage('Connection refused!\n Client ID already taken!')
    client.factory.failcount = 100


def file_transfer_request(client, line):
    """
    Decides if a GET or a SEND operation needs to be dispatched
    :param client: ClientProtocol
    :param line: Line received from server
    :return:
    """
    client.file_data = clean_and_split_input(line)
    client.factory.files = get_file_list(client.factory.files_path)
    (trigger, task, filetype, filename, file_hash) = client.file_data[0:5]
    student_file_request_dispatcher[task](filetype, filename, file_hash, client)


def send_file_request(filetype, *args):
    """
    Dispatches method for specific filetype to be sent
    :param filetype: Filetype to be sent as in (File, Folder, Screenshot)
    :param args: (filename, file_hash, client)
    :return:
    """
    student_send_file_filetype_dispatcher[filetype](*args)
    client = args[2]
    client._sendFile(args[0], filetype)


def get_file_request(filetype, *args):
    client = args[2]
    client.setRawMode()


def send_screenshot(filename, *args):
    scriptfile = os.path.join(SCRIPTS_DIRECTORY, SHOT)
    screenshotfile = os.path.join(CLIENTSCREENSHOT_DIRECTORY, filename)
    command = "%s %s" % (scriptfile, screenshotfile)
    os.system(command)


def send_folder(filename, *args):
    client = args[1]
    if filename in client.factory.files:
        target_folder = client.factory.files[filename[0]]
        output_filename = os.path.join(CLIENTZIP_DIRECTORY, filename)
        shutil.make_archive(output_filename, 'zip', target_folder)
        filename = "%s.zip" % filename


def send_abgabe(filename, *args):
    client = args[1]
    client._triggerAutosave()
    time.sleep(2)  # what
    target_folder = ABGABE_DIRECTORY
    output_filename = os.path.join(CLIENTZIP_DIRECTORY, filename)
    shutil.make_archive(output_filename, 'zip', target_folder)  # create zip of folder
    filename = "%s.zip" % filename  # this is the filename of the zip file


# dispatcher dictionaries
student_line_dispatcher = {
    Command.ENDMSG: end_msg,
    Command.REFUSED: connection_refused,
    Command.FILETRANSFER: file_transfer_request,

}

student_file_request_dispatcher = {
    Command.SEND: send_file_request,
    Command.GET: get_file_request
}

student_send_file_filetype_dispatcher = {
    DataType.SCREENSHOT: send_screenshot,
    DataType.FOLDER: send_folder,
    DataType.ABGABE: send_abgabe
}
