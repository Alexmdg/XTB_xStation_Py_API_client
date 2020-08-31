import os, sys, inspect, ssl, threading
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from PyXTB.api_access import QuerySet, AccessAPI
from PyXTB.data_processing import *
from PyXTB.settings import *

class Test_FromStaticTo:
    datas = {
        'Test_request_240_ChartRange_EURUSD': {
            "status": True,
            "returnData": {
                "digits": 4,
                "rateInfos": [{
                    "close": 1.0,
                    "ctm": 1389362640000,
                    "ctmString": "Jan 10, 2014 3:04:00 PM",
                    "high": 6.0,
                    "low": 0.0,
                    "open": 41848.0,
                    "vol": 0.0
                    }]
                }
            },
        'Test_request_240_ChartLast_EURUSD': {
            "status": True,
            "returnData": {
                "digits": 4,
                "rateInfos": [{
                    "close": 1.0,
                    "ctm": 1389362640000,
                    "ctmString": "Jan 10, 2014 3:04:00 PM",
                    "high": 6.0,
                    "low": 0.0,
                    "open": 41848.0,
                    "vol": 0.0
                }]
            }
        },
        }

    def test_static_to_chartdataset(self):
        errors=[]
        dataset = static_to_chartdataset(self.datas)
        log.dataIO.cmn_dbg(dataset)
        if not type(dataset['Test_request_240_ChartRange_EURUSD']) != type(pandas.DataFrame):
            errors.append(f'no dataframe: {type(dataset["Test_request_240_ChartRange_EURUSD"])}')
        if not type(dataset['Test_request_240_ChartRange_EURUSD']) != type(pandas.DataFrame):
            errors.append(f'no dataframe: {type(dataset["Test_request_240_ChartRange_EURUSD"])}')
        assert len(errors) == 0
