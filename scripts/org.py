#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.org
import json

def parse_org(org):
	data = vgmdb.org.fetch_page(org)
	org_info = vgmdb.org.parse_page(data)
	return json.dumps(org_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_org(sys.argv[1]).encode('utf-8')
