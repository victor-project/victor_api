#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"

from handlers.hello import *

url_patterns = [
    # admin overview
    (r"/victor/hello?", HelloVictorHandler),
    (r"/?", HelloVictorHandler)
]