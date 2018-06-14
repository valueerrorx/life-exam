#! /usr/bin/env python3
from enum import Enum



class DataType(Enum):
    SCREENSHOT = b"SS"
    FOLDER = b"FO"
    ABGABE = b"AB"
    EXAM = b"EX"
    FILE = b"FI"
    PRINTER = b"PR"

class Command(Enum):
    ENDMSG = b"E"
    AUTH = b"AU"
    FILETRANSFER = b"FT"
    REFUSED = b"RE"
    REMOVED = b"RM"
    GET = b"G"
    SEND = b"S"
    LOCK = b"LKS"
    UNLOCK = b"ULKS"
    EXITEXAM = b"EXIT"
