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

def search(type, id, start_search=True, wait=True):
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
		return search_info(type, id, info, start_search, wait)
	else:
		return []

def search_info(type, id, info, start_search=True, wait=True):
	"""
	Search for sellers for this info item
	if start_search is True and wait is True, attempt to start a search
	If start_search is True but wait is False, it will return the current search results
		Any unfinished search results will say they are searching
	"""
	results = []
	if start_search:
		if wait and 'ThreadPoolExecutor' in globals():
			return _search_all_async(type,id,info)
		elif wait:
			return _search_all_sync(type,id,info)
		else:
			results = get_results(type,id,info)
	else:
		results = get_results(type,id,info)

	if start_search:
		for result in results:
			result['searching'] = 'not_searched' in result
	return results

def _search_all_sync(type, id, info):
	results = []
	for module in search_modules:
		with Timer(tag=module.__name__, verbose=False):
			search = getattr(module, "search_%s"%(type,), None)
			empty = getattr(module, "empty_%s"%(type,), None)
			prev = cache.get("vgmdb/%s/%s/sellers/%s"%(type,id,module.__name__))
			if search and not prev:
				ret = search(info)
				if ret:
					cache.set("vgmdb/%s/%s/sellers/%s"%(type,id,module.__name__), ret)
					results.append(ret)
				else:
					results.append(empty(info))
	return results

def _search_all_async(type, id, info):
	def search_module(module):
		with Timer(tag=module.__name__, verbose=False):
			search = getattr(module, "search_%s"%(type,), None)
			empty = getattr(module, "empty_%s"%(type,), None)
			prev = cache.get("vgmdb/%s/%s/sellers/%s"%(type,id,module.__name__))
			if search and not prev:
				ret = search(info)
				if ret:
					cache.set("vgmdb/%s/%s/sellers/%s"%(type,id,module.__name__), ret)
					return ret
				else:
					return empty(info)
			return prev
	executor = ThreadPoolExecutor(max_workers=5)
	results = executor.map(search_module, search_modules, timeout=60)
	results = filter(lambda x:x, results)
	return results

def get_results(type, id, info):
	results = []
	for module in search_modules:
		module_results = cache.get("vgmdb/%s/%s/sellers/%s"%(type,id,module.__name__))
		empty_results = getattr(module, "empty_%s"%(type,))
		if not module_results:
			module_results = empty_results(info)
			module_results['not_searched'] = True
		results.append(module_results)
	return results
