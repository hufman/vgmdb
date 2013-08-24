#!/usr/bin/python

import logging
logging.basicConfig(level=logging.DEBUG)

from bottle import run

from vgmdb import main

run(host='0.0.0.0', port=9990)

