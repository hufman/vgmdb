import urllib
import urlparse
import json


BASE_URL = 'http://www.cdjapan.co.jp/products?q=%s&term.media_format=cd'
API_SEARCH_ARTIST = 'http://www.cdjapan.co.jp/api/products/facet/person/json?q=%s&term.media_format=cd&facet_limit=5'
API_SEARCH_SERIES = 'http://www.cdjapan.co.jp/api/products/facet/series/json?q=%s&term.media_format=cd&facet_limit=5'
API_SEARCH_PRODUCTS = 'http://www.cdjapan.co.jp/api/products/json?q=%s'
ARTIST_INFO = 'http://www.cdjapan.co.jp/person/%s'
SERIES_INFO = 'http://www.cdjapan.co.jp/series/%s'
PRODUCT_INFO = 'http://www.cdjapan.co.jp/product/%s'

def get_search_url(query):
	return BASE_URL%(urllib.quote(query),)

def search_artists(query):
	link = API_SEARCH_ARTIST % (urllib.quote(query),)
	return parse_facets(ARTIST_INFO, fetch(link))

def search_series(query):
	link = API_SEARCH_SERIES % (urllib.quote(query),)
	return parse_facets(SERIES_INFO, fetch(link))

def search_products(query):
	link = API_SEARCH_PRODUCTS % (urllib.quote(query),)
	return parse_records(fetch(link))

def fetch(link):
	return json.load(urllib.urlopen(link))

def parse_facets(info_link, data):
	if data:
		return [{'link': info_link % (f['id'],),
		         'name': f['ename'],
		         'jname': f['name']}
		        for f in data['facet']]
		return data['facet'][0]

def parse_records(data):
	if data:
		return [{'link': PRODUCT_INFO % (p['prodkey'],),
		         'title': p['title'],
		         'product_key': p['prodkey']}
		        for p in data['record']]


if __name__ == "__main__":
	import pprint
	pprint.pprint(search_artists('nobuo uematsu'))
	pprint.pprint(search_series('final fantasy'))
	pprint.pprint(search_products('fithos lusec'))
