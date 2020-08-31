import socket, ssl, time, threading, ujson

from tqdm import trange
from datetime import datetime
from api.settings import *


####            QuerySets are named lists of queries (static requests each associated to a name)           ####
class QuerySet:
    def __init__(self, name):
        self.name = name
        self.queries = []

    def getUserData(self):
        self.queries.append({'name': f'{self.name}_UserData',
                              'request': getUserDataRequest})
        log.qset.success(f"added {self.queries[-1]['name']} to the list of {self.name} queries")

    def getMarginLevel(self):
        self.queries.append({'name': f'{self.name}_MarginLevel',
                             'request': getMarginLevelRequest})
        log.qset.success(f"added {self.queries[-1]['name']} to the list of {self.name} queries")

    def getMarginTrade(self, *args):
        for query in args:
            self.queries.append({'name': f'{self.name}_MarginTrade_{query[0]}_{query[1]}',
                                'request': {'command': 'getMarginTrade',
                                            'arguments': {'symbol': query[0],
                                                          'volume': query[1]}
                                        }
                                 })
            log.qset.success(f"added {self.queries[-1]['name']} to the list of {self.name} queries")

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
            log.qset.success(f"added {self.queries[-1]['name']} to the list of {self.name} queries")

    def getAllSymbols(self):
        self.queries.append({'name': f'{self.name}_AllSymbols',
                              'request': getAllSymbolsRequest})
        log.qset.success(f"added {self.queries[-1]['name']} to the list of {self.name} queries")

    def getCalendar(self):
        self.queries.append({'name': f'{self.name}_Calendar',
                              'request': getCalendarRequest})
        log.qset.success(f"added {self.queries[-1]['name']} to the list of {self.name} queries")

    def getChartRange(self, name, symbols, period, start, end):
        #   args : (str, list of str, int, str(datetime), str(datetime))
        #   Will register a query in the queryset for each symbol of the list.
        start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        start_ts = datetime.timestamp(start)
        end_ts = datetime.timestamp(end)
        with log.cbugCheck(log.qset, 'getChartRange'):
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
                log.qset.success(f"added {self.queries[-1]['name']} to the list of {self.name} queries")



