#!/usr/bin/env python

import sys
import urllib
import vgmdb.album
import json

def parse_album(album):
	data = urllib.urlopen('http://vgmdb.net/album/%s'%album).read()
	data = data.decode('utf-8', 'ignore')
	album_info = vgmdb.album.parse_album_page(data)
	return json.dumps(album_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
print parse_album(sys.argv[1])
