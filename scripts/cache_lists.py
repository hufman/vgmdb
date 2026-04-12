#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.fetch
import json
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('scripts/cache_lists')

def cache_all_list():
	for list in ('albumlist', 'artistlist', 'productlist'):
		cache_list(list)
	vgmdb.fetch.list('orglist', '', use_celery=False)

def cache_list(list):
	for letter in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
		id = letter + '1'
		while id:
			logger.info('... %s/%s' % (list, id))
			data = vgmdb.fetch.list(list, id, use_celery=False)
			id = data['pagination'].get('link_next', '/').split('/')[-1]  # next page

if __name__ == '__main__':
	cache_all_list()
