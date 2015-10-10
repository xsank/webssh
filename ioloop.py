__author__ = 'xsank'

import select
import socket
import errno
import logging
from threading import Thread


class IOLoop(Thread):

    def __init__(self):
        super(IOLoop, self).__init__()
        self.daemon = True
        self.select = select.epoll()
        self.bridges = {}
        self.futures = {}

    @staticmethod
    def instance():
        if not hasattr(IOLoop, "_instance"):
            IOLoop._instance = IOLoop()
        return IOLoop._instance

    def register(self, bridge):
        fileno = bridge.id
        self.select.register(fileno, select.EPOLLIN | select.EPOLLET)
        self.bridges[fileno] = bridge

    def add_future(self, future):
        fileno = future.next()
        self.futures[fileno] = future
        future.next()

    def run(self):
        while True:
            epoll_list = self.select.poll()
            for fd, events in epoll_list:
                if select.EPOLLIN & events:
                    while True:
                        try:
                            data = self.bridges[fd].shell.recv(1024)
                        except socket.error, e:
                            if e.errno == errno.EAGAIN:
                                self.select.modify(fd, select.EPOLLET)
                            elif isinstance(e, socket.timeout):
                                break
                            else:
                                self.close(fd)
                        try:
                            self.futures[fd].send(data)
                        except StopIteration:
                            break
                elif select.EPOLLHUP & events:
                    self.close(fd)
                else:
                    continue

    def close(self, fd):
        self.select.unregister(fd)
        self.bridges[fd].detroy()
        del self.bridges[fd]
