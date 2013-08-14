#!/usr/bin/env python

import sys
import urllib
import vgmdb.artist
import json

def parse_artist(artist):
	url = 'http://vgmdb.net/artist/%s'%artist
	data = vgmdb.artist.fetch_artist_page(url)
	artist_info = vgmdb.artist.parse_artist_page(data)
	return json.dumps(artist_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_artist(sys.argv[1]).encode('utf-8')
