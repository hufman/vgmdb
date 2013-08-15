#!/usr/bin/env python

import sys
import vgmdb.product
import json

def parse_product(product):
	data = vgmdb.product.fetch_product_page(product)
	product_info = vgmdb.product.parse_product_page(data)
	return json.dumps(product_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_product(sys.argv[1]).encode('utf-8')
