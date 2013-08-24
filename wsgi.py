# Use this file, along with the snippet from apache.conf,
# to add this application to mod_wsgi

import sys, os, bottle

import logging
logging.basicConfig(level=logging.ERROR)

import vgmdb.main
application = bottle.default_app()

