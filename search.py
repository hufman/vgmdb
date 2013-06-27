#!/usr/bin/env python

import sys
import urllib
import vgmdb.search
import json

def parse_search(query):
	data = urllib.urlopen('http://vgmdb.net/search?q=%s'%query).read()
	data = data.decode('utf-8', 'ignore')
	event_info = vgmdb.search.parse_search_page(data)
	return json.dumps(event_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_search(sys.argv[1]).encode('utf-8')
