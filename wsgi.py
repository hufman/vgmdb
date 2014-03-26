# Use this file, along with the snippet from apache.conf,
# to add this application to mod_wsgi

import sys, os, bottle

base = os.path.dirname(__file__)
sys.path = [base] + sys.path
if os.getcwd() != base:
	os.chdir(base)

import logging
logging.basicConfig(level=logging.ERROR)

import vgmdb.main
application = bottle.default_app()

