#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource


class BasicPage(Resource):
    isLeaf = True

    def render_GET(self, request):
        logger.info("<html><body><h1>Basic Test</h1><p>This is a basic test page.</p></body></html>")
        return "<html><body><h1>Basic Test</h1><p>This is a basic test page.</p></body></html>"

def hello():
    logger.info("Basic web server started.  Visit http://localhost:8000.")
    root = BasicPage()
    factory = Site(root)
    reactor.listenTCP(8000, factory)
    reactor.run()
