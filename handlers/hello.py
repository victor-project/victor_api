#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"


import tornado.web

class HelloVictorHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")