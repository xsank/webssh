__author__ = 'xsank'

from handlers import *

handlers = [
    (r"/", IndexHandler),
    (r"/login", IndexHandler),
    (r"/ws", WSHandler)
]
