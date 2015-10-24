__author__ = 'xsank'

import select
import socket
import errno
import logging
from threading import Thread

from utils import Platform


class IOLoop(Thread):

    READ = 0x001
    WRITE = 0x004
    ERROR = 0x008 | 0x010

    def __init__(self, impl):
        super(IOLoop, self).__init__()
        self.daemon = True
        self.impl = impl
        self.bridges = {}
        self.futures = {}

    @staticmethod
    def instance():
        if not hasattr(IOLoop, "_instance"):
            if Platform.is_win():
                IOLoop._instance = SelectIOLoop()
            elif Platform.is_mac():
                IOLoop._instance = KQueueIOLoop()
            else:
                IOLoop._instance = EPollIOLoop()
        return IOLoop._instance

    def register(self, bridge):
        raise NotImplemented("the register method should be implemented")

    def add_future(self, future):
        fileno = future.next()
        self.futures[fileno] = future
        future.next()

    def close(self, fd):
        self.impl.unregister(fd)
        self.bridges[fd].detroy()
        del self.bridges[fd]


class EPollIOLoop(IOLoop):

    def __init__(self):
        super(EPollIOLoop, self).__init__(impl=select.epoll())

    def register(self, bridge):
        fileno = bridge.id
        self.impl.register(fileno, select.EPOLLIN | select.EPOLLET)
        self.bridges[fileno] = bridge

    def run(self):
        while True:
            poll_list = self.impl.poll()
            for fd, events in poll_list:
                if select.EPOLLIN & events:
                    while True:
                        try:
                            data = self.bridges[fd].shell.recv(1024)
                        except socket.error, e:
                            if e.errno == errno.EAGAIN:
                                self.impl.modify(fd, select.EPOLLET)
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


class SelectIOLoop(IOLoop):

    def __init__(self):
        super(SelectIOLoop, self).__init__(impl=select.select())

    def register(self, bridge):
        pass

    def run(self):
        pass


class KQueueIOLoop(IOLoop):

    def __init__(self):
        super(KQueueIOLoop, self).__init__(impl=select.kqueue())

    def register(self, bridge):
        fileno = bridge.id
        self.bridges[fileno] = bridge
        kevent = select.kevent(
            fileno, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_ADD)
        self.impl.control([kevent], 0)

    def run(self):
        while True:
            kevents = self.impl.control(None, 1000, 1)
            events = {}
            for kevent in kevents:
                fd = kevent.ident
                if kevent.filter == select.KQ_FILTER_READ:
                    events[fd] = events.get(fd, 0) | self.READ
                if kevent.flags & select.KQ_EV_ERROR:
                    events[fd] = events.get(fd, 0) | self.ERROR
            for fd, events in events.items():
                if select.KQ_FILTER_READ & events:
                    while True:
                        try:
                            data = self.bridges[fd].shell.recv(1024)
                        except socket.error, e:
                            if isinstance(e, socket.timeout):
                                break
                            else:
                                self.close(fd)
                        try:
                            self.futures[fd].send(data)
                        except StopIteration:
                            break
                elif select.KQ_EV_ERROR & events:
                    self.close(fd)
                else:
                    continue
