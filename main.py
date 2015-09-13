__author__ = 'xsank'

import os.path

import tornado.ioloop
import tornado.web
import tornado.httpserver


from urls import handlers


settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    port=8888,
)


class Application(tornado.web.Application):

    def __init__(self):
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(settings['port'])
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
