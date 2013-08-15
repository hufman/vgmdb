#!/usr/bin/env python

import sys
import vgmdb.albumlist
import json

def parse_albumlist(album):
	data = vgmdb.albumlist.fetch_albumlist_page(album)
	album_info = vgmdb.albumlist.parse_albumlist_page(data)
	return json.dumps(album_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_albumlist(sys.argv[1]).encode('utf-8')
