import socket
import telnetlib
import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException
from tornado.websocket import WebSocketClosedError
from ioloop import IOLoop
from keycode import KEY_BS, KEY_ESC, KEY_DEL

__author__ = 'xsank'


class Bridge(object):
    def __init__(self, websocket):
        self._websocket = websocket
        self._shell = None
        self._id = 0
        self.ssh = None

    @property
    def id(self):
        return self._id

    @property
    def websocket(self):
        return self._websocket

    @property
    def shell(self):
        return self._shell

    def open(self, data={}):
        raise NotImplemented("the open method should be implemented")

    def wrap_recv_data(self, data):
        return data

    def wrap_send_data(self, data):
        return data

    def trans_forward(self, data=""):
        if self._shell:
            self._shell.send(self.wrap_recv_data(data))

    def trans_back(self):
        yield self.id
        connected = True
        while connected:
            result = yield
            result = self.wrap_send_data(result)
            try:
                result = unicode(result, 'utf-8')
            except UnicodeDecodeError:
                try:
                    result = unicode(result, 'gbk')
                except UnicodeDecodeError:
                    pass
            if self._websocket:
                try:
                    self._websocket.write_message(result)
                except WebSocketClosedError:
                    connected = False
                if result.strip() == 'logout':
                    connected = False
            else:
                connected = False
        self.destroy()

    def destroy(self):
        self._websocket.close()
        self.ssh.close()


class SSHBridge(Bridge):
    def open(self, data={}):
        self.ssh = paramiko.SSHClient()
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
        self._shell = self.ssh.invoke_shell(term)
        self._shell.setblocking(0)

        self._id = self._shell.fileno()
        IOLoop.instance().register(self)
        IOLoop.instance().add_future(self.trans_back())


class TELNETBridge(Bridge):
    def open(self, data={}):
        self.ssh = telnetlib.Telnet()
        try:
            self.ssh.open(
                data["hostname"],
                port=int(data["port"])
            )
            self.ssh.set_debuglevel(2)
        except Exception as e:
            raise e
        else:
            self.ssh.read_until("login: ")
            self.ssh.write(data["username"].encode('utf-8') + "\r\n")
            if data["password"]:
                self.ssh.read_until("password: ")
                self.ssh.write(data["password"].encode('utf-8') + "\r\n")
        self._shell = self.ssh
        self._shell.send = self.ssh.write
        self._shell.recv = self._ssh_recv
        self._id = self._shell.fileno()
        IOLoop.instance().register(self)
        IOLoop.instance().add_future(self.trans_back())

    def _ssh_recv(self, max_byte):
        try:
            data = self.ssh.read_very_eager()
        except EOFError:
            raise socket.error
        if len(data) == 0:
            raise socket.timeout
        return data

    def wrap_send_data(self, data):
        try:
            if ord(data) == KEY_BS:
                data = chr(KEY_BS) + chr(KEY_ESC) + '[K'
        except Exception:
            pass
        return data

    def wrap_recv_data(self, data):
        try:
            if ord(data) == KEY_DEL:
                data = chr(KEY_BS)
        except Exception:
            pass
        return data.encode('utf-8')

