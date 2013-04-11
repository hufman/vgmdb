#!/usr/bin/python

from bottle import run

from vgmdb import main

run(host='0.0.0.0', port=9990)

