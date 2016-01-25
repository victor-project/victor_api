#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"


import tornado.web
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer

class HelloVictorHandler(tornado.web.RequestHandler):

    def get(self):
        return self.write("Hello, world")


class Server(TCPServer):
    @coroutine
    def handle_stream(self, stream, address):
        try:
            yield stream.read_bytes(1024, partial=True)
            yield stream.write(b'HTTP 1.0 200 OK\r\n\r\nhello world')
        finally:
            stream.close()


server = Server()
server.bind(8000)
server.start(1)
IOLoop.current().start()