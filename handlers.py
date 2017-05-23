from ioloop import IOLoop
import logging
import tornado.web
import tornado.websocket
from daemon import SSHBridge, TELNETBridge
from data import ClientData
from utils import check_ip, check_port

__author__ = 'xsank'


SSH_PROTOCOL = 1
TELNET_PROTOCOL = 2


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")


class WSHandler(tornado.websocket.WebSocketHandler):
    clients = dict()

    def check_origin(self, origin):
        return True

    def get_client(self):
        return self.clients.get(self._id(), None)

    def put_client(self):
        server_protocol = int(self.get_query_argument('server', SSH_PROTOCOL))
        if server_protocol == SSH_PROTOCOL:
            bridge = SSHBridge(self)
        elif server_protocol == TELNET_PROTOCOL:
            bridge = TELNETBridge(self)
        else:
            bridge = SSHBridge(self)
        self.clients[self._id()] = bridge

    def remove_client(self):
        bridge = self.get_client()
        if bridge:
            IOLoop.instance().close(bridge.id)
            bridge.destroy()
            del self.clients[self._id()]

    @staticmethod
    def _check_init_param(data):
        return check_ip(data["hostname"]) and check_port(data["port"])

    @staticmethod
    def _is_init_data(data):
        return data.get_type() == 'init'

    def _id(self):
        return id(self)

    def open(self):
        self.put_client()

    def on_message(self, message):
        bridge = self.get_client()
        client_data = ClientData(message)
        if self._is_init_data(client_data):
            if self._check_init_param(client_data.data):
                bridge.open(client_data.data)
                logging.info('connection established from: %s' % self._id())
            else:
                self.remove_client()
                logging.warning('init param invalid: %s' % client_data.data)
        else:
            if bridge:
                bridge.trans_forward(client_data.data)

    def on_close(self):
        self.remove_client()
        logging.info('client close the connection: %s' % self._id())
