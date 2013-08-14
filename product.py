#!/usr/bin/env python

import sys
import urllib
import vgmdb.product
import json

def parse_product(product):
	url = 'http://vgmdb.net/product/%s'%product
	data = vgmdb.product.fetch_product_page(url)
	product_info = vgmdb.product.parse_product_page(data)
	return json.dumps(product_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_product(sys.argv[1]).encode('utf-8')
