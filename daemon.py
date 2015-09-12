__author__ = 'mazheng'

import paramiko

from data import ClientData,ServerData,InitData


class Bridge(object):

    def __init__(self,websocket):
        self.websocket=websocket
        self.ssh=paramiko.SSHClient()
        self.shell=None

    def open(self,data=""):
        init_data=InitData(data)
        self._ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        self.ssh.connect(
            hostname=init_data.hostname,
            port=init_data.port,
            username=init_data.username,
            password=init_data.password,
            timeout=init_data.timeout
        )
        self.establish()

    def establish(self,term="xterm"):
        self.shell=self.ssh.invoke_shell(term)
        self.shell.setblocking(False)
        self.shell.settimeout(0)

    def trans_forward(self,data=""):
        data=ClientData(data)
        self.shell.send(data)

    def trans_back(self):
        while True:
            data=self.shell.recv(1024)
            if not data:
                return
            self.websocket.write_message(ServerData(data))

    def trans_data(self,data=""):
        self.trans_forward(data)
        self.trans_back()

    def destroy(self):
        self.websocket.close()
        self.ssh.close()