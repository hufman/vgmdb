import urllib
import urlparse
import json
import logging
import time

from .. import config
from ._utils import squash_str,find_best_match, primary_name
import paapi5_python_sdk as paapi5

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
	API = paapi5.api.default_api.DefaultApi(
		access_key = config.AMAZON_ACCESS_KEY_ID,
		secret_key = config.AMAZON_SECRET_ACCESS_KEY,
		host = "webservices.amazon.com",
		region = "us-east-1"
	)
else:
	API = None

def run_search(keywords, artist=None):
	search_items_resource = [paapi5.search_items_resource.SearchItemsResource.ITEMINFO_TITLE]
	request = paapi5.search_items_request.SearchItemsRequest(
		partner_tag = config.AMAZON_ASSOCIATE_TAG,
		partner_type = paapi5.partner_type.PartnerType.ASSOCIATES,
		keywords = keywords,
		search_index = "Music",
		item_count = 5,
		resources = search_items_resource,
		artist = artist
	)
	try:
		response = API.search_items(request)
	except paapi5.rest.ApiException:
		time.sleep(2)
		return None
	if response.search_result is None:
		return None
	return response.search_result.items

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
			result['found'] = found.detail_page_url
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_artist_album_name(info):
	if not API:
		return None
	if len(info['composers']) < 1:
		return None
	artist = primary_name(info['composers'][0]['names'])
	title = info['name']
	results = run_search(keywords=squash_str(artist) + " " + squash_str(title),
	                     artist=squash_str(artist))
	if results is None:
		return None
	found = find_best_match(squash_str(title), results,
	   threshold=0.5, key=lambda x:squash_str(x.item_info.title.display_value))
	return found

def search_album_name(info):
	if not API:
		return None
	title = info['name']
	results = run_search(keywords=squash_str(title))
	if results is None:
		return None
	found = find_best_match(squash_str(title), results,
	   threshold=0.5, key=lambda x:squash_str(x.item_info.title.display_value))
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
			# leave the search link in place
			result['found'] = result['search']
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_artist_name(name):
	if not API:
		return None
	results = run_search(keywords=squash_str(name), artist=squash_str(name))
	if results is not None:
		return results[0]
	results = run_search(keywords=squash_str(name))
	if results is not None:
		return results[0]

