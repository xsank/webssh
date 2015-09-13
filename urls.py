__author__ = 'xsank'

from handlers import *


handlers = [
    (r"/", IndexHandler),
    (r"/ws", WSHandler)
]
