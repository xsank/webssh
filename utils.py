__author__ = 'xsank'

import re


def check_ip(ip):
    pattern = re.compile(
        '^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    return True if pattern.match(ip) else False


def check_port(port):
    if port and port.isdigit():
        iport = int(port)
        return iport < 65536 and iport > 0
    return False
