#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.parsers.product
import json

def parse_product(product):
	data = vgmdb.parsers.product.fetch_page(product)
	product_info = vgmdb.parsers.product.parse_page(data)
	return json.dumps(product_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_product(sys.argv[1]).encode('utf-8')
