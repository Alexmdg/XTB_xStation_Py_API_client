import logging
from colorama import Fore

SERVER = "xapi.xtb.com"
STATIC_PORT = 5124      #   5124: demo, 5112: real
STREAM_PORT = 5125      #   5125: demo, 5113: real
USERID = 11311073       #   set account_id
PASSWORD = 'Mdp876800;'           #   set your account_password
FORMAT = 'UTF-8'

####            Logging           ####

logger = logging.getLogger(__name__)
filelogger = logging.getLogger(f"f_{__name__}")
formatter = logging.Formatter(Fore.WHITE + '%(asctime)s:%(levelname)s:%(funcName)s:%(message)s')
handler = logging.StreamHandler()
filehandler = logging.FileHandler(f"{__name__}.log")
handler.setFormatter(formatter)
logger.addHandler(handler)
filehandler.setFormatter(formatter)
filelogger.addHandler(filehandler)


logger.setLevel(logging.DEBUG)
filelogger.setLevel(logging.DEBUG)



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

