import logging
from colorama import Fore

SERVER = "xapi.xtb.com"
STATIC_PORT = 5124      #   5124: demo, 5112: real
STREAM_PORT = 5125      #   5125: demo, 5113: real
USERID = 11311073       #   set account_id
PASSWORD = ''           #   set your account_password
FORMAT = 'UTF-8'

####            Logging           ####

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(Fore.WHITE + '%(asctime)s:%(levelname)s:%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


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

