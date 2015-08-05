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
		ttl = 86400 * 300  # 300 days
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
		ttl = 86400 * 300  # 300 days
		try:
			self._gaecache.set(key, pickle.dumps(value,-1), time=ttl)
		except:
			pass
	def __delitem__(self, key):
		try:
			self._gaecache.delete(key)
		except:
			pass

cache = NullCache()
if memcache:
	try:
		cache = MemcacheCache(['127.0.0.1:11211'])
	except:
		pass

	# detect openshift
	if 'OPENSHIFT_MEMCACHED_HOST' in os.environ and \
	   'OPENSHIFT_MEMCACHED_PORT' in os.environ:
		try:
			cache = MemcacheCache(['%s:%s'%(
			    os.environ['OPENSHIFT_MEMCACHED_HOST'],
			    os.environ['OPENSHIFT_MEMCACHED_PORT'])],
			    username =os.environ['OPENSHIFT_MEMCACHED_USERNAME'],
			    password = os.environ['OPENSHIFT_MEMCACHED_PASSWORD'])
		except Exception as e:
			pass

	# detect docker cache
	if 'MEMCACHED_PORT_11211_TCP' in os.environ:
		try:
			cache = MemcacheCache(['%s:%s'%(
			    os.environ['MEMCACHED_PORT_11211_TCP_ADDR'],
			    os.environ['MEMCACHED_PORT_11211_TCP_PORT'])])
		except Exception as e:
			pass

if gaecache:
	try:
		cache = GaeCache()
	except:
		pass

def get(key):
	return cache[key]
def set(key, value):
	cache[key] = value
def delete(key):
	del cache[key]
