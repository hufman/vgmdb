import urllib
import urlparse
import json
import logging
from ._utils import squash_str,find_best_match

SEARCH_API = 'https://itunes.apple.com/search?media=music&'

class NullHandler(logging.Handler):
	def emit(self, record):
		pass
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

def search_album(info):
	search_url = SEARCH_API+'entity=album&term=%s'%(urllib.quote(squash_str(info['name'])),)
	result = {"name":"iTunes",
	          "icon":"https://upload.wikimedia.org/wikipedia/en/0/0c/ITunes_11_Logo.png"
	         }
	try:
		found = None
		found = search_album_name(info)
		if found:
			result['surity'] = 'album'
		if found:
			result['image'] = found['artworkUrl100']
			result['found'] = found['collectionViewUrl']
	except:
		import traceback
		logger.warning(traceback.format_exc())
	return result

def search_album_name(info):
	title = info['name']
	url = SEARCH_API + "entity=album&term=%s"%(urllib.quote(squash_str(title)),)
	webdata = urllib.urlopen(url).read()
	data = json.loads(webdata)
	found = find_best_match(squash_str(title), data['results'],
	   threshold=0.5, key=lambda x:squash_str(x['collectionName']))
	return found

def search_artist(info):
	search_url = SEARCH_API+'entity=musicArtist&term=%s'%(urllib.quote(squash_str(info['name'])),)
	result = {"name":"iTunes",
	          "icon":"https://upload.wikimedia.org/wikipedia/en/0/0c/ITunes_11_Logo.png"
	         }
	try:
		found = search_artist_name(info['name'])
		if found:
			result['surity'] = 'name'
			result['found'] = found['artistLinkUrl']
	except:
		import traceback
		logger.warning(traceback.format_exc())
	return result

def search_artist_name(name):
	url = SEARCH_API+'entity=musicArtist&term=%s'%(urllib.quote(squash_str(name)),)
	webdata = urllib.urlopen(url).read()
	data = json.loads(webdata)
	found = find_best_match(squash_str(name), data['results'],
	   threshold=0.7, key=lambda x:squash_str(x['artistName']))
	return found
