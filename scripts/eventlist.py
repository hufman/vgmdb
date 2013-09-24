#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.parsers.eventlist
import json

def parse_eventlist():
	data = vgmdb.parsers.eventlist.fetch_page(None)
	event_info = vgmdb.parsers.eventlist.parse_page(data)
	return json.dumps(event_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__':
	print parse_eventlist().encode('utf-8')
