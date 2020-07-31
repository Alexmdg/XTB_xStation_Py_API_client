import os, sys, inspect, ssl, threading
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from api_access import QuerySet, AccessAPI
from settings import *


class TestQuerySet:
    qs = QuerySet('name')

    def test_queryset_init(self):
        errors = []
        if self.qs.name != 'name':
            errors.append('name')
        if type(self.qs.queries) != list:
            errors.append('list')
        assert len(errors) == 0

    def test_getUserData(self):
        errors = []
        x = len(self.qs.queries)
        self.qs.getUserData()
        if len(self.qs.queries) != x + 1:
            errors.append('query not added to queries')
        elif self.qs.queries[-1]['name'] != 'name_UserData':
            errors.append('query name issue')
        elif self.qs.queries[-1]['request'] != getUserDataRequest:
            errors.append('query request issue')
        assert len(errors) == 0

    def test_getMarginLevel(self):
        errors = []
        x = len(self.qs.queries)
        self.qs.getMarginLevel()
        if len(self.qs.queries) != x + 1:
            errors.append('query not added to queries')
        elif self.qs.queries[-1]['name'] != 'name_MarginLevel':
            errors.append('query name issue')
        elif self.qs.queries[-1]['request'] != getMarginLevelRequest:
            errors.append('query request issue')
        assert len(errors) == 0

    def test_getMarginTrade(self):
        errors = []
        args = [('EURUSD', 1), ('GBPUSD', 2)]
        request = {'command': 'getMarginTrade',
                   'arguments': {'symbol': 'GBPUSD',
                                 'volume': 2
                     }}
        x = len(self.qs.queries)
        self.qs.getMarginTrade(*args)
        if len(self.qs.queries) != x + 2:
            errors.append('number of queries created issue')
        elif self.qs.queries[-1]['name'] != 'name_MarginTrade_GBPUSD_2':
            errors.append('query name issue')
        elif self.qs.queries[-1]['request'] != request:
            errors.append('query request issue')
        assert len(errors) == 0

    def test_getCommissionDef(self):
        errors = []
        args = [('EURUSD', 1), ('OIL.WTI', 3)]
        request = {'command': 'getCommissionDef',
                   'arguments': {'symbol': 'OIL.WTI',
                                 'volume': 3
                     }}
        x = len(self.qs.queries)
        self.qs.getCommissionDef(*args)
        if len(self.qs.queries) != x + 2:
            errors.append('number of queries created issue')
        elif self.qs.queries[-1]['name'] != 'name_Commission_OIL.WTI_3':
            errors.append('query name issue')
        elif self.qs.queries[-1]['request'] != request:
            errors.append('query request issue')
        assert len(errors) == 0


    def test_getAllSymbols(self):
        errors = []
        x = len(self.qs.queries)
        self.qs.getAllSymbols()
        if len(self.qs.queries) != x + 1:
            errors.append('query not added to queries')
        elif self.qs.queries[-1]['name'] != 'name_AllSymbols':
            errors.append('query name issue')
        elif self.qs.queries[-1]['request'] != getAllSymbolsRequest:
            errors.append('query request issue')
        assert len(errors) == 0

    def test_getCalendar(self):
        errors = []
        x = len(self.qs.queries)
        self.qs.getCalendar()
        if len(self.qs.queries) != x + 1:
            errors.append('query not added to queries')
        elif self.qs.queries[-1]['name'] != 'name_Calendar':
            errors.append('query name issue')
        elif self.qs.queries[-1]['request'] != getCalendarRequest:
            errors.append('query request issue')
        assert len(errors) == 0

    def test_getChartRange(self):
        errors = []
        args = ['hist', ['OIL.WTI', 'GBPUSD', 'EURUSD'], 60, '2020-06-10 09:00:00', '2020-07-24 19:00:00']
        request = {'command': 'getChartRangeRequest',
                   'arguments': {'info': {'start': 1591772400000,
                                          'period': 60,
                                          'end': 1595610000000,
                                          'symbol': 'EURUSD'}
                                    }
                    }
        x = len(self.qs.queries)
        self.qs.getChartRange(*args)
        if len(self.qs.queries) != x + 3:
            errors.append('number of queries created issue')
        elif self.qs.queries[-1]['name'] != 'name_hist_ChartRange_EURUSD':
            errors.append('query name issue')
        elif self.qs.queries[-1]['request'] != request:
            errors.append('query request issue')
        assert len(errors) == 0


