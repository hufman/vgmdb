#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.DEBUG)

from vgmdb import config

if config.USE_GEVENT:
	from gevent import monkey; monkey.patch_all()

from vgmdb import main
from bottle import run

if config.USE_GEVENT:
	run(host='0.0.0.0', port=9990, server='gevent')
else:
	run(host='0.0.0.0', port=9990)

