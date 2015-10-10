__author__ = 'xsank'

import re
import functools
from threading import Lock

from ioloop import IOLoop


def check_ip(ip):
    pattern = re.compile(
        '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    return True if pattern.match(ip) else False


def check_port(port):
    if port and port.isdigit():
        iport = int(port)
        return iport < 65536 and iport > 0
    return False


def routine(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        future = func(*args, **kwargs)
        IOLoop.instance().add_future(future)
    return wrapper
