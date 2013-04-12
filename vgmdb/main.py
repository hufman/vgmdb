from bottle import route, response
import urllib
import json
import vgmdb.artist

@route('/hello')
def hello():
	return "Hello!"

@route('/artist/<artist:int>')
def artist(artist):
	data = urllib.urlopen('http://vgmdb.net/artist/%s'%artist).read()
	artist_info = vgmdb.artist.parse_artist_page(data)
	response.content_type = 'application/json; charset=utf-8'
	return json.dumps(artist_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
