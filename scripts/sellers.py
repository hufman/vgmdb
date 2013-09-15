#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.sellers
import json
import logging
logging.basicConfig(level=logging.DEBUG)

def find_sellers(itemid):
	type,id = itemid.split('/')
	data = vgmdb.sellers.search(type,id)
	return json.dumps(data, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)

if __name__ == '__main__' and len(sys.argv) > 1:
	print find_sellers(sys.argv[1]).encode('utf-8')
