import socket, ssl, time, threading, ujson
from tqdm import trange
from datetime import datetime
from settings import *

# noinspection SpellCheckingInspection
logger, filelogger = createLogger(__name__, file=True)
logger.setLevel(logging.INFO)
filelogger.setLevel(logging.INFO)

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
    static_datas = {}
    stream_datas = {}
    is_streaming = False
    is_receiving = False

    def __init__(self):
        main_add = socket.getaddrinfo(SERVER, STATIC_PORT)[0][4][0]
        self.static_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.static_s.connect((main_add, STATIC_PORT))
        self.static_s = ssl.wrap_socket(self.static_s)
        stream_add = socket.getaddrinfo(SERVER, STREAM_PORT)[0][4][0]
        self.stream_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_s.connect((stream_add, STREAM_PORT))
        self.stream_s = ssl.wrap_socket(self.stream_s)
        self.stream_s.settimeout(5)
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
                        self.static_datas[name] = '' + data
                        while '\n\n' not in data:
                            data = self.static_s.recv().decode(FORMAT)
                            self.static_datas[name] = self.static_datas[name] + data
                        self.static_datas[name] = ujson.loads(self.static_datas[name])
                    if self.static_datas[name]['status'] is False:
                        logger.info(Fore.RED + f"{name.upper()} : {self.static_datas[name]['status']}")
                        try:
                            logger.error(Fore.RED + self.static_datas[name]['errorDescr']\
                                         + '\n')
                        except:
                            logger.exception(Fore.RED + 'Error not listed on API documentation')
                    else:
                        logger.info(Fore.GREEN + f"{name.upper()} : {self.static_datas[name]['status']}")
            filelogger.info([key for key in self.static_datas.keys()])
        except NameError:
            logger.exception(Fore.RED + 'invalid argument' + '\n')

    def _streamRecv(self):
        self.is_receiving = True
        while self.is_streaming is True:
            data = ''
            try: data += self.stream_s.recv().decode(FORMAT)
            except socket.timeout: logger.debug(Fore.BLUE + "Didn't receive any data for 5sec")
            except: logger.exception(Fore.RED + "Error while trying to receive")
            try:
                if data != '':
                    try: data = ujson.loads(data)
                    except ValueError: logger.debug(Fore.RED + "Datas not JSON readable: " + Fore.YELLOW + f"{data}")
                    if data['command'] == 'balance':
                        self.stream_datas['balance'].append(data)
                        logger.info(Fore.GREEN + f'datas added to stream_datas["balance"] dict')
                        logger.debug(Fore.BLUE + f'{data} added to stream_datas dict')
                    elif data['command'] == 'tickPrices':
                        self.stream_datas[f"tickPrices_{data['data']['symbol']}"].append(data)
                        logger.info(Fore.GREEN+ "datas added to stream_datas['" + f"tickPrices_{data['data']['symbol']}] dict")
                        logger.debug(Fore.BLUE + f'{data} added to stream_datas dict')
            except TypeError:
                logger.debug(Fore.RED + 'Datas was not JSON but string and has not been saved')
        self.is_receiving = False

    def streamListeningInit(self):
        try:
            self.is_streaming = True
            self.thread = threading.Thread(target=self._streamRecv)
            self.thread.start()
        except:
            logger.exception(Fore.RED + f'Exception while trying to open thread')

    def streamListeningStop(self):
        self.is_streaming = False
        self.thread.join()
        logger.info(Fore.GREEN + 'Listening thread terminated')

    def streamTickPrices(self, symbol):
        self.stream_datas[f"tickPrices_{symbol}"] = []
        try:
            request = {"command": "getTickPrices",
                       "streamSessionId": self.key,
                       "symbol": symbol,
                       "minArrivalTime": 1500,
                       "maxLevel": 2}
            self.stream_s.send(ujson.dumps(request).encode(FORMAT))
            logger.debug(Fore.BLUE + f'Stream request getTickPrices for symbol {symbol} has been sent')
        except:
            logger.exception(Fore.RED + "Couldn't open stream")

    def stopTickPrices(self, symbol):
        try:
            request = {"command": "stopTickPrices",
                       "symbol": symbol}
            self.stream_s.send(ujson.dumps(request).encode(FORMAT))
            logger.info(Fore.GREEN + f'Stop TickPrices request has been sent for symbol {symbol} ')
        except:
            logger.exception(Fore.RED + f"Couldn't send stopTickPrices request for symbol {symbol}")

    def streamBalance(self):
        self.stream_datas['balance'] = []
        try:
            request = {"command": "getBalance",
                       "streamSessionId": self.key}
            self.stream_s.send(ujson.dumps(request).encode(FORMAT))
            logger.debug(Fore.BLUE + f'Stream request getBalance has been sent')
        except:
            logger.exception(Fore.RED + 'Request not sent')

    def stopBalance(self):
        try:
            request = {"command": "stopBalance"}
            self.stream_s.send(ujson.dumps(request).encode(FORMAT))
            logger.info(Fore.GREEN + 'Stop Balance request has been sent')
        except:
            logger.exception(Fore.RED + f"Couldn't send stopBalance request")




if __name__ == '__main__':


    #TODO#         Uncomment and modify with your values for a quick first use


    # from data_processing import static_to_chartdataset
    # #!# Create an AccessAPI instance to access XTB JSON API
    # session = AccessAPI()
    #
    # #!# Create a stream of data
    # session.streamListeningInit()
    # session.streamTickPrices('EURUSD')
    # session.streamBalance()
    #
    # #!#Create a QuerySet
    # req = QuerySet('first_query')
    #
    # #!# Add queries to the QuerySet
    # symbols = ["EURUSD",
    #            'OIL.WTI',
    #            'GBPUSD'
    #            ]
    # req.getChartRange('hist_datas', symbols, 240, '2020-06-10 02:00:00',
    #                                                  '2020-07-24 12:00:00')
    # req.getChartRange('short_datas', symbols, 5, '2020-07-18 09:00:00',
    #                                                  '2020-07-24 19:00:00')
    #
    # req.getMarginTrade(*[('EURUSD', 1), ('GBPUSD', 1)])
    # req.getUserData()
    # logger.debug(Fore.BLUE + f'requests = {[query for query in req.queries]}')
    #
    #
    # #!# Pass the QuerySet to the API
    # session.staticDataRequest(req)
    # logger.debug(Fore.BLUE + f'datas = {[data for data in session.static_datas.keys()]}')
    #
    # #!# Process collected datas
    # datasets = static_to_chartdataset(session.static_datas)
    # logger.debug(Fore.BLUE + f'{datasets[0]}')
    # time.sleep(5)
    # session.stopTickPrices('EURUSD')
    # session.stopBalance()
    # session.streamListeningStop()
    # logger.debug(Fore.BLUE + f'{session.stream_datas}')
    # filelogger.debug(session.stream_datas)

    pass