from bottle import route, response
import urllib
import json
import vgmdb.artist
import vgmdb.album
import vgmdb.product
import vgmdb.event
import vgmdb.org

@route('/hello')
def hello():
	return "Hello!"

@route('/artist/<artist:int>')
def artist(artist):
	data = urllib.urlopen('http://vgmdb.net/artist/%s'%artist).read()
	data = data.decode('utf-8', 'ignore')	# some pages have broken utf8
	artist_info = vgmdb.artist.parse_artist_page(data)
	response.content_type = 'application/json; charset=utf-8'
	return json.dumps(artist_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)

@route('/album/<album:int>')
def album(album):
	data = urllib.urlopen('http://vgmdb.net/album/%s'%album).read()
	data = data.decode('utf-8', 'ignore')	# some pages have broken utf8
	album_info = vgmdb.album.parse_album_page(data)
	response.content_type = 'application/json; charset=utf-8'
	return json.dumps(album_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)

@route('/product/<product:int>')
def product(product):
	data = urllib.urlopen('http://vgmdb.net/product/%s'%product).read()
	data = data.decode('utf-8', 'ignore')	# some pages have broken utf8
	product_info = vgmdb.product.parse_product_page(data)
	response.content_type = 'application/json; charset=utf-8'
	return json.dumps(product_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)

@route('/event/<event:int>')
def event(event):
	data = urllib.urlopen('http://vgmdb.net/event/%s?perpage=99999'%event).read()
	data = data.decode('utf-8', 'ignore')	# some pages have broken utf8
	event_info = vgmdb.event.parse_event_page(data)
	response.content_type = 'application/json; charset=utf-8'
	return json.dumps(event_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)

@route('/org/<org:int>')
def org(org):
	data = urllib.urlopen('http://vgmdb.net/org/%s'%org).read()
	data = data.decode('utf-8', 'ignore')	# some pages have broken utf8
	org_info = vgmdb.org.parse_org_page(data)
	response.content_type = 'application/json; charset=utf-8'
	return json.dumps(org_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
