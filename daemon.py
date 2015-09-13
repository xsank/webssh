__author__ = 'mazheng'

import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException

from data import ServerData


class Bridge(object):

    def __init__(self, websocket):
        self.websocket = websocket
        self.ssh = paramiko.SSHClient()
        self.shell = None

    def open(self, data={}):
        self.ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(
                hostname=data["hostname"],
                port=data["port"],
                username=data["username"],
                password=data["password"],
            )
        except AuthenticationException:
            raise Exception("auth failed user:%s ,passwd:%s" %
                            (data["username"], data["password"]))
        except SSHException:
            raise Exception("could not connect to host:%s:%s" %
                            (data["hostname"], data["port"]))

        self.establish()

    def establish(self, term="xterm"):
        self.shell = self.ssh.invoke_shell(term)
        self.shell.setblocking(0)

    def trans_forward(self, data=""):
        self.shell.send(data)

    def trans_back(self):
        while True:
            try:
                data = self.shell.recv(1024)
            except Exception:
                return
            if not data:
                return
            self.websocket.write_message(data)

    def trans_data(self, data=""):
        self.trans_forward(data)
        self.trans_back()

    def destroy(self):
        self.websocket.close()
        self.ssh.close()
