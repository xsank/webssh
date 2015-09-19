__author__ = 'xsank'

import select
import socket
import errno
from threading import Thread

from tornado.websocket import WebSocketClosedError


class IOLoop(Thread):

    def __init__(self):
        super(IOLoop, self).__init__()
        self.daemon = True
        self.select = select.epoll()
        self.connections = {}
        self.websockets = {}

    @staticmethod
    def instance():
        if not hasattr(IOLoop, "_instance"):
            IOLoop._instance = IOLoop()
        return IOLoop._instance

    def register(self, fileno, connection, websocket):
        self.select.register(fileno, select.EPOLLIN | select.EPOLLET)
        self.connections[fileno] = connection
        self.websockets[fileno] = websocket

    def run(self):
        while True:
            epoll_list = self.select.poll()
            for fd, events in epoll_list:
                if select.EPOLLIN & events:
                    while True:
                        try:
                            data = self.connections[fd].recv(1024)
                        except socket.error, e:
                            if e.errno == errno.EAGAIN:
                                self.select.modify(fd, select.EPOLLET)
                            elif isinstance(e, socket.timeout):
                                break
                            else:
                                self.close(fd)
                        try:
                            self.websockets[fd].write_message(data)
                        except WebSocketClosedError:
                            break
                elif select.EPOLLHUP & events:
                    self.close(fd)
                else:
                    continue

    def close(self, fd):
        self.select.unregister(fd)
        self.connections[fd].close()
        self.websockets[fd].close()
        del self.connections[fd]
        del self.websockets[fd]
