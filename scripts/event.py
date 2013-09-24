#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.parsers.event
import json

def parse_event(event):
	data = vgmdb.parsers.event.fetch_page(event)
	event_info = vgmdb.parsers.event.parse_page(data)
	return json.dumps(event_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_event(sys.argv[1]).encode('utf-8')
