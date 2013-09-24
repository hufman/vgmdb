#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.parsers.album
import json

def parse_album(album):
	data = vgmdb.parsers.album.fetch_page(album)
	album_info = vgmdb.parsers.album.parse_page(data)
	return json.dumps(album_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_album(sys.argv[1]).encode('utf-8')
