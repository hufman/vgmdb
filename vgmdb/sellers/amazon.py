import urllib
import urlparse
import json
from .. import config
from ._utils import squash_str,find_best_match
from amazonproduct import api, errors

SEARCH_PAGE = 'http://www.amazon.com/s/?_encoding=UTF8&url=search-alias%%3Dpopular&SubscriptionId=%s&AssociateTag=%s&linkCode=ur2&tag=%s'%(config.AMAZON_ACCESS_KEY_ID,config.AMAZON_ASSOCIATE_TAG,config.AMAZON_ASSOCIATE_TAG)
API = api.API(config.AMAZON_ACCESS_KEY_ID, config.AMAZON_SECRET_ACCESS_KEY, 'us', config.AMAZON_ASSOCIATE_TAG)

def parse_results(roots):
	results = []
	for root in roots:
		if root.Items.Request.ItemSearchRequest.ItemPage.pyval != 1:
			break
		nspace = root.nsmap.get(None, '')
		xml_results = root.xpath('//aws:Items/aws:Item',
		                         namespaces={'aws':nspace})
		for xml_result in xml_results:
			try:
				result = {"DetailPageURL":xml_result.DetailPageURL.text}
				for child in xml_result.ItemAttributes.getchildren():
					name = child.tag.split("}")[-1]
					value = child.text
					result[name] = value
				results.append(result)
			except:
				pass
	return results

def search_album(info):
	search_url = SEARCH_PAGE + "&field-artist=%s&field-title=%s"%(urllib.quote(squash_str(info['composers'][0]['names']['en'])), urllib.quote(squash_str(info['name'])))
	result = {"name":"Amazon",
	          "icon":"https://upload.wikimedia.org/wikipedia/commons/b/b4/Amazon-icon.png",
	          "search": search_url
	         }
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
	return result

def search_artist_album_name(info):
	artist = info['composers'][0]['names']['en']
	title = info['name']
	try:
		results = parse_results(API.item_search('Music', ResponseGroup='ItemAttributes', Artist=squash_str(artist), Title=squash_str(title)))
	except errors.NoExactMatchesFound:
		return None
	found = find_best_match(squash_str(title), results,
	   threshold=0.5, key=lambda x:squash_str(x['Title']))
	return found

def search_album_name(info):
	title = info['name']
	try:
		results = parse_results(API.item_search('Music', ResponseGroup='ItemAttributes', Title=squash_str(title)))
	except errors.NoExactMatchesFound:
		return None
	found = find_best_match(squash_str(title), results,
	   threshold=0.6, key=lambda x:squash_str(x['Title']))
	return found

def search_artist(info):
	search_url = SEARCH_PAGE + "&field-artist=%s"%(urllib.quote(squash_str(info['name'])),)
	result = {"name":"Amazon",
	          "icon":"https://upload.wikimedia.org/wikipedia/commons/b/b4/Amazon-icon.png",
	          "search": search_url
	         }
	found = search_artist_name(info['name'])
	if found:
		result['surity'] = 'results'
		result['found'] = search_url
	return result

def search_artist_name(name):
	try:
		results = parse_results(API.item_search('Music', ResponseGroup='ItemAttributes', Artist=squash_str(name)))
	except errors.NoExactMatchesFound:
		return None
	def get_artist(item):
		if 'Artist' in item:
			return item['Artist']
		if 'Creator' in item:
			return item['Creator']
	found = find_best_match(squash_str(name), results,
	   threshold=0.5, key=lambda x:squash_str(get_artist(x)))
	return found

