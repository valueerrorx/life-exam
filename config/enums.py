#! /usr/bin/env python3
from enum import Enum


class DataType(Enum):
    SCREENSHOT = "SS"
    ABGABE = "AB"
    EXAM = "EX"
    FILE = "FI"
    PRINTER = "PR"

    def tobytes(self):
        return bytes(self.value, 'utf-8')

    @staticmethod
    def list():
        return list(map(lambda c: c.value, DataType))


class Command(Enum):
    ENDMSG = "E"
    AUTH = "AU"
    FILETRANSFER = "FT"
    REFUSED = "RE"
    REMOVED = "RM"
    GET = "G"
    SEND = "S"
    LOCK = "LKS"
    UNLOCK = "ULKS"
    EXITEXAM = "EXIT"
    FILE_OK = "FO"
    LOCKSCREEN_OK = "LKSOK"
    UNLOCKSCREEN_OK = "ULKSOK"

    def tobytes(self):
        return bytes(self.value, 'utf-8')

    @staticmethod
    def list():
        return list(map(lambda c: c.value, Command))
