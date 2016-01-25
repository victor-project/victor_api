#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"


from tornado import gen
import time
import tornado.web
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class IndexHandler(tornado.web.RequestHandler):
    # 使用多线程跑或者是使用多进程
    executor = ThreadPoolExecutor(2)

    @tornado.gen.coroutine
    def get(self):
        #调用下层API
        str = self.api_1()
        self.write(str)

    @run_on_executor
    def api_1(self):
        time.sleep(10)
        return "Hello Word"