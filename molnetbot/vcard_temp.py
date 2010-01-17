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


Send a vCard to servers handling xmpp extension XEP-0054: vCard-temp

"""
import sys

from twisted.words.xish import domish

import config


class VCardTemp(object):
    def __init__(self, xmppclient):
        # TODO: Initialize vCard properties from config
        self.xmppclient = xmppclient
        self.image = None
        self.mime_type = None
        self.full_name = "Molnet"
        self.nickname = "Molnet"
        self.url = "http://molnet/"
        self.description = "Who? Me?"

    def set_image(self, path):
        """Set avatar image given a path to an image."""

        try:
            image, mime_type = self.get_image_and_mime_type(path)
        except:
            raise

        self.image = image
        self.mime_type = mime_type

    def get_image_and_mime_type(self, path):
        """
        Given a path to an avatar image, figures out mime_type
        from file extension and reads image file into memory.
        
        Returns mime_type and image as a tuple.

        """
        # Get mime type from file extension
        extension = path[-4:]
        if extension == '.png':
            mime_type = 'image/png'
        elif extension == '.gif':
            mime_type = 'image/gif'
        elif extension == '.jpg' or extension == '.jpeg':
            mime_type = 'image/jpeg'
        else:
            raise ValueError, "Image extension '%s' not recognized." % (
                              extension)

        # Fetch and return image + mime_type
        try:
            f = open(path, 'rb')
        except IOError as (errno, errstr):
            print >> sys.stderr, "Error opening avatar file: '%s'" % errstr
            raise

        try:
            image = f.read()
        except IOError as (errno, errstr):
            print >> sys.stderr, "Error reading avatar file: '%s'" % errstr
            raise

        return (image, mime_type)

    def send(self):
        """Sends a vcard-temp set request to the xmpp server."""

        if not self.image or not self.mime_type:
            raise ValueError, "Image not initialized yet."

        xml = """\
<FN>%(full_name)s</FN>
<NICKNAME>%(nickname)s</NICKNAME>
<URL>%(url)s</URL>
<PHOTO>
    <TYPE>%(mime_type)s</TYPE>
    <BINVAL>%(b64image)s</BINVAL>
</PHOTO>
<DESC>%(description)s</DESC>""" % {'full_name': self.full_name,
                                   'nickname': self.nickname,
                                   'url': self.url,
                                   'b64image': self.image.encode('base64'),
                                   'mime_type': self.mime_type,
                                   'description': self.description}

        vcard_temp = domish.Element((None, 'iq'))
        vcard_temp['type'] = 'set'
        vcard_wrapper = vcard_temp.addElement('vCard', 'vcard-temp')
        vcard_wrapper.addRawXml(xml)
        self.xmppclient.send(vcard_temp)
