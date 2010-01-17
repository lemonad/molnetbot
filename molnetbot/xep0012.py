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


XEP-0012: Last Activity handler

"""
from datetime import datetime
import time

from twisted.words.protocols.jabber.xmlstream import toResponse
from wokkel.subprotocols import IQHandlerMixin, XMPPHandler


NS_LAST_ACTIVITY = 'jabber:iq:last'
LAST_ACTIVITY = '/iq[@type="get"]/query[@xmlns="' + NS_LAST_ACTIVITY +'"]'


class LastActivityHandler(XMPPHandler, IQHandlerMixin):
    """
    XMPP subprotocol handler for Last Activity extension.

    This protocol is described in
    U{XEP-0012<http://www.xmpp.org/extensions/xep-0012.html>}.

    """
    iqHandlers = {LAST_ACTIVITY: 'onLastActivityGet'}

    def __init__(self, get_last=lambda: 0):
        self.get_last = get_last

    def connectionInitialized(self):
        self.xmlstream.addObserver(LAST_ACTIVITY, self.handleRequest)

    def onLastActivityGet(self, iq):
        """Handle a request for last activity."""

        response = toResponse(iq, 'result')
        # TODO: Replace 'hello world!' string with something proper.
        query = response.addElement((NS_LAST_ACTIVITY, 'query'),
                                    content="Hello world!")
        query['seconds'] = str(self.get_last())

        self.send(response)
        iq.handled = True
