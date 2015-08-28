""" Frontend to fetching vgmdb data
    Will load from cache, or from synchronous request module, or async celery
"""
import urllib as _urllib
import base64 as _base64
import datetime as _datetime
import logging as _logging

import vgmdb.data
import vgmdb._tasks

import vgmdb.cache
import vgmdb.config

_vgmdb = vgmdb
del vgmdb

_logger = _logging.getLogger(__name__)

def _fetch_page(cache_key, page_type, id, link=None, use_cache=True):
	""" Generic function to handle general vgmdb requests

	@param cache_key is where the data should be stored in the cache
	@param page_type is used to locate the vgmdb module
	@param id is which specific page to fetch
	@param link is where the page comes from, to be added to the data
	@param use_cache can be set to False to ignore any cached data
	"""
	info = None
	prevdata = None
	if use_cache:
		prevdata = _vgmdb.cache.get(cache_key)
	if prevdata:
		info = prevdata
		if not _is_info_current(info):
			task = _vgmdb._tasks.request_page
			running = task.apply_async(args=[cache_key, page_type, id, link], queue='background')
	else:
		# if we should try to load over Celery
		if getattr(_vgmdb.config, 'DATA_BACKGROUND', False):
			alive = True	# assume it's accessible
			if getattr(_vgmdb.config, 'CELERY_PING', False):
				# check if it's accessible
				alive = _vgmdb._tasks.celery.control.inspect(timeout=0.1).stats()
			if not alive:
				# load synchronously
				_logger.warning('Celery is unavailable but DATA_BACKGROUND requested!')
				info = _vgmdb.data.request_page(cache_key, page_type, id, link)
			else:
				task = _vgmdb._tasks.request_page
				running = task.delay(cache_key, page_type, id, link)
				info = running.wait()
		else:
			info = _vgmdb.data.request_page(cache_key, page_type, id, link)
	return info

def _is_info_current(info):
	info_current = True
	fetched_date = info.get('meta', {}).get('fetched_date', None)
	ttl = info.get('meta', {}).get('ttl', 86400)
	if fetched_date:
		try:
			fetched_date = _datetime.datetime.strptime(fetched_date, '%Y-%m-%dT%H:%M')
		except ValueError as e:
			_logger.warning('Could not parse fetched_date from %s (%s): %s' % (info.get('link', None), fetched_date, e))
			fetched_date = None
	else:
		_logger.warning('Missing fetched_date on %s' % (info.get('link', None),))
	if fetched_date:
		age = _datetime.datetime.now() - fetched_date
		if age > _datetime.timedelta(seconds=ttl):
			info_current = False
	return info_current

def info(page_type, id, use_cache=True):
	""" Loads an information page

	@param page_type says which specific type of page
		artist album product event org
	@param id is which specific item to load
	@param use_cache can be set to False to ignore any cached data
	"""
	cache_key = 'vgmdb/%s/%s'%(page_type,_urllib.quote(str(id)))
	link = '%s/%s'%(page_type,id)
	return _fetch_page(cache_key, page_type, id, link, use_cache)
_info_aliaser = lambda page_type: lambda id,use_cache=True: info(page_type, id, use_cache)
for name in ['artist','album','product','release','event','org']:
	func = _info_aliaser(name)
	func.__name__ = name
	locals()[name] = func

def list(page_type, id='A', use_cache=True):
	""" Loads an information list page

	@param page_type says which specific type of page
		albumlist artistlist productlist
		orglist eventlist
	@param id is which specific item to load
		orglist and eventlist ignore the id
		id will default to 'A' if not passed
	@param use_cache can be set to False to ignore any cached data
	"""
	cache_key = 'vgmdb/%s/%s'%(page_type,id)
	if page_type in ['orglist', 'eventlist']:	# complete pages
		cache_key = 'vgmdb/%s'%(page_type,)
	if id:
		link = '%s/%s'%(page_type, _urllib.quote(str(id)))
	else:
		link = '%s'%(page_type,)
	return _fetch_page(cache_key, page_type, id, link, use_cache)
_list_aliaser = lambda page_type: lambda id='A',use_cache=True: list(page_type, id, use_cache)
for name in ['albumlist','artistlist','productlist','orglist','eventlist']:
	func = _list_aliaser(name)
	func.__name__ = name
	locals()[name] = func

def search(page_type, query, use_cache=True):
	""" Loads an search page

	@param page_type says which specific type of page
		This information is only used to change the data['link'] key
		The results for all sections are always returned
		This item can be None
		albums artists orgs products
	@param query is what to search for
	@param use_cache can be set to False to ignore any cached data
	"""
	cache_key = 'vgmdb/search/%s'%(_base64.b64encode(query),)
	link = 'search/%s'%(_urllib.quote(query),)
	data = _fetch_page(cache_key, 'search', query, link, use_cache)
	if page_type:
		data['link'] = 'search/%s/%s'%(page_type,_urllib.quote(query))
	return data
_search_aliaser = lambda page_type: lambda query,use_cache=True: search(page_type, query, use_cache)
for name in ['albums','artists','orgs','products']:
	func_name = 'search_%s'%(name,)
	func = _search_aliaser(name)
	func.__name__ = func_name
	locals()[func_name] = func

def recent(page_type, use_cache=True):
	""" Loads a list of recent edits

	@param page_type says which specific type of page
	"""
	cache_key = 'vgmdb/recent/%s'%(page_type,)
	link = 'recent/%s'%(_urllib.quote(page_type),)
	info = _fetch_page(cache_key, 'recent', page_type, link, use_cache)
	_clear_recent_cache(info)
	return info
_recent_aliaser = lambda page_type: lambda use_cache=True: recent(page_type, use_cache)
for name in ['albums', 'media', 'tracklists', 'scans', 'artists', \
             'products', 'labels', 'links', 'ratings']:
	func_name = 'recent_%s'%(name,)
	func = _recent_aliaser(name)
	func.__name__ = name
	locals()[func_name] = func

def _clear_recent_cache(recent_info):
	edited_date = None
	for update in recent_info['updates']:
		if 'date' in update:
			edited_date = update['date']
		else:
			continue

		if 'link' in update:
			cache_key = "vgmdb/%s"%(update['link'],)
			prevdata = _vgmdb.cache.get(cache_key)
			if prevdata and \
			   'meta' in prevdata and \
			   'edited_date' in prevdata['meta'] and \
			   prevdata['meta']['edited_date'] < edited_date:
				_vgmdb.cache.delete(cache_key)

# Cleaup temporary variables
del _info_aliaser
del _list_aliaser
del _search_aliaser
del _recent_aliaser
del name
del func_name
del func
