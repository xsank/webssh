__author__ = 'mazheng'

import select
import socket
from threading import Thread


class IOLoop(Thread):

    def __init__(self):
        super(IOLoop,self).__init__()
        self.select=select.epoll()
        self.connections={}
        self.websockets={}

    @staticmethod
    def instance():
        if not hasattr(IOLoop,"_instance"):
            IOLoop._instance=IOLoop()
        return IOLoop._instance

    def register(self,fileno,connection,websocket):
        self.select.register(fileno,select.EPOLLIN)
        self.connections[fileno]=connection
        self.websockets[fileno]=websocket

    def run(self):
        while True:
            epoll_list=self.select.poll(1)
            for fd,events in epoll_list:
                print fd,events
                if select.EPOLLIN & events:
                    error=False
                    while True:
                        try:
                            data = self.connections[fd].recv(1024)
                        except socket.error:
                            error=True
                        if not data or error:
                            break
                        self.websockets[fd].write_message(data)
                elif select.EPOLLHUP & events:
                    self.close()
                else:
                    continue

    def close(self,fd):
        self.select.unregister(fd)
        self.connections[fd].close()
        self.websockets[fd].close()
        del self.connections[fd]
        del self.websockets[fd]
