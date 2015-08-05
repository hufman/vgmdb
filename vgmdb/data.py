""" Loads vgmdb data and saves it to cache """
import urllib as _urllib
import base64 as _base64

from datetime import datetime as _datetime

import vgmdb.parsers.artist
import vgmdb.parsers.album
import vgmdb.parsers.product
import vgmdb.parsers.release
import vgmdb.parsers.event
import vgmdb.parsers.org

import vgmdb.parsers.albumlist
import vgmdb.parsers.artistlist
import vgmdb.parsers.productlist
import vgmdb.parsers.orglist
import vgmdb.parsers.eventlist
import vgmdb.parsers.search

import vgmdb.parsers.recent

import vgmdb.cache
import vgmdb.config

import logging
logger = logging.getLogger(__name__)

_vgmdb = vgmdb
del vgmdb

def request_page(cache_key, page_type, id, link=None):
	""" Generic function to handle general vgmdb requests

	@param cache_key is where the data should be stored in the cache
	@param page_type is used to locate the vgmdb module
	@param id is which specific page to fetch
	@param link is where the page comes from, to be added to the data
	"""
	info = None
	module = getattr(_vgmdb.parsers, page_type)
	fetch_url = getattr(module, "fetch_url")
	fetch_page = getattr(module, "fetch_page")
	parse_page = getattr(module, "parse_page")
	data = fetch_page(id)
	info = parse_page(data)
	if info != None:
		if link:
			info['link'] = link
		if fetch_url:
			info['vgmdb_link'] = fetch_url(id)
		_calculate_ttl(info)
		_vgmdb.cache.set(cache_key, info)
	return info

def _calculate_ttl(info):
	ttl = 24 * 60 * 60	# 1 day default
	if 'meta' in info and 'edited_date' in info['meta']:
		try:
			fetched_date = _datetime.now()
			info['meta']['fetched_date'] = fetched_date.strftime('%Y-%m-%dT%H:%M')
			edited_date = _datetime.strptime(info['meta']['edited_date'], '%Y-%m-%dT%H:%M')
			date_diff = fetched_date - edited_date
			if date_diff.total_seconds() < 7 * 24 * 60 * 60:	# 1 week
				ttl = 60 * 60	# 1 hour
			if date_diff.total_seconds() < 24 * 60 * 60:	# 1 day
				ttl = 5 * 60	# 5 minutes
			if date_diff.total_seconds() < 1 * 60 * 60:	# 1 hour
				ttl = 60	# 1 minute
		except Exception as e:
			logger.warning("Failed to update data ttl for %s: %s" % (info.get('link'), e))
		info['meta']['ttl'] = ttl

def info(page_type, id):
	""" Loads an information page

	@param page_type says which specific type of page
		artist album product event org
	@param id is which specific item to load
	"""
	cache_key = 'vgmdb/%s/%s'%(page_type,_urllib.quote(str(id)))
	link = '%s/%s'%(page_type,id)
	return request_page(cache_key, page_type, id, link)
_info_aliaser = lambda page_type: lambda id: info(page_type, id)
for name in ['artist','album','product','release','event','org']:
	func = _info_aliaser(name)
	func.__name__ = name
	locals()[name] = func

def list(page_type, id='A'):
	""" Loads an information list page

	@param page_type says which specific type of page
		albumlist artistlist productlist
		orglist eventlist
	@param id is which specific item to load
		orglist and eventlist ignore the id
		id will default to 'A' if not passed
	"""
	cache_key = 'vgmdb/%s/%s'%(page_type,id)
	if page_type in ['orglist', 'eventlist']:	# complete pages
		cache_key = 'vgmdb/%s'%(page_type,)
	if id:
		link = '%s/%s'%(page_type, _urllib.quote(str(id)))
	else:
		link = '%s'%(page_type,)
	return request_page(cache_key, page_type, id, link)
_list_aliaser = lambda page_type: lambda id='A': list(page_type, id)
for name in ['albumlist','artistlist','productlist','orglist','eventlist']:
	func = _list_aliaser(name)
	func.__name__ = name
	locals()[name] = func

def search(page_type, query):
	""" Loads an search page

	@param page_type says which specific type of page
		This information is only used to change the data['link'] key
		The results for all sections are always returned
		This item can be None
		albums artists orgs products
	@param query is what to search for
	"""
	cache_key = 'vgmdb/search/%s'%(_base64.b64encode(query),)
	link = 'search/%s'%(_urllib.quote(query),)
	data = request_page(cache_key, 'search', query, link)
	if page_type:
		data['link'] = 'search/%s/%s'%(page_type,_urllib.quote(query))
	return data
_search_aliaser = lambda page_type: lambda query: search(page_type, query)
for name in ['albums','artists','orgs','products']:
	func_name = 'search_%s'%(name,)
	func = _search_aliaser(name)
	func.__name__ = func_name
	locals()[func_name] = func

def recent(page_type):
	""" Loads a list of recent edits

	@param page_type says which specific type of page
	"""
	cache_key = 'vgmdb/recent/%s'%(page_type,)
	link = 'recent/%s'%(_urllib.quote(page_type),)
	info = request_page(cache_key, 'recent', page_type, link)
	_clear_recent_cache(info)
	return info
_recent_aliaser = lambda page_type: lambda : recent(page_type)
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
