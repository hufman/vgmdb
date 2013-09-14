import urllib
import urlparse
import json
import logging
from ._utils import squash_str,find_best_match
from .. import config

SEARCH_API = 'https://itunes.apple.com/search?media=music&'
AFFILIATE_ID = getattr(config, 'ITUNES_AFFILIATE_ID', None)
TD_PROGRAM_ID = getattr(config, 'ITUNES_TD_PROGRAM_ID', None)
TD_WEBSITE_ID = getattr(config, 'ITUNES_TD_WEBSITE_ID', None)

class NullHandler(logging.Handler):
	def emit(self, record):
		pass
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

def add_affiliate_id(link):
	query = 3
	TD_URL = "http://clk.tradedoubler.com/click?p=%s&a=%s&url=%s"
	if AFFILIATE_ID:
		parts = list(urlparse.urlsplit(link))
		if parts[query] == '':
			parts[query] += '?'
		else:
			parts[query] += '&'
		parts[query] += 'at=%s'%(AFFILIATE_ID,)
		link = urlparse.urlunsplit(parts)
	if TD_PROGRAM_ID and TD_WEBSITE_ID:
		parts = list(urlparse.urlsplit(link))
		if parts[query] == '':
			parts[query] += '?'
		else:
			parts[query] += '&'
		parts[query] += 'partnerId=2003'
		link = urlparse.urlunsplit(parts)
		link = TD_URL % (TD_PROGRAM_ID, TD_WEBSITE_ID, urllib.quote(link))
	return link

def empty_album(info):
	search_url = SEARCH_API+'entity=album&term=%s'%(urllib.quote(squash_str(info['name'])),)
	result = {"name":"iTunes",
	          "icon":"https://upload.wikimedia.org/wikipedia/en/0/0c/ITunes_11_Logo.png"
	         }
	return result
def search_album(info):
	result = empty_album(info)
	try:
		found = None
		found = search_album_name(info)
		if found:
			result['surity'] = 'album'
		if found:
			result['image'] = found['artworkUrl100']
			result['found'] = found['collectionViewUrl']
			result['found'] = add_affiliate_id(result['found'])
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_album_name(info):
	title = info['name']
	url = SEARCH_API + "entity=album&term=%s"%(urllib.quote(squash_str(title)),)
	webdata = urllib.urlopen(url).read()
	data = json.loads(webdata)
	found = find_best_match(squash_str(title), data['results'],
	   threshold=0.5, key=lambda x:squash_str(x['collectionName']))
	return found

def empty_artist(info):
	search_url = SEARCH_API+'entity=musicArtist&term=%s'%(urllib.quote(squash_str(info['name'])),)
	result = {"name":"iTunes",
	          "icon":"https://upload.wikimedia.org/wikipedia/en/0/0c/ITunes_11_Logo.png"
	         }
	return result
def search_artist(info):
	result = empty_artist(info)
	try:
		found = search_artist_name(info['name'])
		if found:
			result['surity'] = 'name'
			result['found'] = found['artistLinkUrl']
			result['found'] = add_affiliate_id(result['found'])
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_artist_name(name):
	url = SEARCH_API+'entity=musicArtist&term=%s'%(urllib.quote(squash_str(name)),)
	webdata = urllib.urlopen(url).read()
	data = json.loads(webdata)
	found = find_best_match(squash_str(name), data['results'],
	   threshold=0.7, key=lambda x:squash_str(x['artistName']))
	return found
