#!/usr/bin/env python

import sys
import vgmdb.artistlist
import json

def parse_artistlist(artist):
	data = vgmdb.artistlist.fetch_artistlist_page(artist)
	artist_info = vgmdb.artistlist.parse_artistlist_page(data)
	return json.dumps(artist_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_artistlist(sys.argv[1]).encode('utf-8')
