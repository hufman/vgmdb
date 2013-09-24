#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.parsers.orglist
import json

def parse_orglist():
	data = vgmdb.parsers.orglist.fetch_page(None)
	org_info = vgmdb.parsers.orglist.parse_page(data)
	return json.dumps(org_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__':
	print parse_orglist().encode('utf-8')
