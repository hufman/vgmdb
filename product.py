#!/usr/bin/env python

import sys
import urllib
import vgmdb.product
import json

def parse_product(product):
	data = urllib.urlopen('http://vgmdb.net/product/%s'%product).read()
	data = data.decode('utf-8', 'ignore')
	product_info = vgmdb.product.parse_product_page(data)
	return json.dumps(product_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
print parse_product(sys.argv[1])
