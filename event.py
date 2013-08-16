#!/usr/bin/env python

import sys
import vgmdb.event
import json

def parse_event(event):
	data = vgmdb.event.fetch_page(event)
	event_info = vgmdb.event.parse_page(data)
	return json.dumps(event_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_event(sys.argv[1]).encode('utf-8')
