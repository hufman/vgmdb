# Use this file, along with the snippet from apache.conf,
# to add this application to mod_wsgi

import sys, os, bottle

base = os.path.dirname(__file__)
sys.path = [base] + sys.path
os.chdir(base)

import vgmdb.main
application = bottle.default_app()

