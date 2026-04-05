from .. import cache
from .. import config
from .. import fetch

from . import discogs
from . import amazon
from . import cdjapan
from . import itunes
from . import spotify

try:
	from concurrent.futures import ThreadPoolExecutor
except:
	pass

search_modules = [discogs, amazon, cdjapan, itunes, spotify]
search_types = ['album', 'artist']

import time
import logging

class NullHandler(logging.Handler):
	def emit(self, record):
		pass
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

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
				print('%s - elapsed time: %f ms' % (self.tag, self.msecs))
			else:
				print('elapsed time: %f ms' % self.msecs)

def search(type, id, start_search=True, wait=True, allow_partial=False):
	"""
	type should be either album or artist
	"""
	if type in search_types:
		info = fetch.info(type, id)
		return search_info(type, id, info, start_search, wait, allow_partial)
	else:
		return []

def search_info(type, id, info, start_search=True, wait=True, allow_partial=False):
	"""
	Search for sellers for this info item
	If start_search is True, attempt to start a search
		If the worker method is available, it will start a search
		Otherwise it will only search if wait is True
		With the worker method, allow_partial will let it return after submitting the tasks
	If start_search is True but wait is False, it will return the current search results
		Any unfinished search results will say they are searching
	"""
	if type not in search_types:
		return []
	results = []
	if start_search:
		if hasattr(config, 'CELERY_BROKER'):
			try:
				return _search_all_workers(type,id,info,wait and not allow_partial)
			except Exception as e:
				logger.warning("Celery unreachable! (%s)" % (e,))
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
	logger.debug("Searching for sellers for %s/%s synchronously"%(type, id))
	results = []
	for module in search_modules:
		with Timer(tag=module.__name__, verbose=False):
			search = getattr(module, "search_%s"%(type,), None)
			empty = getattr(module, "empty_%s"%(type,), None)
			prev = cache.get("vgmdb/%s/%s/sellers/%s"%(type,id,module.__name__))
			ret = None
			if search and not prev:
				try:
					ret = search(info)
				except Exception as e:
					logger.error("Exception while searching %s for %s/%s: %s"%(module, type, id, e))
				if ret:
					cache.set("vgmdb/%s/%s/sellers/%s"%(type,id,module.__name__), ret)
					results.append(ret)
				else:
					results.append(empty(info))
			if search and prev:
				results.append(prev)
	return results

def _search_all_async(type, id, info):
	logger.debug("Searching for sellers for %s/%s asynchronously"%(type, id))
	def search_module(module):
		cache_key = "vgmdb/%s/%s/sellers/%s"%(type,id,module.__name__)
		with Timer(tag=module.__name__, verbose=False):
			search = getattr(module, "search_%s"%(type,), None)
			empty = getattr(module, "empty_%s"%(type,), None)
			prev = cache.get(cache_key)
			ret = None
			if search and not prev:
				try:
					ret = search(info)
				except Exception as e:
					logger.error("Exception while searching %s for %s/%s: %s"%(module, type, id, e))
				if ret:
					cache.set(cache_key, ret)
					return ret
				else:
					return empty(info)
			return prev
	executor = ThreadPoolExecutor(max_workers=5)
	results = executor.map(search_module, search_modules, timeout=60)
	results = [x for x in results if x]
	return results

def _search_all_workers(type, id, info, wait):
	from . import _tasks
	if getattr(config, 'CELERY_PING', False):
		alive = _tasks.celery.control.inspect(timeout=0.1).stats()
		if not alive:
			raise IOError("No Celery workers")
	logger.debug("Searching for sellers for %s/%s with Celery"%(type, id))
	active = []
	for module in search_modules:
		cache_key = "vgmdb/%s/%s/sellers/%s"%(type,id,module.__name__)
		prev = cache.get(cache_key)
		if not prev:
			name = module.__name__.split('.')[-1]
			task = getattr(_tasks, name)
			active.append(task.apply_async(args=[type, id], queue='sellers'))
	if wait:
		try:
			for task in active:
				task.wait()
		except:
			pass
	results = get_results(type, id, info)
	for result in results:
		if 'not_searched' in result:
			if not wait:
				result['searching'] = result['not_searched']
			del result['not_searched']
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
