import urllib
import urlparse
import json
import logging
import time

from .. import config
from ._utils import squash_str,find_best_match, primary_name
import amazonproduct

class NullHandler(logging.Handler):
	def emit(self, record):
		pass
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

if hasattr(config, 'AMAZON_ASSOCIATE_TAG') and config.AMAZON_ASSOCIATE_TAG:
	SEARCH_PAGE = 'http://www.amazon.com/s/?_encoding=UTF8&url=search-alias%%3Dpopular&SubscriptionId=%s&AssociateTag=%s&linkCode=ur2&tag=%s'%(config.AMAZON_ACCESS_KEY_ID,config.AMAZON_ASSOCIATE_TAG,config.AMAZON_ASSOCIATE_TAG)
else:
	SEARCH_PAGE = 'http://www.amazon.com/s/?_encoding=UTF8&url=search-alias%%3Dpopular'

if hasattr(config, 'AMAZON_ACCESS_KEY_ID') and config.AMAZON_ACCESS_KEY_ID and \
   hasattr(config, 'AMAZON_SECRET_ACCESS_KEY') and config.AMAZON_SECRET_ACCESS_KEY:
	api_config = {
		'access_key': config.AMAZON_ACCESS_KEY_ID,
		'secret_key': config.AMAZON_SECRET_ACCESS_KEY,
		'locale': 'us',
		'associate_tag': getattr(config, 'AMAZON_ASSOCIATE_TAG', 'vgmdb')
	}
	#API = api.API(config.AMAZON_ACCESS_KEY_ID, config.AMAZON_SECRET_ACCESS_KEY, 'us', getattr(config, 'AMAZON_ASSOCIATE_TAG', 'vgmdb'))
	API = amazonproduct.API(cfg=api_config)
else:
	API = None

def parse_results(roots):
	results = []
	for root in roots:
		nspace = root.nsmap.get(None, '')
		xml_results = root.xpath('//aws:Item',
		                         namespaces={'aws':nspace})
		for xml_result in xml_results:
			try:
				url = xml_result.DetailPageURL.text
				if '%3F' in url or '%ef' in url:
					url = urllib.unquote(url)
				result = {"DetailPageURL":url}

				for child in xml_result.ItemAttributes.getchildren():
					name = child.tag.split("}")[-1]
					value = child.text
					result[name] = value
				results.append(result)
			except:
				pass
	return results

def empty_album(info):
	search_url = SEARCH_PAGE + "&field-keywords=%s"%(urllib.quote(squash_str(info['name'])))
	result = {"name":"Amazon",
	          "icon":"static/amazon.png",
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
			result['found'] = found['DetailPageURL']
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_artist_album_name(info):
	if not API:
		return None
	artist = primary_name(info['composers'][0]['names'])
	title = info['name']
	try:
		results = parse_results(API.item_search('Music', limit=1, ResponseGroup='ItemAttributes', Artist=squash_str(artist), Title=squash_str(title)))
	except amazonproduct.errors.TooManyRequests:
		time.sleep(2)
		return None
	except amazonproduct.errors.NoExactMatchesFound:
		return None
	found = find_best_match(squash_str(title), results,
	   threshold=0.5, key=lambda x:squash_str(x['Title']))
	return found

def search_album_name(info):
	if not API:
		return None
	title = info['name']
	try:
		results = parse_results(API.item_search('Music', limit=1, ResponseGroup='ItemAttributes', Title=squash_str(title)))
	except amazonproduct.errors.TooManyRequests:
		time.sleep(2)
		return None
	except amazonproduct.errors.NoExactMatchesFound:
		return None
	found = find_best_match(squash_str(title), results,
	   threshold=0.5, key=lambda x:squash_str(x['Title']))
	return found

def empty_artist(info):
	search_url = SEARCH_PAGE + "&field-artist=%s"%(urllib.quote(squash_str(info['name'])),)
	result = {"name":"Amazon",
	          "icon":"static/amazon.png",
	          "search": search_url
	         }
	return result
def search_artist(info):
	result = empty_artist(info)
	try:
		found = search_artist_name(info['name'])
		if found:
			result['surity'] = 'results'
			result['found'] = result['search']
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_artist_name(name):
	if not API:
		return None
	try:
		results = parse_results(API.item_search('Music', limit=1, ResponseGroup='ItemAttributes', Artist=squash_str(name)))
	except amazonproduct.errors.TooManyRequests:
		time.sleep(2)
	except amazonproduct.errors.NoExactMatchesFound:
		return None
	def get_artist(item):
		if 'Artist' in item:
			return item['Artist']
		if 'Creator' in item:
			return item['Creator']
	found = find_best_match(squash_str(name), results,
	   threshold=0.7, key=lambda x:squash_str(get_artist(x)))
	return found

