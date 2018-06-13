#! /usr/bin/env python3
from enum import Enum


class DataType(Enum):
    SCREENSHOT = "SS"
    FOLDER = "FO"
    ABGABE = "AB"
    EXAM = "EX"
    FILE = "FI"
    PRINTER = "PR"

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


print(Command.AUTH) 
