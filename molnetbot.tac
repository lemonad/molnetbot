#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Lets users query an intranet application named Molnet for people and
phone numbers.

The actual backend is not defined yet except that queries will be
submitted to a restful API. What kind of resources that will be returned
is TBD.

Install and run:
$ virtualenv --no-site-packages .
$ source bin/activate
$ python bootstrap.py
$ bin/buildout
$ twistd -ny molnetbot.tac

"""
from twisted.application import service
from twisted.internet import reactor
from twisted.words.protocols.jabber import jid
from wokkel.xmppim import PresenceClientProtocol
from wokkel.client import XMPPClient
from wokkel.generic import VersionHandler, FallbackHandler

from molnetbot import config
from molnetbot.molnetbot import QueryHandler, PresenceAcceptingHandler
from molnetbot.vcard_temp import VCardTemp
from molnetbot.xep0012 import LastActivityHandler
from molnetbot.xep0202 import EntityTimeHandler

application = service.Application("molnetbot")

xmppclient = XMPPClient(jid.internJID(config.JID), config.PASSWORD)
if config.LOG_TRAFFIC:
    xmppclient.logTraffic = True
xmppclient.setServiceParent(application)

# Install handler for XEP-0092 Software version
version_handler = VersionHandler('MolnetBot', config.version())
version_handler.setHandlerParent(xmppclient)
# Install handler for XEP-0012: Last activity
last_activity_handler = LastActivityHandler()
last_activity_handler.setHandlerParent(xmppclient)
# Install handler for XEP-0202: Entity time
entity_time_handler = EntityTimeHandler()
entity_time_handler.setHandlerParent(xmppclient)

# Install handler for receiving and replying to search queries
query_handler = QueryHandler()
query_handler.setHandlerParent(xmppclient)
# Install handler for handling subscribtions, etc.
presence_handler = PresenceAcceptingHandler()
presence_handler.setHandlerParent(xmppclient)

# If nothing else... install a fallback handler
fallback_handler = FallbackHandler()
fallback_handler.setHandlerParent(xmppclient)

# Initialize and send vCard, including avatar... but let everything
# settle first
vcard_temp = VCardTemp(xmppclient)
vcard_temp.set_image(config.AVATAR_IMAGE_PATH)
reactor.callLater(5, vcard_temp.send)
