#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.parsers.productlist
import json

def parse_productlist(product):
	data = vgmdb.parsers.productlist.fetch_page(product)
	product_info = vgmdb.parsers.productlist.parse_page(data)
	return json.dumps(product_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_productlist(sys.argv[1]).encode('utf-8')
