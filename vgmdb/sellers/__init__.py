from .. import album
from .. import artist
from .. import cache

from . import discogs
from . import amazon
from . import cdjapan
from . import itunes

try:
	from concurrent.futures import ThreadPoolExecutor
except:
	pass

search_modules = [discogs, amazon, cdjapan, itunes]

import time

class Timer(object):
	""" Absolutely brilliant idea from http://www.huyng.com/posts/python-performance-analysis/ """
	def __init__(self, tag=None, verbose=False):
		self.tag = tag
		self.verbose = verbose

	def __enter__(self):
		self.start = time.time()
		return self

	def __exit__(self, *args):
		self.end = time.time()
		self.secs = self.end - self.start
		self.msecs = self.secs * 1000  # millisecs
		if self.verbose:
			if self.tag:
				print '%s - elapsed time: %f ms' % (self.tag, self.msecs)
			else:
				print 'elapsed time: %f ms' % self.msecs

def search(type, id):
	"""
	itemid should be something like album/79 or artist/77
	"""
	if type in ['album','artist']:
		module = globals()[type]
		prevdata = cache.get("vgmdb/%s/%s"%(type,id))
		if not prevdata:
			fetch_page = getattr(module, "fetch_page")
			parse_page = getattr(module, "parse_page")
			page = fetch_page(id)
			info = parse_page(page)
			cache.set("vgmdb/%s/%s"%(type,id), info)
		else:
			info = prevdata
		return search_info(type, info)
	else:
		return []

def search_info(type, info):
	if 'ThreadPoolExecutor' in globals():
		return _search_all_async(type,info)
	else:
		return _search_all(type,info)

def _search_all_sync(type, info):
	results = []
	for module in search_modules:
		with Timer(tag=module.__name__, verbose=False):
			search = getattr(module, "search_%s"%(type,), None)
			if search:
				ret = search(info)
				if ret:
					results.append(ret)
	return results

def _search_all_async(type, info):
	def search_module(module):
		with Timer(tag=module.__name__, verbose=False):
			search = getattr(module, "search_%s"%(type,), None)
			if search:
				ret = search(info)
				if ret:
					return ret
	executor = ThreadPoolExecutor(max_workers=5)
	results = executor.map(search_module, search_modules, timeout=60)
	results = filter(lambda x:x, results)
	return results
