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