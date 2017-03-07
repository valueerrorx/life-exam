from collections import OrderedDict
from wheel.signatures import assertTrue

from config.enums import Command, DataType


class Message(object):
    def __init__(self, command, **kwargs):
        self.command = command
        self.arguments = OrderedDict().update(kwargs)  # type: OrderedDict

    def __str__(self):
        return " ".join(
            ((" ".join((self.command, self.data_type))), (" ".join(value) for value in self.arguments.values())))


class EndMessage(Message):
    def __init__(self, **kwargs):
        Message.__init(self, Command.ENDMSG, **kwargs)


class AuthMessage(Message):
    def __init__(self, **kwargs):
        """
        AuthMessage
        :param kwargs: requires named argument 'id'
        """
        # TODO: cannot get this assert to work....
        assert "id" in kwargs.keys(), "Keyword argument id missing"
        Message.__init__(self, Command.AUTH, **kwargs)


class RequestDataMessage(Message):
    def __init__(self, data_type, **kwargs):
        """
        A message that tells the other party to send some kind of data.
        Extend it for requesting new kind of DataTypes
        :param data_type: DataType
        :param kwargs: see subclasse for required kwargs
        """
        self.data_type = data_type
        Message.__init__(self, Command.REQUESTDATA, **kwargs)


class RequestFileMessage(RequestDataMessage):
    def __init__(self, **kwargs):
        """
        Tells the other party (ie. server -> client) that it wants it to send a File
        :param kwargs: requires named argument 'file_name'
        """
        RequestDataMessage.__init__(self, DataType.FILE, **kwargs)


class RequestFolderMessage(RequestDataMessage):
    def __init__(self, **kwargs):
        RequestDataMessage.__init__(self, DataType.FOLDER, **kwargs)


class RequestScreenshotMessage(RequestDataMessage):
    def __init__(self, **kwargs):
        """
        Tells the other party it wants it to send a screenshot
        :param kwargs: requires named argument 'file_name', should be of format 'xxxxx.jpg'
        """
        RequestDataMessage.__init__(self, DataType.SCREENSHOT, **kwargs)


class RequestAbgabeMessage(RequestDataMessage):
    def __init__(self, **kwargs):
        """
        Tells the client that it needs to send Abgabe
        :param kwargs: requires named argument 'file_name', should be in format 'Abgabe-{time}-clientName'
        """
        RequestDataMessage.__init__(self, DataType.ABGABE, **kwargs)


class ReceiveDataMessage(Message):
    def __init__(self, data_type, **kwargs):
        """
        A message that tells the other party that it can expect to receive byte data next
        Extend it if you want to send new types of data
        :param data_type: DataType
        :param kwargs: see subclasse for required kwargs
        """
        self.data_type = data_type
        Message.__init__(self, Command.RECEIVEDATA, **kwargs)


class ReceiveFileMessage(ReceiveDataMessage):
    def __init__(self, **kwargs):
        """
        Expect to receive a File
        :param kwargs: requires named arguments:
                                            'file_name'
                                            'md5_hash'
        """
        ReceiveDataMessage.__init__(self, DataType.FILE, **kwargs)


class ReceiveFolderMessage(ReceiveDataMessage):
    def __init__(self, **kwargs):
        ReceiveDataMessage.__init__(self, DataType.FOLDER, **kwargs)


class ReceiveExamMessage(ReceiveDataMessage):
    def __init__(self, **kwargs):
        ReceiveDataMessage.__init__(self, DataType.EXAM, **kwargs)
