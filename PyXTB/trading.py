from api.api_access import AccessAPI, QuerySet
import time


class ActiveWallet():

    def __init__(self, id, password):
        self.session = AccessAPI(id, password)
        self.session.streamListeningStart()
        self.session.streamBalance()
        time.sleep(2)
        self.session.stopBalance()
        self.session.streamListeningStop()
        qs = QuerySet('wallet_init')
        qs.GetUserData()
        qs.getAllSymbols()
        self.session.staticDataRequest(qs)
        self.symbols = []
        for symbol in self.session.static_datas['wallet_init_AllSymbols']:
            self.symbols.append({'symbol': symbol['symbol'],
                                 'currency': symbol['currency'],
                                 'category': symbol['categoryName'],
                                 'pip': symbol['tickValue'],
                                 'lot': symbol['contractSize']
                             })
        self.balance = self.session.stream_datas['balance']['data']['balance']
        self.margin = self.session.stream_datas['balance']['data']['margin']
        self.leverage = self.session.static_datas['wallet_init_UserData']['returnData']['leverageMultiplier']
        self.currency = self.session.static_datas['wallet_init_UserData']['returnData']['currency']














