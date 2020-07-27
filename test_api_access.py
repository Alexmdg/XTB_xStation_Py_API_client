import pytest
from api_access import *
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
                   'arguments': {'info': {'start': 1591772400.0,
                                          'period': 60,
                                          'end': 1595610000.0,
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
        pass