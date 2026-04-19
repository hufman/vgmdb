#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.parsers.search
import json
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('scripts/generate_search_index')

if __name__ == '__main__':
	vgmdb.parsers.search.generate_search_index()
