import urllib
import urllib2
import urlparse
import json
import logging
import oauth2 as oauth
from ._utils import squash_str, find_best_match
from .. import config

class NullHandler(logging.Handler):
	def emit(self, record):
		pass

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

BASE_SEARCH_URL = 'http://www.rdio.com/search/'
BASE_SEARCH_API = 'http://api.rdio.com/1/'

result_template = {
	'name': 'Rdio',
	'icon': 'static/rdio.png'
}

def quote_search(name):
	return urllib.quote(squash_str(name))
def url_search_artist(name):
	return "%s%s/artists/" % (BASE_SEARCH_URL, quote_search(name))
def url_search_album(name):
	return "%s%s/albums/" % (BASE_SEARCH_URL, quote_search(name))

def api(args={}):
	body = urllib.urlencode(args)
	headers = {
		'User-Agent': 'VGMdb/1.0 vgmdb.info',
		'Content-Type': 'application/x-www-form-urlencoded'
	}
	consumer = oauth.Consumer(config.RDIO_KEY, config.RDIO_SECRET)
	client = oauth.Client(consumer)
	response, content = client.request(BASE_SEARCH_API, 'POST', body, headers)
	return json.loads(content)

def api_search_artist(name):
	data = {
		'method': 'search',
		'query': name,
		'types': 'Artist',
		'extras': '-*,name,url'
	}
	ret = api(data)
	return ret['result']['results']

def api_search_album(name):
	data = {
		'method': 'search',
		'query': name,
		'types': 'Album',
		'extras': '-*,name,url'
	}
	ret = api(data)
	return ret['result']['results']

def search_artist_name(name):
	results = api_search_artist(name)
	found = find_best_match(squash_str(name), results,
	   threshold=0.7, key=lambda x:squash_str(x['name']))
	return found

def search_album_name(artist, name):
	results = api_search_album("%s %s"%(artist, name))
	found = find_best_match(squash_str(name), results,
	   threshold=0.5, key=lambda x:squash_str(x['name']))
	return found

def empty_artist(info):
	result = dict(result_template)
	result['search'] = url_search_artist(info['name'])
	return result
def search_artist(info):
	result = empty_artist(info)
	try:
		found = search_artist_name(info['name'])
		if found:
			result['surity'] = 'name'
			result['found'] = urlparse.urljoin('http://www.rdio.com', found['url'])
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def empty_album(info):
	result = dict(result_template)
	artist_name = info['composers'][0]['names']['en']
	album_name = info['name']
	result['search'] = url_search_album("%s %s"%(artist_name, album_name))
	return result
def search_album(info):
	result = empty_album(info)
	artist_name = info['composers'][0]['names']['en']
	album_name = info['name']
	try:
		found = search_album_name(artist_name, album_name)
		if found:
			result['surity'] = 'name'
			result['found'] = urlparse.urljoin('http://www.rdio.com', found['url'])
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result
