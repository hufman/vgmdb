from bottle import route, response, request, static_file, abort
import urllib
import json

import vgmdb.artist
import vgmdb.album
import vgmdb.product
import vgmdb.event
import vgmdb.org

import vgmdb.albumlist
import vgmdb.artistlist
import vgmdb.productlist

import vgmdb.cache
import vgmdb.output

try:
	import simplejson as json
except:
	pass

@route('/hello')
def hello():
	return "Hello!"

@route('/<type:re:(artist|album|product|event|org)>/<id:int>')
def info(type,id):
	prevdata = vgmdb.cache.get('vgmdb/%s/%s'%(type,id))
	if not prevdata:
		data = urllib.urlopen('http://vgmdb.net/%s/%s?perpage=99999'%(type,id)).read()
		data = data.decode('utf-8', 'ignore')	# some pages have broken utf8
		module = getattr(vgmdb, type)
		parse_page = getattr(module, "parse_%s_page"%type)
		info = parse_page(data)
		if info != None:
			info['link'] = "/%s/%s"%(type,id)
			vgmdb.cache.set('vgmdb/%s/%s'%(type,id), info)
	else:
		info = prevdata
	if info == None:
		abort(404, "Item not found")

	requested_format = request.query.format or ''
	outputter = vgmdb.output.get_outputter(requested_format, request.headers.get('Accept'))
	response.content_type = outputter.content_type
	return outputter(type, info)

@route('/<type:re:(albumlist|artistlist|productlist)>/<id:re:[#A-Z]>')
def list(type,id):
	typeurls = {'albumlist': 'albums',
	            'artistlist': 'artists',
	            'productlist': 'product'}
	prevdata = vgmdb.cache.get('vgmdb/%s/%s'%(type,id))
	if not prevdata:
		data = urllib.urlopen('http://vgmdb.net/db/%s.php?ltr=%s&field=title&perpage=9999'%(typeurls[type],id)).read()
		data = data.decode('utf-8', 'ignore')	# some pages have broken utf8
		module = getattr(vgmdb, "%s"%type)
		parse_page = getattr(module, "parse_%s_page"%type)
		info = parse_page(data)
		if info != None:
			info['link'] = "/%s/%s"%(type,id)
			vgmdb.cache.set('vgmdb/%s/%s'%(type,id), info)
	else:
		info = prevdata
	if info == None:
		abort(404, "Item not found ")

	requested_format = request.query.format or ''
	outputter = vgmdb.output.get_outputter(requested_format, request.headers.get('Accept'))
	response.content_type = outputter.content_type
	return outputter(type, info)

@route('/static/<name:path>')
def static(name):
	return static_file(name, root='./static')
