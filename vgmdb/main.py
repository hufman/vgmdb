from bottle import route, response
import urllib
import json
import vgmdb.artist
import vgmdb.album

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
