import socket, ssl, time, threading, ujson
from tqdm import trange
from datetime import datetime
from settings import *


logger, filelogger = createLogger(__name__, file=True)
logger.setLevel(logging.DEBUG)
filelogger.setLevel(logging.DEBUG)

####            QuerySets are named lists of queries (static requests each associated to a name)           ####
class QuerySet:
    def __init__(self, name):
        self.name = name
        self.queries = []

    def getUserData(self):
        self.queries.append({'name': f'{self.name}_UserData',
                              'request': getUserDataRequest})
        logger.debug(Fore.BLUE + f'{self.queries[-1]}')
        logger.info(Fore.GREEN + f"added {self.queries[-1]} to the list of {self.name} queries")

    def getMarginLevel(self):
        self.queries.append({'name': f'{self.name}_MarginLevel',
                             'request': getMarginLevelRequest})
        logger.debug(Fore.BLUE + f'{self.queries[-1]}')
        logger.info(Fore.GREEN + f"added {self.queries[-1]} to the list of {self.name} queries")

    def getMarginTrade(self, *args):
        for query in args:
            self.queries.append({'name': f'{self.name}_MarginTrade_{query[0]}_{query[1]}',
                                'request': {'command': 'getMarginTrade',
                                            'arguments': {'symbol': query[0],
                                                          'volume': query[1]}
                                        }
                                 })
            logger.debug(Fore.BLUE + f'{self.queries[-1]}')
            logger.info(Fore.GREEN + f"added {self.queries[-1]} to the list of {self.name} queries")

    def getCommissionDef(self, *args):
        #   args:list of tuples ('str', int)
        #   Will register a query in the queryset for each tuple
        for query in args:
            self.queries.append({'name': f'{self.name}_Commission_{query[0]}_{query[1]}',
                                'request': {'command': 'getCommissionDef',
                                            'arguments': {'symbol': query[0],
                                                          'volume': query[1]}
                                        }
                                 })
            logger.debug(Fore.BLUE + f'{self.queries[-1]}')
            logger.info(Fore.GREEN + f"added {self.queries[-1]} to the list of {self.name} queries")

    def getAllSymbols(self):
        self.queries.append({'name': f'{self.name}_AllSymbols',
                              'request': getAllSymbolsRequest})
        logger.debug(Fore.BLUE + f'{self.queries[-1]}')
        logger.info(Fore.GREEN + f"added {self.queries[-1]} to the list of {self.name} queries")

    def getCalendar(self):
        self.queries.append({'name': f'{self.name}_Calendar',
                              'request': getCalendarRequest})
        logger.debug(Fore.BLUE + f'{self.queries[-1]}')
        logger.info(Fore.GREEN + f"added {self.queries[-1]} to the list of {self.name} queries")

    def getChartRange(self, name, symbols, period, start, end):
        #   args : (str, list of str, int, str(datetime), str(datetime))
        #   Will register a query in the queryset for each symbol of the list.
        try:
            start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            start_ts = datetime.timestamp(start)
            end_ts = datetime.timestamp(end)
            logger.debug(Fore.BLUE + f'start_ts = {start_ts} -- end_ts = {end_ts}')
            for symbol in symbols:
                request = {'command': 'getChartRangeRequest',
                            'arguments': {'info': {'start': 1000 * round(start_ts),
                                                   'period': period,
                                                   'end': 1000 * round(end_ts),
                                                   'symbol': symbol}
                                    }
                        }
                self.queries.append({'name': f'{self.name}_{name}_ChartRange_{symbol}',
                                  'request': request})
                logger.debug(Fore.BLUE + f'{self.queries[-1]}')
                logger.info(Fore.GREEN + f"added {self.queries[-1]} to the list of {self.name} queries")
        except:
            logger.exception()