####        All communications with the XTB json API happen through an AccessAPI instance         ####
class AccessAPI:
    requests = []
    key = ''
    static_datas = {}
    stream_datas = {}
    is_streaming = False
    is_receiving = False

    def __init__(self, id, password):
        main_add = socket.getaddrinfo(SERVER, STATIC_PORT)[0][4][0]
        self.static_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.static_s.connect((main_add, STATIC_PORT))
        self.static_s = ssl.wrap_socket(self.static_s)
        stream_add = socket.getaddrinfo(SERVER, STREAM_PORT)[0][4][0]
        self.stream_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_s.connect((stream_add, STREAM_PORT))
        self.stream_s = ssl.wrap_socket(self.stream_s)
        self.stream_s.settimeout(25)
        with log.cbugCheck(log.static, func_name='Login'):
            self.static_s.send(ujson.dumps({"command": "login",
                                            "arguments": {"userId": id,
                                                         "password": password}}).encode(FORMAT))
            status = self.static_s.recv().decode(FORMAT)
            status = ujson.loads(status)
            self.key = status['streamSessionId']
            log.static.success('LOGIN : {}'.format(status))

    def staticDataRequest(self, *args):  #  feed with QuerySets
        with log.cbugCheck(log.static, func_name='static Data Request'):
            for queryset in args:
                for query in queryset.queries:
                    request = query['request']
                    name = query['name']
                    time.sleep(0.2)
                    log.static.spc_dbg(f'request {name} = {request}')
                    for _ in trange(len(args), bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.WHITE),
                                    desc=Fore.BLUE + "Downloading"):
                        self.static_s.send(ujson.dumps(request).encode(FORMAT))
                        data = self.static_s.recv().decode(FORMAT)
                        self.static_datas[name] = '' + data
                        while '\n\n' not in data:
                            data = self.static_s.recv().decode(FORMAT)
                            self.static_datas[name] = self.static_datas[name] + data
                        self.static_datas[name] = ujson.loads(self.static_datas[name])
                    if self.static_datas[name]['status'] is False:
                        log.static.info(Fore.RED + f"{name.upper()} : {self.static_datas[name]['status']}")
                        try:
                            log.static.error(self.static_datas[name]['errorDescr']\
                                         + '\n')
                        except:
                            log.static.exception(Fore.RED + 'Error not listed on API documentation')
                    else:
                        log.static.success(f"{name.upper()} : {self.static_datas[name]['status']}")

    def _streamRecv(self):
        self.is_receiving = True
        while self.is_streaming is True:
            data = ''
            try: data += self.stream_s.recv().decode(FORMAT)
            except: log.main.exception(Fore.RED + "Error while trying to receive")
            log.stream.cmn_dbg(f'{data}')
            try:
                if data != '':
                    data = ujson.loads(data.split('\n\n')[0])
                    if data['command'] == 'balance':
                        self.stream_datas['balance'].append(data)
                        log.stream.info(Fore.GREEN + f'datas added to stream_datas["balance"] list')
                    elif data['command'] == 'tickPrices':
                        self.stream_datas[f"tickPrices_{data['data']['symbol']}"].append(data['data'])
                        log.stream.info(Fore.GREEN+ "datas added to stream_datas['" + f"tickPrices_{data['data']['symbol']}] list")
            except Exception as e:
                log.stream.debug(Fore.RED + f'data = {type(data)} {data}' + Fore.RESET)
                log.stream.debug(Fore.RED + f'{e}' + Fore.RESET)
        self.is_receiving = False

    def streamListeningStart(self):
        try:
            self.is_streaming = True
            self.thread = threading.Thread(target=self._streamRecv)
            self.thread.start()
        except:
            log.stream.exception(Fore.RED + f'Exception while trying to open thread')

    def streamListeningStop(self):
        self.is_streaming = False
        self.thread.join()
        log.stream.info(Fore.GREEN + 'Listening thread terminated')

    def streamTickPrices(self, *symbols):
        for symbol in symbols:
            self.stream_datas[f"tickPrices_{symbol}"] = []
            try:
                request = {"command": "getTickPrices",
                           "streamSessionId": self.key,
                           "symbol": symbol,
                           "minArrivalTime": 1500,
                           "maxLevel": 2}
                self.stream_s.send(ujson.dumps(request).encode(FORMAT))
                log.stream.debug(Fore.GREEN + f'Stream request getTickPrices has been sent for symbol {symbol}')
            except:
                log.stream.exception(Fore.RED + "Couldn't open stream")

    def stopTickPrices(self, symbol):
        try:
            request = {"command": "stopTickPrices",
                       "symbol": symbol}
            self.stream_s.send(ujson.dumps(request).encode(FORMAT))
            log.stream.info(Fore.GREEN + f'Stop TickPrices request has been sent for symbol {symbol} ')
        except:
            log.stream.exception(Fore.RED + f"Couldn't send stopTickPrices request for symbol {symbol}")

    def streamBalance(self):
        self.stream_datas['balance'] = []
        try:
            request = {"command": "getBalance",
                       "streamSessionId": self.key}
            self.stream_s.send(ujson.dumps(request).encode(FORMAT))
            log.stream.debug(Fore.GREEN + f'Stream request getBalance has been sent')
        except:
            log.stream.exception(Fore.RED + 'Request not sent')

    def stopBalance(self):
        try:
            request = {"command": "stopBalance"}
            self.stream_s.send(ujson.dumps(request).encode(FORMAT))
            log.stream.info(Fore.GREEN + 'Stop Balance request has been sent')
        except:
            log.stream.exception(Fore.RED + f"Couldn't send stopBalance request")





if __name__ == '__main__':


    #TODO#         Uncomment and modify with your values for a quick first use


    # from api.data_processing import static_to_chartdataset
    # #!# Create an AccessAPI instance to access XTB JSON API
    # session = AccessAPI('11360828', 'A00000000')
    #
    # #!# Create a stream of data
    # session.streamListeningStart()
    # session.streamBalance()
    # time.sleep(2)
    # session.stopBalance()
    # session.streamTickPrices('EURUSD', 'GBPUSD')
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
    #
    #
    # #!# Pass the QuerySet to the API
    # session.staticDataRequest(req)
    #
    #
    # #!# Process collected datas
    # datasets = static_to_chartdataset(session.static_datas)
    # log.main.debug(Fore.BLUE + f'{datasets[0]}')
    # time.sleep(45)
    # session.stopTickPrices('EURUSD')
    # session.streamListeningStop()
    # log.main.debug(Fore.BLUE + f'{session.stream_datas}')

    pass