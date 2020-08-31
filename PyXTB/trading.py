from PyXTB.api_access import AccessAPI, QuerySet
from PyXTB.settings import log
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
        qs.getUserData()
        qs.getAllSymbols()
        self.session.staticDataRequest(qs)
        self.symbols = []
        with log.cbugCheck(log.main):
            for symbol in self.session.static_datas['wallet_init_AllSymbols']['returnData']:
                self.symbols.append({'symbol': symbol['symbol'],
                                     'currency': symbol['currency'],
                                     'category': symbol['categoryName'],
                                     'pip': symbol['tickValue'],
                                     'lot': symbol['contractSize']
                                 })
        self.balance = self.session.stream_datas['balance'][0]['data']['balance']
        self.margin = self.session.stream_datas['balance'][0]['data']['margin']
        self.leverage = self.session.static_datas['wallet_init_UserData']['returnData']['leverageMultiplier']
        self.currency = self.session.static_datas['wallet_init_UserData']['returnData']['currency']

    def newSubWallet(self, name, percentage, symbols):
        pass


if __name__ == '__main__':
    trading = ActiveWallet('11360828', 'A00000000')
    log.main.debug(f'{trading.balance}')




