#!/usr/bin/env python

import sys
import urllib
import vgmdb.productlist
import json

def parse_productlist(product):
	data = urllib.urlopen('http://vgmdb.net/db/product.php?ltr=%s&field=title&perpage=999999'%urllib.quote(product)).read()
	data = data.decode('utf-8', 'ignore')
	product_info = vgmdb.productlist.parse_productlist_page(data)
	return json.dumps(product_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_productlist(sys.argv[1]).encode('utf-8')
