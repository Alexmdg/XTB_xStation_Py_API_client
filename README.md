# xStation_Py_API_client
Python tools to communicate with the "XTB JSON API" and process the collected datas


# Quick Exemple

**Create an AccessAPI instance to access XTB JSON API**

    session = AccessAPI()

**Create a stream of data**

    session.streamSocketInit('eurusd')
    session.streamTickPrices('eurusd', 'eurusd', 'EURUSD')

**Create a QuerySet**

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
    logger.debug(Fore.BLUE + f'requests = {[query for query in req.queries]}')


**Pass the QuerySet to the API**

    session.staticDataRequest(req)
    logger.debug(Fore.BLUE + f'datas = {session.datas}')

**Process collected datas**

    datasets = api_to_dataset(session.datas)
    logger.debug(Fore.BLUE + f'{datasets[0]}')
    time.sleep(2)
    session.is_socket_open['eurusd'] = False
    logger.debug(Fore.BLUE + f'{session.stream_datas}')
