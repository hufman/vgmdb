#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.parsers.search
import json

def parse_search(query):
	data = vgmdb.parsers.search.fetch_page(query)
	event_info = vgmdb.parsers.search.parse_page(data)
	return json.dumps(event_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_search(sys.argv[1]).encode('utf-8')
