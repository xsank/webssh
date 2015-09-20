__author__ = 'xsank'

from tornado.options import define


def init_config():
    define('port', default=9527, type=int, help='server listening port')
