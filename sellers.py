#!/usr/bin/env python

import sys
import vgmdb.sellers
import json

def find_sellers(itemid):
	type,id = itemid.split('/')
	data = vgmdb.sellers.search(type,id)
	return json.dumps(data, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)

if __name__ == '__main__' and len(sys.argv) > 1:
	print find_sellers(sys.argv[1]).encode('utf-8')
