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

"""
import re
import sys
import time
import urllib

from email.mime.text import MIMEText
from twisted.mail.smtp import sendmail
from twisted.web import client
from twisted.words.xish import domish
from wokkel.xmppim import (MessageProtocol, AvailablePresence,
                           PresenceProtocol)

import config


def _build_notification(content):
    """Builds a xmpp notification element for admins."""

    notification = domish.Element((None, 'message'))
    notification['from'] = config.JID
    # type 'headline' is more appropriate really but headlines
    # are often displayed in a dialog so that's not cool
    notification['type'] = 'chat'
    notification.addElement('body', content=content)
    return notification
    

class PresenceAcceptingHandler(PresenceProtocol):
    """
    Presence accepting XMPP subprotocol handler.

    This handler blindly accepts incoming presence subscription requests,
    confirms unsubscription requests and responds to presence probes.

    Note that this handler does not remember any contacts, so it will not
    send presence when starting.

    """
    def subscribedReceived(self, presence):
        """
        Subscription approval confirmation was received.

        This is just a confirmation so no need to respond. Send out
        notifications if configured for it.

        """
        if config.NOTIFY_ON_SUBSCRIBES:
            content = "%s subscribed." % presence.sender.full()
            self._notify(content)

    def unsubscribedReceived(self, presence):
        """
        Unsubscription confirmation was received.

        This is just a confirmation so no need to respond. Send out
        notifications if configured for it.

        """
        if config.NOTIFY_ON_UNSUBSCRIBES:
            content = "%s unsubscribed." % presence.sender.full()
            self._notify(content)

    def subscribeReceived(self, presence):
        """
        Subscription request was received.

        Always grant permission to see our presence.

        """
        self.subscribed(recipient=presence.sender,
                        sender=presence.recipient)
        self.available(recipient=presence.sender,
                       status=u"Hej!",
                       sender=presence.recipient)
                       
        reply = domish.Element((None, 'message'))
        reply['to'] = presence.sender.full()
        reply['from'] = presence.recipient.full()
        reply['type'] = 'chat'
        reply.addElement('body', content="Hej hej!")
        self.send(reply)

    def unsubscribeReceived(self, presence):
        """
        Unsubscription request was received.

        Always confirm unsubscription requests.

        """
        self.unsubscribed(recipient=presence.sender,
                          sender=presence.recipient)

    def probeReceived(self, presence):
        """
        Presence probe was received.

        Always send available presence to whoever is asking.
        
        TODO: Perhaps we don't need to set status here?

        """
        self.available(recipient=presence.sender,
                       status=u"Queries goes here!",
                       sender=presence.recipient)

    def _notify(self, content):
        """Notify admins through xmpp."""

        notification = _build_notification(content)
        for jid in config.NOTIFY_JIDS:
            notification['to'] = jid
            self.send(notification)


class QueryHandler(MessageProtocol):
    """
    Replies to queries received from subscribed users by
    submitting their queries to the API backend and returning
    the results via xmpp messages.

    """
    def connectionMade(self):
        """
        Set "away" message on connection.
        
        TODO: Re-read xmpp specs to see if presence _really_ needs to go out twice.
        
        """
        self.send(AvailablePresence())
        s = {'en': u"Hello!",
             'sv': u"Hej!",
             'es': u"Hola!"}
        self.send(AvailablePresence(statuses=s))

    def onMessage(self, msg):
        """
        Handle incoming chat messages by forwarding the query to the
        backend API via HTTP.
        
        Send out notifications if configured for it.
        
        """
        if msg.getAttribute('type') == 'chat' \
                and hasattr(msg, 'body') \
                and getattr(msg, 'body') != None:
            query = msg.body
            deferred = client.getPage(config.API_SEARCH_URL, timeout=20)
            deferred.addCallbacks(self._answer_query,
                                  self._query_error,
                                  callbackArgs=(query,
                                                msg['from'],
                                                msg['to']),
                                  errbackArgs=(query,
                                               msg['from'],
                                               msg['to']))
            if config.NOTIFY_ON_QUERIES:
                content = "%s sent query '%s'." % (msg['from'], query)
                self._notify(content)

    def _notify(self, content):
        """Notify admins through xmpp."""

        notification = _build_notification(content)
        for jid in config.NOTIFY_JIDS:
            notification['to'] = jid
            self.send(notification)

    def _answer_query(self, result, query, sender, recipient):
        """
        Handle query results from backend API.
        
        TODO: Replace fake results with actual API results.

        """
        reply = domish.Element((None, 'message'))
        reply['to'] = sender
        reply['from'] = recipient
        reply['type'] = 'chat'
        # Add results as both regular text and html. It's up to the xmpp
        # client to decide which version to render.
        reply.addElement('body', content=u"Bob Smith, Developer, (123) 456-789.")
        html = domish.Element(('http://jabber.org/protocol/xhtml-im', 'html'))
        html_body = domish.Element(('http://www.w3.org/1999/xhtml', 'body'))
        html_body.addRawXml(u"<a href=\"mailto:bobsmith@example.com\">Bob Smith</a>, Developer, (123) 456-789.")
        html.addChild(html_body)
        reply.addChild(html)
        self.send(reply)


    def _query_error(self, error, query, sender, recipient):
        """
        Handle failed API queries.
        
        Send out email notifications to admins.

        """
        # TODO: Move constants to external preferences
        # Send Email on error
        host = config.SMTP_HOST
        from_addr = config.EMAIL_FROM
        to_addrs = config.EMAIL_TO

        text = "Query: '%s'." % query
        msg = MIMEText(text.encode('utf-8'), 'plain', 'utf-8')
        msg['Subject'] = "[Molnetbot] An error occured while sending a " \
                         "search query to Molnet."
        msg['From'] = from_addr
        msg['To'] = ', '.join(to_addrs)
        deferred = sendmail(host, from_addr, to_addrs, msg.as_string())

        # Send error reply back to query sender
        reply = domish.Element((None, 'message'))
        reply['to'] = sender
        reply['from'] = recipient
        reply['type'] = 'chat'
        reply.addElement('body', content="An error occurred while "
                                         "sending your search query to "
                                         "Molnet. Please try again later.")
        self.send(reply)
