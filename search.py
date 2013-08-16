#!/usr/bin/env python

import sys
import vgmdb.search
import json

def parse_search(query):
	data = vgmdb.search.fetch_page(query)
	event_info = vgmdb.search.parse_page(data)
	return json.dumps(event_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_search(sys.argv[1]).encode('utf-8')
