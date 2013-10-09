from bottle import route, response, request, static_file, abort
import urllib

import vgmdb.request
import vgmdb.sellers

import vgmdb.config
import vgmdb.output

@route('/hello')
def hello():
	return "Hello!"

def do_page(page_type, info, filterkey=None):
	"""
	@param info is what data to output
	@param filterkey some pages have data that can be filtered in the output
	"""
	if info == None:
		abort(404, "Item not found")

	# figure out what format the user wants
	requested_format = request.query.format or ''
	outputter = vgmdb.output.get_outputter(vgmdb.config.for_request(request), requested_format, request.headers.get('Accept'))

	# add in any seller information
	if False and outputter.content_type[:9] == 'text/html':
		sellers = vgmdb.sellers.search_info(page_type, id, info, start_search=True, wait=False)
		info['sellers'] = sellers
		not_searched = any(['not_searched' in item for item in sellers])
		searching = any(['searching' in item for item in sellers])
		if not_searched or searching:
			response.set_header('Cache-Control', 'max-age:60,public')
		else:
			response.set_header('Cache-Control', 'max-age:3600,public')
	else:
		response.set_header('Cache-Control', 'max-age:3600,public')

	# output
	response.content_type = outputter.content_type
	return outputter(page_type, info, filterkey)

@route('/<type:re:(artist|album|product|event|org)>/<id:int>')
def info(type,id):
	return do_page(type, vgmdb.request.info(type,id))

@route('/<type:re:(albumlist|artistlist|productlist)>/<id:re:[#A-Z]>')
@route('/<type:re:(albumlist|artistlist|productlist)>/')
@route('/<type:re:(albumlist|artistlist|productlist)>')
def list(type,id='A'):
	return do_page(type, vgmdb.request.list(type,id))

@route('/<type:re:(orglist)>/<filterkey:re:[#A-Z]>')
@route('/<type:re:(eventlist)>/<filterkey:int>')
@route('/<type:re:(orglist|eventlist)>/')
@route('/<type:re:(orglist|eventlist)>')
def singlelist(type,filterkey=None):
	return do_page(type, vgmdb.request.list(type, filterkey), filterkey=filterkey)

@route('/search/<type:re:(albums|artists|orgs|products)>/<query>')
@route('/search/<type:re:(albums|artists|orgs|products)>')
@route('/search/<query>')
@route('/search')
def search(type=None, query=None):
	# Handle the case of /search/albums?q=
	if query in ['albums','artists','orgs','products']:
		type = query
		query = None
	query = query or request.query['q']
	return do_page('search', vgmdb.request.search(type, query), filterkey=type)

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
