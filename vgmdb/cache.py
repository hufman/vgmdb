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

if not cache:
	logger.info("Failing back to null cache")
	cache = NullCache()

def get(key):
	return cache[key]
def set(key, value):
	cache[key] = value
def delete(key):
	del cache[key]
