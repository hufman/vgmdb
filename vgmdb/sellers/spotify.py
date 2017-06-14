import urllib
import urllib2
import urlparse
import base64
import datetime
import json
import logging
from ._utils import squash_str, find_best_match, primary_name
from .. import config

AUTH_API = 'https://accounts.spotify.com/api/token'
SEARCH_API = 'https://api.spotify.com/v1/search'
access_token = None
access_expires = None

def authenticate():
	if config.SPOTIFY_ID is None or len(config.SPOTIFY_ID) < 10:
		raise Exception("Invalid SPOTIFY_ID")
	data = urllib.urlencode({'grant_type': 'client_credentials'})
	request = urllib2.Request(AUTH_API, data=data)
	auth = base64.b64encode("%s:%s" % (config.SPOTIFY_ID, config.SPOTIFY_SECRET))
	request.add_header('Authorization', 'Basic %s' % (auth,))
	opener = urllib2.build_opener()
	response = opener.open(request).read()
	response = json.loads(response)
	# save auth info
	global access_token
	global access_expires
	access_token = response['access_token']
	access_expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=response['expires_in'])

def search(query):
	time_in_10_minutes = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
	if access_expires is None or access_expires < time_in_10_minutes:
		authenticate()
	if access_expires is None:
		raise Exception("Failed to authenticate to Spotify API")
	url = SEARCH_API + '?' + query
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'VGMdb/1.0 vgmdb.info')
	request.add_header('Authorization', 'Bearer %s' % (access_token,))
	opener = urllib2.build_opener()
	return opener.open(request).read()

class NullHandler(logging.Handler):
	def emit(self, record):
		pass
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

def empty_album(info):
	search_url = "https://play.spotify.com/search/%s%%3Aalbums"%(urllib.quote(squash_str(info['name'])),)
	result = {"name":"Spotify",
	          "icon":"static/spotify.png",
	          "search": search_url
	         }
	return result
def search_album(info):
	result = empty_album(info)
	try:
		found = None
		if not found:
			found = search_artist_album_name(info)
			if found:
				result['surity'] = 'artist+album'
		if not found:
			found = search_album_name(info)
			if found:
				result['surity'] = 'album'
		if found:
			result['found'] = found['external_urls']['spotify']
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_artist_album_name(info):
	if not( 'composers' in info and len(info['composers']) > 0):
		return None
	title = info['name']
	artist = primary_name(info['composers'][0]['names'])
	webdata = search("q=artist:%s+album:%s&type=album"%(urllib.quote(squash_str(artist)),urllib.quote(squash_str(title))))
	data = json.loads(webdata)
	found = find_best_match(squash_str(title), data['albums']['items'],
	   threshold=0.5, key=lambda x:squash_str(x['name']))
	return found

def search_album_name(info):
	title = info['name']
	webdata = search("q=album:%s&type=album"%(urllib.quote(squash_str(title)),))
	data = json.loads(webdata)
	found = find_best_match(squash_str(title), data['albums']['items'],
	   threshold=0.5, key=lambda x:squash_str(x['name']))
	return found

def empty_artist(info):
	search_url = "https://play.spotify.com/search/%s%%3Aartists"%(urllib.quote(squash_str(info['name'])),)
	result = {"name":"Spotify",
	          "icon":"static/spotify.png",
	          "search": search_url
	         }
	return result
def search_artist(info):
	result = empty_artist(info)
	try:
		found = search_artist_name(info['name'])
		if found:
			result['surity'] = 'name'
			result['found'] = found['external_urls']['spotify']
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_artist_name(name):
	webdata = search("q=artist:%s&type=artist"%(urllib.quote(squash_str(name))))
	data = json.loads(webdata)
	found = find_best_match(squash_str(name), data['artists']['items'],
	   threshold=0.7, key=lambda x:squash_str(x['name']))
	return found
