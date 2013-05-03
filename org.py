#!/usr/bin/env python

import sys
import urllib
import vgmdb.org
import json

def parse_org(org):
	data = urllib.urlopen('http://vgmdb.net/org/%s'%org).read()
	data = data.decode('utf-8', 'ignore')
	org_info = vgmdb.org.parse_org_page(data)
	return json.dumps(org_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print parse_org(sys.argv[1]).encode('utf-8')
