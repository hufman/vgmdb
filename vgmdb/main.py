from bottle import route, response, request, static_file, abort
import urllib
import json
import base64

import vgmdb.artist
import vgmdb.album
import vgmdb.product
import vgmdb.event
import vgmdb.org

import vgmdb.albumlist
import vgmdb.artistlist
import vgmdb.productlist
import vgmdb.orglist
import vgmdb.eventlist
import vgmdb.search

import vgmdb.sellers

import vgmdb.cache
import vgmdb.config
import vgmdb.output

try:
	import simplejson as json
except:
	pass

@route('/hello')
def hello():
	return "Hello!"

def do_page(cache_key, page_type, id, link=None, filterkey=None):
	"""
	@param cache_key where to save the parsed data
	@param page_type what parser and output to use
	@param id which particular data to request from the backend
	@param link what short url to set as the data['link']
	@param filterkey some pages have data that can be filtered in the output
	"""
	prevdata = vgmdb.cache.get(cache_key)
	if not prevdata:
		module = getattr(vgmdb, page_type)
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
			vgmdb.cache.set(cache_key, info)
	else:
		info = prevdata
	if info == None:
		abort(404, "Item not found")

	# add in any seller information
	sellers = vgmdb.sellers.search_info(page_type, id, info, start_search=True, wait=False)
	info['sellers'] = sellers
	not_searched = any(['not_searched' in item for item in sellers])
	searching = any(['searching' in item for item in sellers])
	if not_searched or searching:
		response.set_header('Cache-Control', 'max-age:60,public')
	else:
		response.set_header('Cache-Control', 'max-age:3600,public')

	requested_format = request.query.format or ''
	outputter = vgmdb.output.get_outputter(vgmdb.config.for_request(request), requested_format, request.headers.get('Accept'))
	response.content_type = outputter.content_type
	return outputter(page_type, info, filterkey)

@route('/<type:re:(artist|album|product|event|org)>/<id:int>')
def info(type,id):
	cache_key = 'vgmdb/%s/%s'%(type,id)
	page_type = type
	link = "%s/%s"%(type,id)
	return do_page(cache_key, page_type, id, link)

@route('/<type:re:(albumlist|artistlist|productlist)>/<id:re:[#A-Z]>')
@route('/<type:re:(albumlist|artistlist|productlist)>/')
@route('/<type:re:(albumlist|artistlist|productlist)>')
def list(type,id='A'):
	cache_key = 'vgmdb/%s/%s'%(type,id)
	page_type = type
	if id:
		link = '%s/%s'%(type, id)
	else:
		link = '%s'%(type,)
	return do_page(cache_key, page_type, id, link=link)

@route('/<type:re:(orglist)>/<filterkey:re:[#A-Z]>')
@route('/<type:re:(orglist)>/')
@route('/<type:re:(orglist)>')
def orglist(type,filterkey=None):
	cache_key = 'vgmdb/%s'%(type,)
	page_type = type
	if filterkey:
		link = '%s/%s'%(type, urllib.quote(filterkey))
	else:
		link = '%s'%(type,)
	return do_page(cache_key, page_type, filterkey, link=link, filterkey=filterkey)

@route('/<type:re:(eventlist)>/<filterkey:int>')
@route('/<type:re:(eventlist)>/')
@route('/<type:re:(eventlist)>')
def eventlist(type,filterkey=None):
	cache_key = 'vgmdb/%s'%(type,)
	page_type = type
	if filterkey:
		link = '%s/%s'%(type, filterkey)
		filterkey = str(filterkey)
	else:
		link = '%s'%(type,)
	return do_page(cache_key, page_type, filterkey, link=link, filterkey=filterkey)

@route('/search/<type:re:(albums|artists|orgs|products)>/<query>')
@route('/search/<query>')
@route('/search')
def search(type=None, query=None):
	query = query or request.query['q']
	cache_key = 'vgmdb/search/%s'%(base64.b64encode(query),)
	page_type = 'search'
	if type:
		link = 'search/%s/%s'%(type,urllib.quote(query))
	else:
		link = 'search/%s'%(urllib.quote(query),)
	filterkey = type
	return do_page(cache_key, page_type, query, link=link, filterkey=filterkey)

@route('/')
@route('/about')
def about():
	outputter = vgmdb.output.get_outputter(vgmdb.config.for_request(request), 'html', None)
	response.content_type = outputter.content_type
	return outputter('about', {}, None)

@route('/<type:re:(album|artist)>/<id:int>/sellers')
def sellers(type,id):
	allow_partial = False or request.query.get('allow_partial')
	sellers = vgmdb.sellers.search(type,id, start_search=True, wait=True, allow_partial=allow_partial)
	searching = any(['searching' in item for item in sellers])
	requested_format = request.query.format or ''
	outputter = vgmdb.output.get_outputter(vgmdb.config.for_request(request), requested_format, request.headers.get('Accept'))
	response.content_type = outputter.content_type
	if searching:
		response.set_header('Cache-Control', 'max-age:1,public')
		response.set_header('Refresh', '1')
	else:
		response.set_header('Cache-Control', 'max-age:3600,public')
	return outputter('sellers', {'sellers':sellers})

@route('/static/<name:path>')
def static(name):
	response.set_header('Cache-Control', 'max-age:3600,public')
	return static_file(name, root='./static')
