from api.api_access import AccessAPI


class ActiveWallet():

    def __init__(self):
        self.access_api = AccessAPI()
        self.access_api.streamListeningStart()
        self.access_api.streamBalance()











