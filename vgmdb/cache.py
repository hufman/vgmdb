import os
import json
import logging
try:
	import simplejson as json
except:
	pass

memcache = None
try:
	import memcache
except:
	pass
try:
	import bmemcached as memcache
except:
	pass
try:
	import pylibmc as memcache
except:
	pass

import pickle
try:
	import cPickle as pickle
except:
	pass

gaecache = None
try:
	from google.appengine.api import memcache as gaecache
except:
	pass

logger = logging.getLogger(__name__)

from . import config

class NullCache(object):
	def __getitem__(self, key):
		return None
	def __setitem__(self, key, value):
		pass
	def __delitem__(self, key):
		pass

class MemcacheCache(object):
	def __init__(self, addresses, **kwargs):
		self._memcache = memcache.Client(addresses, **kwargs)
	def __getitem__(self, key):
		# returns the value or None
		try:
			value = self._memcache.get(key)
			if value:
				value = pickle.loads(value)
		except Exception as e:
			logger.warning("Failed to load %s from cache: %s"% (key, e))
			return None
		return value
	def __setitem__(self, key, value):
		ttl = 86400 * 29  # 29 days
		try:
			self._memcache.set(key, pickle.dumps(value,-1), time=ttl)
		except Exception as e:
			logger.warning("Failed to set %s in cache: %s"% (key, e))
	def __delitem__(self, key):
		try:
			self._memcache.delete(key)
		except:
			pass

class GaeCache(object):
	def __init__(self):
		self._gaecache = gaecache
	def __getitem__(self, key):
		# returns the value or None
		try:
			value = self._gaecache.get(key)
			if value:
				value = pickle.loads(value)
		except:
			return None
		return value
	def __setitem__(self, key, value):
		ttl = 86400 * 29  # 29 days
		try:
			self._gaecache.set(key, pickle.dumps(value,-1), time=ttl)
		except:
			pass
	def __delitem__(self, key):
		try:
			self._gaecache.delete(key)
		except:
			pass

cache = None

if not cache and gaecache:
	try:
		cache = GaeCache()
	except:
		pass

if not cache and memcache:
	try:
		cache = MemcacheCache(config.MEMCACHE_SERVERS, **config.MEMCACHE_ARGS)
	except:
		pass

if not cache:
	cache = NullCache()

def get(key):
	return cache[key]
def set(key, value):
	cache[key] = value
def delete(key):
	del cache[key]
