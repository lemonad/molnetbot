#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
The MIT license

Copyright (c) 2010 Jonas Nockert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
---


Configuration for molnetbot.

Copy 'molnetbot.conf.sample' to 'molnetbot.conf' and edit options.

"""
from ConfigParser import ConfigParser
import subprocess


def version():
    """Get version number as latest git tag."""

    p = subprocess.Popen('git describe',
                         shell=True,
                         stdout=subprocess.PIPE)
    if p.poll() != 0:
        # Process exited with error, set version manually
        return "na"
    else:
        return proc.communicate()[0].strip()

config = ConfigParser()
config.read('molnetbot.conf')

# JID and password to use for this bot
JID = config.get('xmpp', 'jid')
PASSWORD = config.get('xmpp', 'password')

# notifications configuration
NOTIFY_JIDS = config.get('notifications', 'jids').split(' ')
NOTIFY_ON_SUBSCRIBES = config.getboolean('notifications',
                                         'notify_on_subscribes')
NOTIFY_ON_UNSUBSCRIBES = config.getboolean('notifications',
                                           'notify_on_unsubscribes')
NOTIFY_ON_QUERIES = config.getboolean('notifications',
                                      'notify_on_queries')

# smtp configuration
SMTP_HOST = config.get('smtp', 'host')
EMAIL_FROM = config.get('smtp', 'from')
EMAIL_TO = config.get('smtp', 'to').split(' ')

# API configuration
API_SEARCH_URL = config.get('molnet', 'api_search_url')

# vCard
AVATAR_IMAGE_PATH = config.get('vCard', 'avatar_path')

# Log traffic?
LOG_TRAFFIC = config.getboolean('debug', 'log_traffic')
