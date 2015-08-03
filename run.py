#!/usr/bin/env python

import os
import logging
logging.basicConfig(level=logging.DEBUG)

USE_GEVENT = os.environ.get('USE_GEVENT', False)

if USE_GEVENT:
	from gevent import monkey; monkey.patch_all()

from vgmdb import main
from bottle import run

if USE_GEVENT:
	run(host='0.0.0.0', port=9990, server='gevent')
else:
	run(host='0.0.0.0', port=9990)

