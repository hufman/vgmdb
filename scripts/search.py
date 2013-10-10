#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.request
import json

def parse_search(query):
	event_info = vgmdb.request.search(None, query, use_cache=False)
	return json.dumps(event_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_search(sys.argv[1]).encode('utf-8')