class TestAccessAPI:
    session = AccessAPI()
    qs = QuerySet('queryset')
    symbols = ["EURUSD",
               'OIL.WTI',
               'GBPUSD'
               ]
    qs.getChartRange('hist', symbols, 240, '2020-06-10 08:00:00',
                                                     '2020-06-10 12:00:00')
    qs.getMarginTrade(*[('EURUSD', 1), ('GBPUSD', 1)])
    qs.getUserData()

    def test_AccessAPI_init(self):
        errors = []
        if not self.session.static_s:
            errors.append('static socket')
        if type(self.session.key) != str or len(self.session.key) < 1:
            errors.append('session key')
        assert len(errors) == 0

    def test_staticDataRequest(self):

        errors = []
        self.session.staticDataRequest(self.qs)
        if len(self.session.datas) != 6:
            errors.append('wrong number of responses collected')
        assert len(errors) == 0

    def test_streamSocketInit(self):
        errors = []
        self.session.streamSocketInit(*['first', 'second', 'third'])
        if len(self.session.stream_socket_list) != 3:
            errors.append('number of socket')
        elif type(self.session.stream_socket_list['first']) != ssl.SSLSocket\
            or type(self.session.stream_socket_list['second']) != ssl.SSLSocket\
            or type(self.session.stream_socket_list['third']) != ssl.SSLSocket:
            errors.append(f"sockets name or type: {ssl.SSLSocket}")
            errors.append(f"sockets name or type: {type(self.session.stream_socket_list['first'])}")
            errors.append(f"sockets name or type: {type(self.session.stream_socket_list['second'])}")
            errors.append(f"sockets name or type: {type(self.session.stream_socket_list['third'])}")
        assert len(errors) == 0


    def test_streamTickPrices(self):
        errors = []
        self.session.streamTickPrices('first', 'EURUSD')
        if len(self.session.thread_list) != 1:
            errors.append('no thread in list')
        elif type(self.session.thread_list['first']) != threading.Thread:
            errors.append(f'thread name or type : {threading.Thread}')
            errors.append(f"thread name or type : {type(self.session.thread_list['first'])}")
        assert len(errors) == 0


    def test_stopTickPrices(self):
        errors = []
        self.session.stopTickPrices('first', 'EURUSD')
        if 'first' in self.session.stream_socket_list.keys():
            errors.append('socket not deleted from list')
        elif 'first' in self.session.thread_list.keys():
            errors.append('thread not deleted from list')
        elif 'first' in self.session.is_socket_open.keys():
            errors.append('is socket open not deleted')
        assert len(errors) == 0


    def test_streamBalance(self):
        errors = []
        self.session.streamBalance('second')
        if len(self.session.thread_list) != 1:
            errors.append('no thread in list')
        elif type(self.session.thread_list['second']) != threading.Thread:
            errors.append(f'thread name or type : {threading.Thread}')
            errors.append(f"thread name or type : {type(self.session.thread_list['second'])}")
        assert len(errors) == 0

    def test_stopBalance(self):
        errors = []
        self.session.stopBalance('second')
        if 'second' in self.session.stream_socket_list.keys():
            errors.append('socket not deleted from list')
        elif 'second' in self.session.thread_list.keys():
            errors.append('thread not deleted from list')
        elif 'second' in self.session.is_socket_open.keys():
            errors.append('is socket open not deleted')
        assert len(errors) == 0

    # def test__streamRecv(self):
    #     errors = []
    #     if not 'first' in self.session.stream_datas.keys():
    #         errors.append('no data registered from stream')
    #     elif not


