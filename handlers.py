__author__ = 'xsank'

import tornado.web
import tornado.websocket

from daemon import Bridge


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")


class WSHandler(tornado.websocket.WebSocketHandler):

    clients=dict()

    def get_client(self):
        return self.clients[self._id()]

    def put_client(self):
        bridge=Bridge(self)
        self.clients[self._id()]=bridge

    def remove_client(self):
        bridge=self.get_client()
        bridge.destroy()
        del self.clients[self._id()]

    @staticmethod
    def _is_init_data(message):
        return 'init' in message

    def _id(self):
        return id(self)

    def open(self):
        self.put_client()

    def on_message(self, message):
        bridge=self.get_client()
        if self._is_init_data():
            bridge.open(message)
        else:
            bridge.trans_data(message)

    def on_close(self):
        self.remove_client()