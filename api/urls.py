#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "tamchen"

from handlers import *

url_patterns = [
    # admin overview
    (r"/victor/hello?", HelloVictorHandler)
]