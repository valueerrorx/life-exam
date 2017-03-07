import datetime

from classes.message import *
from server import MyServerProtocol


def broadcast_message(connections, msg_func, **kwargs):
    """
    Calls the passed messenger function for all passed connections
    :param connections: a dictionary of connections
    :type connections: dict
    :param msg_func: the function for the message you want to broadcast
    :type msg_func: func
    :return:
    :rtype:
    """

    for connection in connections.itervalues():
        msg_func(connection, **kwargs)


def request_screenshot(connection, **kwargs):
    """
    Requests a screenshot of a connection
    :param connection:
    :type connection: MyServerProtocol
    :param kwargs: Should contain named argument 'file_name=xxxx.jpg'
    :return: None
    """
    connection.sendLine(Message.getPickledMessage(RequestScreenshotMessage, **kwargs))


def request_abgabe(connection):
    """

    :param connection:
    :type connection: MyServerProtocol
    :param kwargs:
    :type kwargs: dict
    :return:
    :rtype:
    """
    file_name = "Abgabe-%s-%s" % (datetime.datetime.now().strftime("%H:%M:%S"), connection.clientName)
    connection.sendLine(Message.getPickledMessage(RequestAbgabeMessage, file_name=file_name))


def refuse(connection):
    """

    :param connection:
    :type connection: MyServerProtocol
    :return:
    :rtype:
    """
    connection.sendLine(Message.getPickledMessage(RefusedMessage))


def init_exam_mode(connection, file_name="", md5_hash="", cleanup_abgabe=True):
    """
    This message prepares the client for exam mode and triggers it eventually
    :param connection:
    :type connection: MyServerProtocol
    :param file_name: The name of the file that will be sent
    :type file_name: str
    :param md5_hash: The md5 Hash of the file that will be sent
    :type md5_hash: str
    :param cleanup_abgabe: Should the client clean the abgabe folder first
    :type cleanup_abgabe: bool
    :return:
    :rtype:
    """
    connection.sendLine(Message.getPickledMessage(ReceiveExamMessage, file_name=file_name, md5_hash=md5_hash,
                                                  cleanup_abgabe=cleanup_abgabe))


def receive_file(connection, data_type, file_name="", md5_hash=""):
    """
    Tells the connection it will receive a file
    :param connection:
    :type connection: MyServerProtocol
    :param data_type: The filetype that will be send
    :type data_type: DataType
    :param file_name: the filename of the file that will be sent
    :type file_name: str
    :param md5_hash: the md5hash of the file that will be sent
    :type md5_hash: str
    :return:
    :rtype:
    """
    msg_class = ReceiveDataMessageFactory.get_rcv_data_message_for_type(data_type)
    if msg_class is not None:
        connection.sendLine(Message.getPickledMessage(msg_class, file_name=file_name, md5_hash=md5_hash))
