from api_access import AccessAPI, QuerySet
from settings import *


class ActiveWallet:

    def __init__(self, session):
        qs = QuerySet('wallet_init')
        qs.getUserData()
        qs.getMarginLevel()
        session.staticDataRequest(qs)
        self.funds = session.datas['wallet_init_UserData']['returnData']



