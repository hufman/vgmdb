#!/usr/bin/env python

import sys
import urllib
import vgmdb.album
import json

def parse_album(album):
	url = 'http://vgmdb.net/album/%s'%album
	data = vgmdb.album.fetch_album_page(url)
	album_info = vgmdb.album.parse_album_page(data)
	return json.dumps(album_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_album(sys.argv[1]).encode('utf-8')
