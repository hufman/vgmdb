import urllib as _urllib
import base64 as _base64

import vgmdb.parsers.artist
import vgmdb.parsers.album
import vgmdb.parsers.product
import vgmdb.parsers.event
import vgmdb.parsers.org

import vgmdb.parsers.albumlist
import vgmdb.parsers.artistlist
import vgmdb.parsers.productlist
import vgmdb.parsers.orglist
import vgmdb.parsers.eventlist
import vgmdb.parsers.search

import vgmdb.cache
import vgmdb.config

_vgmdb = vgmdb
del vgmdb

def _request_page(cache_key, page_type, id, link=None, use_cache=True):
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
	if not prevdata:
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
			_vgmdb.cache.set(cache_key, info)
	else:
		info = prevdata
	return info

def info(page_type, id, use_cache=True):
	""" Loads an information page

	@param page_type says which specific type of page
		artist album product event org
	@param id is which specific item to load
	@param use_cache can be set to False to ignore any cached data
	"""
	cache_key = 'vgmdb/%s/%s'%(page_type,_urllib.quote(str(id)))
	link = '%s/%s'%(page_type,id)
	return _request_page(cache_key, page_type, id, link, use_cache)
_info_aliaser = lambda name: lambda id,use_cache=True: info(name, id, use_cache)
for name in ['artist','album','product','event','org']:
	func = _info_aliaser(name)
	func.__name__ = name
	locals()[name] = func

def list(page_type, id, use_cache=True):
	""" Loads an information list page

	@param page_type says which specific type of page
		albumlist artistlist
		productlist orglist eventlist
	@param id is which specific item to load
	@param use_cache can be set to False to ignore any cached data
	"""
	cache_key = 'vgmdb/%s/%s'%(page_type,id)
	if page_type in ['orglist', 'eventlist']:	# complete pages
		cache_key = 'vgmdb/%s'%(page_type,)
	if id:
		link = '%s/%s'%(page_type, _urllib.quote(str(id)))
	else:
		link = '%s'%(page_type,)
	return _request_page(cache_key, page_type, id, link, use_cache)
_list_aliaser = lambda name: lambda id,use_cache=True: list(name, id, use_cache)
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
	data = _request_page(cache_key, 'search', query, link, use_cache)
	if page_type:
		data['link'] = 'search/%s/%s'%(page_type,_urllib.quote(query))
	return data
_search_aliaser = lambda name: lambda query,use_cache=True: search(name, query, use_cache)
for name in ['albums','artists','orgs','products']:
	func_name = 'search_%s'%(name,)
	func = _search_aliaser(name)
	func.__name__ = func_name
	locals()[func_name] = func

del _info_aliaser
del _list_aliaser
del _search_aliaser
del name
del func_name
del func
