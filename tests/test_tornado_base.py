#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"

import tornado
from app import application
from tornado.testing import AsyncTestCase
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import AsyncHTTPClient

# This test uses coroutine style.
class MyTestCase(AsyncTestCase):
    @tornado.testing.gen_test
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        response = yield client.fetch("http://www.baidu.com")
        # Test contents of response
        print(response)
        #self.assertIn("FriendFeed", response.body)

    def test_http_fetch_v1(self):
        print("hello")
        client = AsyncHTTPClient(self.io_loop)
        client.fetch("http://www.baidu.com/", self.stop)
        response = self.wait()
        print(response)
        # Test contents of response
        # self.assertIn("FriendFeed", response.body)

# This test uses argument passing between self.stop and self.wait.
class MyTestCase2(AsyncTestCase):
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        client.fetch("http://www.baidu.com/", self.stop)
        response = self.wait()
        print(response)
        # Test contents of response
        # self.assertIn("FriendFeed", response.body)

# This test uses an explicit callback-based style.
class MyTestCase3(AsyncTestCase):
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        client.fetch("http://www.baidu.com/", self.handle_fetch)
        self.wait()

    def handle_fetch(self, response):
        print(response)
        # Test contents of response (failures and exceptions here
        # will cause self.wait() to throw an exception and end the
        # test).
        # Exceptions thrown here are magically propagated to
        # self.wait() in test_http_fetch() via stack_context.
        # self.assertIn("FriendFeed", response.body)
        self.stop()

class MyHTTPTest(AsyncHTTPTestCase):
    def get_app(self):

        return application

    def test_homepage(self):
        # The following two lines are equivalent to
        #   response = self.fetch('/')
        # but are shown in full here to demonstrate explicit use
        # of self.stop and self.wait.
        self.http_client.fetch(self.get_url('/'), self.stop)

        response = self.wait()
        # print(response)
        print(response.body)
        # test contents of response