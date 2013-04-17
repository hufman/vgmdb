#!/usr/bin/env python

import sys
import urllib
import vgmdb.artist
import json

def parse_artist(artist):
	data = urllib.urlopen('http://vgmdb.net/artist/%s'%artist).read()
	data = data.decode('utf-8', 'ignore')
	artist_info = vgmdb.artist.parse_artist_page(data)
	return json.dumps(artist_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
print parse_artist(sys.argv[1]).encode('utf-8')
