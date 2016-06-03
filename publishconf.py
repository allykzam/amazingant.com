#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = "https://amazingant.com"
RELATIVE_URLS = False

FEED_DOMAIN = SITEURL
FEED_MAX_ITEMS = 20
FEED_ATOM = "feeds/atom.xml"
FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/%s.atom.xml"

DELETE_OUTPUT_DIRECTORY = True
