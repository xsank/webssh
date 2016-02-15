__author__ = 'xsank'

import select
import socket
import errno
import logging
from threading import Thread

from utils import Platform


MAX_DATA_BUFFER = 1024*1024


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
            if Platform.is_linux():
                IOLoop._instance = EPollIOLoop()
            elif Platform.is_mac():
                IOLoop._instance = KQueueIOLoop()
            else:
                IOLoop._instance = SelectIOLoop()
        return IOLoop._instance

    def register(self, bridge):
        raise NotImplemented("the register method should be implemented")

    def _add_bridge(self, bridge):
        self.bridges[bridge.id] = bridge

    def add_future(self, future):
        fd = next(future)
        self.futures[fd] = future
        next(future)

    def close(self, fd):
        self.impl.unregister(fd)
        self.bridges[fd].detroy()
        del self.bridges[fd]


class EPollIOLoop(IOLoop):

    def __init__(self):
        super(EPollIOLoop, self).__init__(impl=select.epoll())

    def register(self, bridge):
        self._add_bridge(bridge)
        self.impl.register(bridge.id, select.EPOLLIN | select.EPOLLET)

    def run(self):
        while True:
            poll_list = self.impl.poll()
            for fd, events in poll_list:
                if select.EPOLLIN & events:
                    while True:
                        try:
                            data = self.bridges[fd].shell.recv(MAX_DATA_BUFFER)
                        except socket.error as e:
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
        super(SelectIOLoop, self).__init__(impl=select.select)
        self.read_fds = set()
        self.write_fds = set()
        self.error_fds = set()
        self.fd_sets = (self.read_fds, self.write_fds, self.error_fds)

    def register(self, bridge):
        self._add_bridge(bridge)
        self.read_fds.add(bridge.id)

    def run(self):
        import time
        while True:
            if self.read_fds:
                readable, writeable, errors = self.impl(
                    self.read_fds, self.write_fds, self.error_fds, 1)
                events = {}
                for fd in readable:
                    events[fd] = events.get(fd, 0) | self.READ
                for fd in errors:
                    events[fd] = events.get(fd, 0) | self.ERROR
                for fd, events in events.items():
                    if self.READ & events:
                        while True:
                            try:
                                data = self.bridges[fd].shell.recv(MAX_DATA_BUFFER)
                            except socket.error as e:
                                if isinstance(e, socket.timeout):
                                    break
                                else:
                                    self.close(fd)
                            try:
                                self.futures[fd].send(data)
                            except StopIteration:
                                break
                    elif self.ERROR & events:
                        self.close(fd)
                    else:
                        continue
            else:
                time.sleep(1)


class KQueueIOLoop(IOLoop):

    def __init__(self):
        super(KQueueIOLoop, self).__init__(impl=select.kqueue())

    def register(self, bridge):
        self._add_bridge(bridge)
        kevent = select.kevent(
            bridge.id, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_ADD)
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
                            data = self.bridges[fd].shell.recv(MAX_DATA_BUFFER)
                        except socket.error as e:
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
