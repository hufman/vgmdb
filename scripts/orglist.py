#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.orglist
import json

def parse_orglist():
	data = vgmdb.orglist.fetch_page(None)
	org_info = vgmdb.orglist.parse_page(data)
	return json.dumps(org_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__':
	print parse_orglist().encode('utf-8')
