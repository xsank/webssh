__author__ = 'xsank'

import tornado.web
import tornado.websocket

from daemon import Bridge
from data import ClientData


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")


class WSHandler(tornado.websocket.WebSocketHandler):

    clients = dict()

    def get_client(self):
        return self.clients[self._id()]

    def put_client(self):
        bridge = Bridge(self)
        self.clients[self._id()] = bridge

    def remove_client(self):
        bridge = self.get_client()
        bridge.destroy()
        del self.clients[self._id()]

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
            bridge.open(client_data.data)
        else:
            bridge.trans_data(client_data.data)

    def on_close(self):
        self.remove_client()
