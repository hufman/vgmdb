#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.fetch
import json

def parse_release(release):
	release_info = vgmdb.fetch.release(release, use_cache=False)
	return json.dumps(release_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_release(sys.argv[1]).encode('utf-8')
