#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"

import tornado.web
from settings import config
from urls import url_patterns

application_settings = {
    'cookie_secret': config.cookie.secret,
    'xsrf_cookies': False,
    'login_url': '/',
}

application = tornado.web.Application(handlers=url_patterns, **application_settings)
