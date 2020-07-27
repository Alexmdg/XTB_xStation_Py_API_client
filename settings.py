import logging
from colorama import Fore

SERVER = "xapi.xtb.com"
STATIC_PORT = 5124
STREAM_PORT = 5125
USERID = 11311073        #account_id
PASSWORD = 'Mdp876800;'    #account_password
KEY = ''
FORMAT = 'UTF-8'


####            Logging           ####

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(Fore.WHITE + '%(asctime)s:%(levelname)s:%(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)



####            Unmutable Requests           ####

getVersionRequest = {'command': 'getVersion'}

loginRequest = {"command" : "login",
                "arguments": {"userId": USERID,
                              "password": PASSWORD
                        }
        }

logoutRequest = {"command" : "logout",
        }

getMarginLevelRequest = {"command": "getMarginLevel"}


getAllSymbolsRequest = {"command": "getAllSymbols",
        }

getCalendarRequest = {"command": "getCalendar"
        }

getUserDataRequest = {"command": "getCurrentUserData"
        }

