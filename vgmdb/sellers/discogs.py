import urllib
import urllib2
import urlparse
import json
import logging
from ._utils import squash_str,find_best_match, primary_name
from .. import config

SEARCH_API = 'https://api.discogs.com/database/search'

def search(query):
	url = SEARCH_API + '?' + query
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'VGMdb/1.0 vgmdb.info')
	if hasattr(config, 'DISCOGS_KEY') and hasattr(config, 'DISCOGS_SECRET'):
		request.add_header('Authorization', 'Discogs key=%s, secret=%s'%(config.DISCOGS_KEY, config.DISCOGS_SECRET))
	opener = urllib2.build_opener()
	return opener.open(request).read()

class NullHandler(logging.Handler):
	def emit(self, record):
		pass
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

def empty_album(info):
	search_url = "http://www.discogs.com/search?q=%s&type=master"%(urllib.quote(squash_str(info['name'])),)
	result = {"name":"discogs",
	          "icon":"static/discogs.ico",
	          "search": search_url
	         }
	return result
def search_album(info):
	result = empty_album(info)
	try:
		found = None
		if 'catalog' in info:
			found = search_album_catalog(info['catalog'])
			if found:
				result['surity'] = 'catalog'
		if not found:
			found = search_artist_album_name(info)
			if found:
				result['surity'] = 'artist+album'
		if not found:
			found = search_album_name(info)
			if found:
				result['surity'] = 'album'
		if found:
			result['found'] = urlparse.urljoin("http://discogs.com/",found['uri'])
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_album_catalog(catalog):
	webdata = search('type=master&catno=%s'%(urllib.quote(squash_str(catalog)),))
	data = json.loads(webdata)
	found = find_best_match(squash_str(catalog), data['results'],
	   threshold=0.9, key=lambda x:squash_str(x['catno']))
	return found

def search_artist_album_name(info):
	if not ('composers' in info and len(info['composers']) > 0):
		return None
	artist = primary_name(info['composers'][0]['names'])
	title = info['name']
	webdata = search("type=master&artist=%s&release_title=%s"%(urllib.quote(squash_str(artist)),urllib.quote(squash_str(title))))
	data = json.loads(webdata)
	found = find_best_match(squash_str(title), data['results'],
	   threshold=0.5, key=lambda x:squash_str(x['title']))
	return found

def search_album_name(info):
	title = info['name']
	webdata = search("type=master&release_title=%s"%(urllib.quote(squash_str(title)),))
	data = json.loads(webdata)
	found = find_best_match(squash_str(title), data['results'],
	   threshold=0.5, key=lambda x:squash_str(x['title']))
	return found

def empty_artist(info):
	search_url = "http://www.discogs.com/search?q=%s&type=artist"%(urllib.quote(squash_str(info['name'])),)
	result = {"name":"discogs",
	          "icon":"static/discogs.ico",
	          "search": search_url
	         }
	return result
def search_artist(info):
	result = empty_artist(info)
	try:
		found = search_artist_name(info['name'])
		if found:
			result['surity'] = 'name'
			result['found'] = urlparse.urljoin("http://discogs.com/",found['uri'])
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_artist_name(name):
	webdata = search("type=artist&q=%s"%(urllib.quote(squash_str(name))))
	data = json.loads(webdata)
	found = find_best_match(squash_str(name), data['results'],
	   threshold=0.7, key=lambda x:squash_str(x['title']))
	return found
