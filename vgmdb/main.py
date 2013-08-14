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

import vgmdb.cache
import vgmdb.output

try:
	import simplejson as json
except:
	pass

@route('/hello')
def hello():
	return "Hello!"

def do_page(cache_key, page_type, url, link=None, filterkey=None):
	"""
	@param cache_key where to save the parsed data
	@param page_type what parser and output to use
	@param url what url to download the data from
	@param link what short url to set as the data['link']
	"""
	prevdata = vgmdb.cache.get(cache_key)
	if not prevdata:
		data = urllib.urlopen(url).read()
		data = data.decode('utf-8', 'ignore')	# some pages have broken utf8
		module = getattr(vgmdb, page_type)
		parse_page = getattr(module, "parse_%s_page"%page_type)
		info = parse_page(data)
		if info != None:
			if link:
				info['link'] = link
			vgmdb.cache.set(cache_key, info)
	else:
		info = prevdata
	if info == None:
		abort(404, "Item not found")

	requested_format = request.query.format or ''
	outputter = vgmdb.output.get_outputter(requested_format, request.headers.get('Accept'))
	response.content_type = outputter.content_type
	response.set_header('Cache-Control', 'max-age:3600,public')
	return outputter(page_type, info, filterkey)

@route('/<type:re:(artist|album|product|event|org)>/<id:int>')
def info(type,id):
	cache_key = 'vgmdb/%s/%s'%(type,id)
	page_type = type
	url = 'http://vgmdb.net/%s/%s?perpage=99999'%(type,id)
	link = "/%s/%s"%(type,id)
	return do_page(cache_key, page_type, url, link)

@route('/<type:re:(albumlist|artistlist|productlist)>/<id:re:[#A-Z]>')
@route('/<type:re:(albumlist|artistlist|productlist)>/')
@route('/<type:re:(albumlist|artistlist|productlist)>')
def list(type,id='A'):
	typeurls = {'albumlist': 'albums',
	            'artistlist': 'artists',
	            'productlist': 'product'}
	cache_key = 'vgmdb/%s/%s'%(type,id)
	page_type = type
	url = 'http://vgmdb.net/db/%s.php?ltr=%s&field=title&perpage=9999'%(typeurls[type],id)
	if id:
		link = '%s/%s'%(type, id)
	else:
		link = '%s'%(type,)
	return do_page(cache_key, page_type, url, link=link)

@route('/<type:re:(orglist)>/<filterkey:re:[#A-Z]>')
@route('/<type:re:(orglist)>/')
@route('/<type:re:(orglist)>')
def orglist(type,filterkey=None):
	typeurls = {'orglist': 'org'}
	cache_key = 'vgmdb/%s'%(type,)
	page_type = type
	url = 'http://vgmdb.net/db/%s.php'%(typeurls[type])
	if filterkey:
		link = '%s/%s'%(type, urllib.quote(filterkey))
	else:
		link = '%s'%(type,)
	return do_page(cache_key, page_type, url, link=link, filterkey=filterkey)

@route('/<type:re:(eventlist)>/<filterkey:int>')
@route('/<type:re:(eventlist)>/')
@route('/<type:re:(eventlist)>')
def eventlist(type,filterkey=None):
	typeurls = {'eventlist': 'events'}
	cache_key = 'vgmdb/%s'%(type,)
	page_type = type
	url = 'http://vgmdb.net/db/%s.php'%(typeurls[type])
	if filterkey:
		link = '%s/%s'%(type, filterkey)
		filterkey = str(filterkey)
	else:
		link = '%s'%(type,)
	return do_page(cache_key, page_type, url, link=link, filterkey=filterkey)

@route('/search/<type:re:(albums|artists|orgs|products)>/<query>')
@route('/search/<query>')
@route('/search')
def search(type=None, query=None):
	query = query or request.query['q']
	cache_key = 'vgmdb/search/%s'%(base64.b64encode(query),)
	page_type = 'search'
	url = 'http://vgmdb.net/search?q=%s'%(urllib.quote(query))
	if type:
		link = 'search/%s/%s'%(type,urllib.quote(query))
	else:
		link = 'search/%s'%(urllib.quote(query),)
	filterkey = type
	return do_page(cache_key, page_type, url, link=link, filterkey=filterkey)

@route('/')
@route('/about')
def about():
	outputter = vgmdb.output.get_outputter('html', None)
	response.content_type = outputter.content_type
	return outputter('about', {}, None)

@route('/static/<name:path>')
def static(name):
	response.set_header('Cache-Control', 'max-age:3600,public')
	return static_file(name, root='./static')
