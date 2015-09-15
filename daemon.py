__author__ = 'mazheng'

import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException

from data import ServerData
from ioloop import IOLoop


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
                port=int(data["port"]),
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

        fileno = self.shell.fileno()
        connection = self.shell
        websocket = self.websocket
        IOLoop.instance().register(fileno, connection, websocket)

    def trans_forward(self, data=""):
        self.shell.send(data)

    def trans_data(self, data=""):
        self.trans_forward(data)

    def destroy(self):
        self.websocket.close()
        self.ssh.close()
