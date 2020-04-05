from requests import post
from platform import platform, architecture, system
from subprocess import Popen
from time import sleep
from colorama import Fore
from colorama import init as colorinit

class Color(object):
    END = Fore.RESET
    OK = Fore.GREEN
    NOTE = Fore.YELLOW
    WARN = Fore.MAGENTA
    ERR = Fore.RED
    DISPLAY = Fore.BLUE

    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        colorinit()
        #print(self)


COLOR = Color()
SYSTEM = 0 if system() == 'Windows' else 1


def getlogindata():
    return open(r'./logindata.txt', 'r', encoding='utf-8').readlines()


def getlogindata_phone():
    return open(r'./logindata_phone.txt', 'r', encoding='utf-8').readlines()


def send_err(err_info):
    data = {
        'platform': platform(),
        'arch': str(architecture()),
        'errorinfo': err_info
    }
    post('http://39.98.127.46/', data=data)
