import urllib
import urlparse
import json
from ._utils import squash_str,find_best_match

SEARCH_API = 'http://api.discogs.com/database/search'

def search_album(info):
	search_url = "http://www.discogs.com/search?q=%s&type=master"%(urllib.quote(info['name']),)
	result = {"name":"discogs",
	          "icon":"http://s.pixogs.com/images/record32.ico",
	          "search": search_url
	         }
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
	return result

def search_album_catalog(catalog):
	url = SEARCH_API + '?type=master&catno=%s'%(urllib.quote(catalog),)
	webdata = urllib.urlopen(url).read()
	data = json.loads(webdata)
	found = find_best_match(squash_str(catalog), data['results'],
	   threshold=0.9, key=lambda x:squash_str(x['catno']))
	return found

def search_artist_album_name(info):
	artist = info['composers'][0]['names']['en']
	title = info['name']
	url = SEARCH_API + "?type=master&artist=%s&release_title=%s"%(urllib.quote(artist),urllib.quote(title))
	webdata = urllib.urlopen(url).read()
	data = json.loads(webdata)
	found = find_best_match(squash_str(title), data['results'],
	   threshold=0.7, key=lambda x:squash_str(x['title']))
	return found

def search_album_name(info):
	title = info['name']
	url = SEARCH_API + "?type=master&release_title=%s"%(urllib.quote(title),)
	webdata = urllib.urlopen(url).read()
	data = json.loads(webdata)
	found = find_best_match(squash_str(title), data['results'],
	   threshold=0.7, key=lambda x:squash_str(x['title']))
	return found

def search_artist(info):
	search_url = "http://www.discogs.com/search?q=%s&type=master"%(urllib.quote(info['name']),)
	result = {"name":"discogs",
	          "icon":"http://s.pixogs.com/images/record32.ico",
	          "search": search_url
	         }
	found = search_artist_name(info['name'])
	if found:
		result['surity'] = 'name'
		result['found'] = urlparse.urljoin("http://discogs.com/",found['uri'])
	return result

def search_artist_name(name):
	url = SEARCH_API + "?type=artist&q=%s"%(urllib.quote(name))
	webdata = urllib.urlopen(url).read()
	data = json.loads(webdata)
	found = find_best_match(squash_str(name), data['results'],
	   threshold=0.7, key=lambda x:squash_str(x['title']))
	return found
