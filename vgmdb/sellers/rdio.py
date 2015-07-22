import urllib
import urllib2
import base64
import urlparse
import json
import logging
from ._utils import squash_str, find_best_match, primary_name
from .. import config

class NullHandler(logging.Handler):
	def emit(self, record):
		pass

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

BASE_SEARCH_URL = 'http://www.rdio.com/search/'
API_URL = 'https://services.rdio.com/api/1/'
TOKEN_URL = 'https://services.rdio.com/oauth2/token'

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

def request_token():
	auth = base64.standard_b64encode('%s:%s' % (config.RDIO_KEY, config.RDIO_SECRET))
	headers = {'Authorization': 'Basic %s' % (auth,)}
	data = 'grant_type=client_credentials'
	req = urllib2.Request(TOKEN_URL, data, headers)
	try:
		result = urllib2.urlopen(req)
	except urllib2.HTTPError as e:
		logger.error('Bad status code while getting access token (%s): %s' % (e.code, e.read()))
		raise e
	parsed = json.load(result)
	return parsed['access_token']

def api(args={}):
	access_token = request_token()
	args = dict([(k, v.encode('utf-8')) for k,v in args.items()])
	body = urllib.urlencode(args)
	headers = {
		'User-Agent': 'VGMdb/1.0 vgmdb.info',
		'Content-Type': 'application/x-www-form-urlencoded',
		'Authorization': 'Bearer %s' % (access_token, )
	}
	req = urllib2.Request(API_URL, body, headers)
	try:
		result = urllib2.urlopen(req)
	except urllib2.HTTPError as e:
		logger.error('Bad status code while searching (%s): %s' % (e.code, e.read()))
		raise e
	return json.load(result)

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
	try:
		result = empty_artist(info)
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
	if 'composers' in info and len(info['composers']) > 0:
		artist_name = primary_name(info['composers'][0]['names'])
	else:
		artist_name = ''
	album_name = info['name']
	result['search'] = url_search_album("%s %s"%(artist_name, album_name))
	return result
def search_album(info):
	try:
		result = empty_album(info)
		if 'composers' in info and len(info['composers']) > 0:
			artist_name = primary_name(info['composers'][0]['names'])
		else:
			artist_name = ''
		album_name = info['name']
		found = search_album_name(artist_name, album_name)
		if found:
			result['surity'] = 'name'
			result['found'] = urlparse.urljoin('http://www.rdio.com', found['url'])
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result
