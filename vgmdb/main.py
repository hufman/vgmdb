from bottle import route, response
import urllib
import json
import vgmdb.artist
import vgmdb.album
import vgmdb.product
import vgmdb.event
import vgmdb.org
import vgmdb.cache

try:
	import simplejson as json
except:
	pass

@route('/hello')
def hello():
	return "Hello!"

@route('/<type:re:(artist|album|product|event|org)>/<id:int>')
def info(type,id):
	prevdata = vgmdb.cache.get('%s/%s'%(type,id))
	if not prevdata:
		data = urllib.urlopen('http://vgmdb.net/%s/%s?perpage=99999'%(type,id)).read()
		data = data.decode('utf-8', 'ignore')	# some pages have broken utf8
		module = getattr(vgmdb, type)
		parse_page = getattr(module, "parse_%s_page"%type)
		info = parse_page(data)
		vgmdb.cache.set('%s/%s'%(type,id), info)
	else:
		info = prevdata

	response.content_type = 'application/json; charset=utf-8'
	return json.dumps(info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)

