#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"

import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options
from app import application

define("port", default=9000, help="Run server on a specific port", type=int)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    print 'Tornado listening on: %s' % options.port
    tornado.ioloop.IOLoop.instance().start()