####        All communications with the XTB json API happen through an AccessAPI instance         ####
class AccessAPI:
    requests = []
    key = ''
    datas = {}
    stream_datas = {}
    stream_socket_list = {}
    is_socket_open = {}
    thread_list = {}

    def __init__(self):
        s_add = socket.getaddrinfo(SERVER, STATIC_PORT)[0][4][0]
        self.static_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.static_s.connect((s_add, STATIC_PORT))
        self.static_s = ssl.wrap_socket(self.static_s)
        try:
            self.static_s.send(ujson.dumps(loginRequest).encode(FORMAT))
            status = self.static_s.recv().decode(FORMAT)
            status = ujson.loads(status)
            self.key = status['streamSessionId']
            logger.info(Fore.GREEN + 'LOGIN : {} \n'.format(status))
        except:
            logger.exception(Fore.RED + status['errorDescr'].upper())

    # noinspection PyArgumentList
    def staticDataRequest(self, *args):  #  feed with QuerySets
        try:
            for queryset in args:
                for query in queryset.queries:
                    request = query['request']
                    name = query['name']
                    time.sleep(0.2)
                    logger.debug(Fore.BLUE + f'request {name} = {request}')
                    for _ in trange(len(args), bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.WHITE),
                                    desc=Fore.BLUE + f"Downloading {request}"):
                        self.static_s.send(ujson.dumps(request).encode(FORMAT))
                        data = self.static_s.recv().decode(FORMAT)
                        self.datas[name] = '' + data
                        while '\n\n' not in data:
                            data = self.static_s.recv().decode(FORMAT)
                            self.datas[name] = self.datas[name] + data
                        self.datas[name] = ujson.loads(self.datas[name])
                    if self.datas[name]['status'] is False:
                        logger.info(Fore.RED + f"{name.upper()} : {self.datas[name]['status']}")
                        try:
                            logger.error(Fore.RED + self.datas[name]['errorDescr']\
                                         + '\n')
                        except:
                            logger.exception(Fore.RED + 'Error not listed on API documentation')
                    else:
                        logger.info(Fore.GREEN + f"{name.upper()} : {self.datas[name]['status']}")
            filelogger.info([key for key in self.datas.keys()])
        except NameError:
            logger.exception(Fore.RED + 'invalid argument' + '\n')

    def streamSocketInit(self, *socket_names):
        for name in socket_names:
            add = socket.getaddrinfo(SERVER, STREAM_PORT)[0][4][0]
            self.stream_socket_list[name] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.stream_socket_list[name].connect((add, STREAM_PORT))
            self.stream_socket_list[name] = ssl.wrap_socket(self.stream_socket_list[name])
            self.stream_socket_list[name].settimeout(5)
            self.is_socket_open[name] = True
        logger.debug(Fore.BLUE + f'{self.stream_socket_list}, {self.is_socket_open}')

    def _streamRecv(self, socket_name):
        self.stream_datas[socket_name] = []
        while self.is_socket_open[socket_name] is True:
            try:
                data = ''
                while '\n\n' not in data:
                    data += self.stream_socket_list[socket_name].recv().decode(FORMAT)
                self.stream_datas[socket_name].append(ujson.loads(data))
                logger.debug(Fore.BLUE + f'{data}')
            except socket.timeout:
                logger.debug(Fore.BLUE + "Didn't receive any data for 5sec")
            except ValueError:
                logger.debug(Fore.BLUE + "Datas not JSON readable")
            except:
                logger.exception(Fore.RED + "Error while trying to receive")
        filelogger.debug(self.stream_datas[socket_name])
        time.sleep(0.2)

    def _streamListening(self, socket_name):
        try:
            self.thread_list[socket_name] = threading.Thread(target=self._streamRecv, args=[socket_name])
            self.thread_list[socket_name].start()
        except:
            logger.exception(Fore.RED + f'Exception while trying to open thread')

    def streamTickPrices(self, socket_name, symbol):
        self._streamListening(socket_name)
        try:
            request = {"command": "getTickPrices",
                       "streamSessionId": self.key,
                       "symbol": symbol,
                       "minArrivalTime": 1500,
                       "maxLevel": 2}
            self.stream_socket_list[socket_name].send(ujson.dumps(request).encode(FORMAT))
            logger.info(Fore.GREEN + f'Stream {socket_name} started')
        except:
            logger.exception(Fore.RED + "Couldn't open stream")

    def stopTickPrices(self, socket_name, symbol):
        try:
            request = {"command": "stopTickPrices",
                       "symbol": symbol}
            self.stream_socket_list[socket_name].send(ujson.dumps(request).encode(FORMAT))
            self.is_socket_open[socket_name] = False
            self.thread_list[socket_name].join()
            self.stream_socket_list[socket_name].close()
            del self.stream_socket_list[socket_name]
            del self.thread_list[socket_name]
            del self.is_socket_open[socket_name]
            logger.info(Fore.GREEN + f'Thread {socket_name} terminated and socket {socket_name} closed')
        except:
            logger.exception(Fore.RED + f"Couldn't close {socket_name} streaming connection")

    def streamBalance(self, socket_name):
        self._streamListening(socket_name)
        try:
            request = {"command": "getBalance",
                       "streamSessionId": self.key}
            self.stream_socket_list[socket_name].send(ujson.dumps(request).encode(FORMAT))
            logger.info(Fore.GREEN + f'Stream {socket_name} started')
        except:
            logger.exception(Fore.RED + 'Request not sent')

    def stopBalance(self, socket_name):
        try:
            request = {"command": "stopBalance"}
            self.stream_socket_list[socket_name].send(ujson.dumps(request).encode(FORMAT))
            self.is_socket_open[socket_name] = False
            self.thread_list[socket_name].join()
            self.stream_socket_list[socket_name].close()
            del self.stream_socket_list[socket_name]
            del self.thread_list[socket_name]
            del self.is_socket_open[socket_name]
            logger.info(Fore.GREEN + f'Thread {socket_name} terminated and socket {socket_name} closed')
        except:
            logger.exception(Fore.RED + f"Couldn't close {socket_name} streaming connection")





if __name__ == '__main__':



    #TODO#         Uncomment and modify with your values for a quick first use


    from data_processing import static_to_chartdataset
    #!# Create an AccessAPI instance to access XTB JSON API
    session = AccessAPI()

    #!# Create a stream of data
    session.streamSocketInit(*['eurusd', 'balance'])
    session.streamTickPrices('eurusd', 'EURUSD')
    # session.streamBalance('balance')

    #!#Create a QuerySet
    req = QuerySet('first_query')

    #!# Add queries to the QuerySet
    symbols = ["EURUSD",
               'OIL.WTI',
               'GBPUSD'
               ]
    req.getChartRange('hist_datas', symbols, 240, '2020-06-10 02:00:00',
                                                     '2020-07-24 12:00:00')
    req.getChartRange('short_datas', symbols, 5, '2020-07-18 09:00:00',
                                                     '2020-07-24 19:00:00')

    req.getMarginTrade(*[('EURUSD', 1), ('GBPUSD', 1)])
    req.getUserData()
    logger.debug(Fore.BLUE + f'requests = {[query for query in req.queries]}')


    #!# Pass the QuerySet to the API
    session.staticDataRequest(req)
    logger.debug(Fore.BLUE + f'datas = {[data for data in session.datas.keys()]}')

    #!# Process collected datas
    datasets = static_to_chartdataset(session.datas)
    logger.debug(Fore.BLUE + f'{datasets[0]}')
    time.sleep(20)
    session.stopTickPrices('eurusd', 'EURUSD')
    # session.stopBalance('balance')
    logger.debug(Fore.BLUE + f'{session.stream_datas}')

    pass