from colorama import Fore
from prelog import CheckLog
from prelog import LEVELS as poglevel
from prelog import FORMATS as pogformat

log = CheckLog(fmt=pogformat['locate'])
log.create_logger('qset', Fore.YELLOW, fmt=pogformat['locate'])
log.create_logger('static', Fore.MAGENTA, fmt=pogformat['locate'])
log.create_logger('stream', Fore.LIGHTCYAN_EX, fmt=pogformat['locate'])
log.main.setLevel(poglevel['1'])
log.qset.setLevel(poglevel['1'])
log.static.setLevel(poglevel['1'])
log.stream.setLevel(poglevel['1'])
log.dataProc.setLevel(poglevel['1'])


####            Connection infos            ####
SERVER = "xapi.xtb.com"
STATIC_PORT = 5124          #   5124: demo, 5112: real
STREAM_PORT = 5125          #   5125: demo, 5113: real
FORMAT = 'UTF-8'



####            Unmutable Requests           ####
getVersionRequest = {'command': 'getVersion'}
logoutRequest = {"command" : "logout"}
getMarginLevelRequest = {"command": "getMarginLevel"}
getAllSymbolsRequest = {"command": "getAllSymbols"}
getCalendarRequest = {"command": "getCalendar"}
getUserDataRequest = {"command": "getCurrentUserData"}

