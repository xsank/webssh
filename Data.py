__author__ = 'xsank'

import json


class BaseData(object):
    def __init__(self,data=""):
        self.from_json(data)

    def from_json(self,data=""):
        self.__dict__=json.loads(data)

    def to_json(self):
        return json.dumps(self)


class InitData(BaseData):
    def __init__(self,data=""):
        super(InitData,self).__init__(data)
        self.tp="init"
        self.hostname="localhost"
        self.port=22
        self.username="root"
        self.password=""
        self.timeout=0


class CloseData(BaseData):
    def __init__(self,data=""):
        super(CloseData,self).__init__(data)
        self.tp="close"


class ClientData(BaseData):
    def __init__(self,data=""):
        super(ClientData,self).__init__(data)
        self.tp="client"


class ServerData(BaseData):
    def __init__(self,data=""):
        super(ServerData,self).__init__(data)
        self.tp="server"
