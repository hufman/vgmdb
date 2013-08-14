#!/usr/bin/env python

import sys
import urllib
import vgmdb.eventlist
import json

def parse_eventlist():
	url = 'http://vgmdb.net/db/events.php'
	data = vgmdb.eventlist.fetch_eventlist_page(url)
	event_info = vgmdb.eventlist.parse_eventlist_page(data)
	return json.dumps(event_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__':
	print parse_eventlist().encode('utf-8')
