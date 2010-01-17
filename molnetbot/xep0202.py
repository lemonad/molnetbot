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

XEP-0202: Entity Time handler

"""
from datetime import datetime
import time

from twisted.words.protocols.jabber.xmlstream import toResponse
from wokkel.subprotocols import IQHandlerMixin, XMPPHandler


NS_ENTITY_TIME = 'urn:xmpp:time'
ENTITY_TIME = '/iq[@type="get"]/time[@xmlns="' + NS_ENTITY_TIME +'"]'


class EntityTimeHandler(XMPPHandler, IQHandlerMixin):
    """
    XMPP subprotocol handler for Entity Time extension.

    This protocol is described in
    U{XEP-0202<http://www.xmpp.org/extensions/xep-0202.html>}.

    """
    iqHandlers = {ENTITY_TIME: 'onEntityTimeGet'}

    def connectionInitialized(self):
        self.xmlstream.addObserver(ENTITY_TIME, self.handleRequest)

    def onEntityTimeGet(self, iq):
        """Handle a request for entity time."""

        response = toResponse(iq, 'result')
        entity_time = response.addElement((NS_ENTITY_TIME, 'time'))

        tzo_str = self._get_timezone_offset_str()
        utc_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        tzo = entity_time.addElement('tzo', content=tzo_str)
        utc = entity_time.addElement('utc', content=utc_str)

        self.send(response)
        iq.handled = True

    def _get_timezone_offset_str(self, timestamp=None):
        """Creates a time zone offset string.

        Seems like there should be a cleaner way to do it but at least
        it's the same method that Twisted, Bazaar and others use.

        """
        if timestamp is None:
            timestamp = time.time()
        offset = (datetime.fromtimestamp(timestamp) -
                  datetime.utcfromtimestamp(timestamp))
        offset_seconds = offset.days * 86400 + offset.seconds
        return "%+03d:%02d" % (offset_seconds / 3600,
                               offset_seconds / 60 % 60)
