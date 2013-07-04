import json
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
	import pylibmc as memcache
except:
	pass

gaecache = None
try:
	from google.appengine.api import memcache as gaecache
except:
	pass

class NullCache(object):
	def __getitem__(self, key):
		return None
	def __setitem__(self, key, value):
		pass

class MemcacheCache(object):
	def __init__(self, addresses):
		self._memcache = memcache.Client(addresses)
	def __getitem__(self, key):
		# returns the value or None
		try:
			value = self._memcache.get(key)
			if value:
				value = json.loads(value)
		except:
			return None
		return value
	def __setitem__(self, key, value):
		try:
			self._memcache.set(key, json.dumps(value), time=86400)
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
				value = json.loads(value)
		except:
			return None
		return value
	def __setitem__(self, key, value):
		try:
			self._gaecache.set(key, json.dumps(value), time=86400)
		except:
			pass

cache = NullCache()
if memcache:
	try:
		cache = MemcacheCache(['127.0.0.1:11211'])
	except:
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
