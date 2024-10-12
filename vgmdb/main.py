from bottle import route, response, request, static_file, abort, hook, error
import urllib
from functools import wraps

from datetime import datetime
import email.utils

import vgmdb.fetch
import vgmdb.sellers

import vgmdb.config
import vgmdb.metrics
from vgmdb.metrics import instrumented
import vgmdb.output


if vgmdb.config.SEARCH_INDEX:
	import vgmdb.parsers.search
	vgmdb.parsers.search.generate_search_index()

if vgmdb.config.STATSD_HOST:
	host, port = vgmdb.config.STATSD_HOST.split(':', 1)
	port = int(port)
	vgmdb.metrics.initialize(host, port)


@route('/hello')
def hello():
	return "Hello!"

@hook('after_request')
def add_cors_headers():
	response.set_header('Access-Control-Allow-Origin', '*')
	response.set_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
	headers = request.headers.get('Access-Control-Request-Headers')
	if not headers:
		headers = 'Origin, User-Agent, If-Modified-Since, Cache-Control'
	response.set_header('Access-Control-Allow-Headers', headers)

@error(405)
def method_unsupported(error):
	if request.method == 'OPTIONS':
		response.status = 200
		add_cors_headers()
		return 'Of course, this API is free for everyone!'

def catch_exceptions(func):
	"""
	Used as a decorator around functions that could raise an exception
	"""
	@wraps(func)
	def func_wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except IOError:
			# failed to connect to vgmdb.net
			abort(503, "vgmdb.net is temporarily unavailable")
	return func_wrapper

def do_page(page_type, info, filterkey=None):
	"""
	@param info is what data to output
	@param filterkey some pages have data that can be filtered in the output
	"""
	if info == None:
		abort(404, "Item not found")

	# figure out what format the user wants
	requested_format = request.query.format or ''
	outputter = vgmdb.output.get_outputter(vgmdb.config.for_request(request), requested_format, request.headers.get('Accept', ''), request.headers.get('User-Agent', ''))

	# figure out the cache ttl
	edited_date = None
	ttl = 24 * 60 * 60	# 1 day default
	if 'meta' in info and 'edited_date' in info['meta']:
		try:
			edited_date = datetime.strptime(info['meta']['edited_date'], '%Y-%m-%dT%H:%M')
			if 'ttl' in info['meta']:
				ttl = info['meta']['ttl']
		except:
			pass

	# add in any seller information
	if outputter.content_type[:9] == 'text/html':
		sellers = vgmdb.sellers.search_info(page_type, info['link'].split('/')[-1], info, start_search=True, wait=False)
		info['sellers'] = sellers
		not_searched = any(['not_searched' in item for item in sellers])
		searching = any(['searching' in item for item in sellers])
		if not_searched or searching:
			response.set_header('Cache-Control', 'max-age:60,public')
		else:
			response.set_header('Cache-Control', 'max-age:%s,public'%(ttl,))
	else:
		response.set_header('Cache-Control', 'max-age:%s,public'%(ttl,))

	# output
	response.content_type = outputter.content_type
	if edited_date:
		epoch = datetime(1970,1,1)
		unix_time = (edited_date - epoch).total_seconds()
		out_time = email.utils.formatdate(timeval=unix_time, localtime=True, usegmt=True)
		response.set_header('Last-Modified', out_time)
	return outputter(page_type, info, filterkey)

@route('/<type:re:(artist|album|product|release|event|org)>/<id:int>')
@catch_exceptions
@instrumented
def info(type,id):
	return do_page(type, vgmdb.fetch.info(type,id))

@route('/<type:re:(albumlist|artistlist|productlist)>/<id:re:[#A-Z][0-9]*>')
@route('/<type:re:(albumlist|artistlist|productlist)>/')
@route('/<type:re:(albumlist|artistlist|productlist)>')
@catch_exceptions
@instrumented
def list(type,id='A1'):
	return do_page(type, vgmdb.fetch.list(type,id))

@route('/<type:re:(orglist)>/<filterkey:re:[#A-Z]>')
@route('/<type:re:(eventlist)>/<filterkey:int>')
@route('/<type:re:(orglist|eventlist)>/')
@route('/<type:re:(orglist|eventlist)>')
@catch_exceptions
@instrumented(name='list')
def singlelist(type,filterkey=None):
	return do_page(type, vgmdb.fetch.list(type, filterkey), filterkey=filterkey)

@route('/search/<type:re:(albums|artists|orgs|products)>/<query>')
@route('/search/<type:re:(albums|artists|orgs|products)>')
@route('/search/<query>')
@route('/search')
@catch_exceptions
@instrumented(page_type='')
def search(type=None, query=None):
	# Handle the case of /search/albums?q=
	if query in ['albums','artists','orgs','products']:
		type = query
		query = None
	query = query or request.query.get('q', "")
	return do_page('search', vgmdb.fetch.search(type, query), filterkey=type)

@route('/recent/<type:re:(albums|media|tracklists|scans|artists|products|labels|links|ratings)>')
@route('/recent')
@catch_exceptions
@instrumented
def recent(type='albums'):
	return do_page('recent', vgmdb.fetch.recent(type))

@route('/')
@route('/about')
def about():
	outputter = vgmdb.output.get_outputter(vgmdb.config.for_request(request), 'html', None)
	response.content_type = outputter.content_type
	return outputter('about', {}, None)

@route('/<type:re:(album|artist)>/<id:int>/sellers')
@instrumented
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

@route('/opensearch.xml')
def opensearch():
	#response.set_header('Cache-Control', 'max-age:86400,public')
	outputter = vgmdb.output.get_outputter(vgmdb.config.for_request(request), 'html', None)
	response.content_type = "application/opensearchdescription+xml"
	return outputter('opensearch', {}, None)

@route('/static/<name:path>')
def static(name):
	response.set_header('Cache-Control', 'max-age:3600,public')
	return static_file(name, root='./static')

@route('/schema/<name:path>')
def schema(name):
	#response.set_header('Cache-Control', 'max-age:3600,public')
	return static_file(name, root='./schema', mimetype='application/json')
@route('/raml/<name:path>')
def raml(name):
	response.set_header('Cache-Control', 'max-age:3600,public')
	mimetype = "application/raml+yaml"
	if 'text/html' in request.headers.get('Accept', ''):  # browser
		mimetype = "text/plain"
	return static_file(name, root='./raml', mimetype=mimetype)
