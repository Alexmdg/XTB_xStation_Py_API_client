# xStation_Py_API_client
Python tools to communicate with the "XTB JSON API" and process the collected datas


# Quick Exemple

**Create an AccessAPI instance to access XTB JSON API**

    session = AccessAPI()

**Get datas from stream :**

    session.streamSocketInit('eurusd')
    session.streamTickPrices('eurusd', 'eurusd', 'EURUSD')

**Get datas from main port :**

*Create a QuerySet*

QuerySet is a class allowing to regroup lists of queries. Queries are "XTB api" json requests associated to a name.

    req = QuerySet('first_query')

**Add queries to the QuerySet**

    symbols = ["EURUSD",
               'OIL.WTI',
               'GBPUSD'
               ]
    req.getChartRange('hist_datas', symbols, 240, '2020-06-10 02:00:00',
                                                     '2020-06-10 12:00:00')
    req.getChartRange('short_datas', symbols, 5, '2020-07-18 09:00:00',
                                                     '2020-07-24 19:00:00')
    req.getMarginTrade(*[('EURUSD', 1), ('GBPUSD', 1)])
    req.getUserData()
    

**Pass the QuerySet to the API**

    session.staticDataRequest(req)
    

**Process collected datas**

    datasets = api_to_dataset(session.datas)
    time.sleep(10)
    session.is_socket_open['eurusd'] = False

