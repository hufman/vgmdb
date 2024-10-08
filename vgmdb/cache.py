import os
import json
import logging
logger = logging.getLogger(__name__)

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
	logger.info("Loaded binary memcache support, SASL authentication available")
except:
	pass
try:
	import socket
	if socket.socket.__module__ != "gevent.socket":
		import pylibmc as memcache
	else:
		logger.info("Skipping pylibmc detection because gevent is active")
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
	logger.info("Google App Engine detected")
except:
	pass

try:
	import redis
except:
	pass

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
		stats = None
		if hasattr(self._memcache, 'get_stats'):
			stats = self._memcache.get_stats()
		elif hasattr(self._memcache, 'stats'):
			stats = self._memcache.stats()
		if stats is not None and all((len(s)==0 for s in stats.values())):
			raise IOError("Could not connect to memcache")
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

class RedisCache(object):
	def __init__(self, host, port=6379):
		self._cache = redis.Redis(host=host, port=6379)
	def __getitem__(self, key):
		try:
			value = self._cache.get(key)
			if value:
				return pickle.loads(value)
		except:
			return None
	def __setitem__(self, key, value):
		try:
			if key.startswith('albumlist') or key.startswith('artistlist') or key.startswith('orglist') or key.startwith('eventlist'):
				self._cache.set(key, pickle.dumps(value,-1))
			else:
				ttl = 86400 * 29  # 29 days
				self._cache.set(key, pickle.dumps(value,-1), ex=ttl)
		except:
			pass
	def __delitem__(self, key):
		try:
			self._cache.delete(key)
		except:
			pass

class FileCache(object):
	def __init__(self, path):
		self._path = path
	def _filepath(self, key):
		return os.path.join(self._path, key.replace('/', '_'))
	def __getitem__(self, key):
		try:
			with open(self._filepath(key)) as handle:
				return json.load(handle)
		except:
			pass
	def __setitem__(self, key, value):
		try:
			with open(self._filepath(key), 'w') as handle:
				json.dump(value, handle)
		except:
			raise
			pass
	def __delitem__(self, key):
		try:
			os.remove(self._filepath(key))
		except:
			pass

class MultiCache(object):
	def __init__(self, backing):
		self._backing = backing
	def __getitem__(self, key):
		for backing in self._backing:
			value = backing[key]
			if value:
				return value
	def __setitem__(self, key, value):
		for backing in self._backing:
			backing[key] = value
	def __delitem__(self, key):
		for backing in self._backing:
			del backing[key]

cache = None

if not cache and gaecache:
	try:
		logger.info("Connecting GAE Cache")
		cache = GaeCache()
	except Exception as e:
		logger.warning("Failed to create GAEcache client: %s" % (e, ))

if not cache and memcache:
	try:
		logger.info("Connecting Memcache client to %s with args %s" % (config.MEMCACHE_SERVERS, config.MEMCACHE_ARGS))
		cache = MemcacheCache(config.MEMCACHE_SERVERS, **config.MEMCACHE_ARGS)
	except Exception as e:
		logger.warning("Failed to create Memcache client: %s" % (e, ))

if not cache and 'redis' in globals() and hasattr(config, 'REDIS_HOST'):
	try:
		logger.info("Connecting Redis client to %s" % (config.REDIS_HOST,))
		cache = RedisCache(config.REDIS_HOST)
	except Exception as e:
		logger.warning("Failed to create Redis client: %s" % (e, ))

if not cache:
	logger.info("Failing back to null cache")
	cache = NullCache()

def get(key):
	return cache[key]
def set(key, value):
	cache[key] = value
def delete(key):
	del cache[key]
