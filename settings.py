import logging
from colorama import Fore

SERVER = "xapi.xtb.com"
STATIC_PORT = 5124      #   5124: demo, 5112: real
STREAM_PORT = 5125      #   5125: demo, 5113: real
USERID = 11311073       #   set account_id
PASSWORD = ''           #   set your account_password
FORMAT = 'UTF-8'

####            Logging           ####

def createLogger(name, file=None,):
    logger = logging.getLogger(name)
    formatter = logging.Formatter(Fore.WHITE + '%(asctime)s:%(levelname)s:%(funcName)s:%(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if file is True :
        filelogger = logging.getLogger(f"f_{name}")
        filehandler = logging.FileHandler(f"{name}.log")
        filehandler.setFormatter(formatter)
        filelogger.addHandler(filehandler)
        return logger, filelogger
    else:
        return logger




####            Unmutable Requests           ####

loginRequest = {"command": "login",
                "arguments": {"userId": USERID,
                              "password": PASSWORD}
                    }
getVersionRequest = {'command': 'getVersion'}
logoutRequest = {"command" : "logout"}
getMarginLevelRequest = {"command": "getMarginLevel"}
getAllSymbolsRequest = {"command": "getAllSymbols"}
getCalendarRequest = {"command": "getCalendar"}
getUserDataRequest = {"command": "getCurrentUserData"}

