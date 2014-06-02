import logging
import cdjapan_parse as parser
from ._utils import squash_str,find_best_match

class NullHandler(logging.Handler):
	def emit(self, record):
		pass
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

def empty_album(info):
	result = {"name":"CDJapan",
	          "icon":"static/cdjapan.gif",
	          "search": parser.get_search_url(squash_str(info['name']))
	         }
	return result

def search_album(info):
	result = empty_album(info)
	try:
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
			result['found'] = found['link']
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_album_catalog(catalog):
	catalog = catalog.split('~')[0]
	results = parser.search_products(squash_str(catalog))
	found = find_best_match(squash_str(catalog), results,
	   threshold=0.9, key=lambda x:squash_str(x['product_key']))
	return found

def search_artist_album_name(info):
	artist = info['composers'][0]['names']['en']
	title = info['name']
	results = parser.search_products(squash_str(artist+" "+title))
	found = find_best_match(squash_str(title), results,
	   threshold=0.5, key=lambda x:squash_str(x['title']))
	return found

def search_album_name(info):
	title = info['name']
	results = parser.search_products(squash_str(title))
	found = find_best_match(squash_str(title), results,
	   threshold=0.5, key=lambda x:squash_str(x['title']))
	return found

def empty_artist(info):
	result = {"name":"CDJapan",
	          "icon":"static/cdjapan.gif",
	          "search": parser.get_search_url(squash_str(info['name']))
	}
	return result

def search_artist(info):
	result = empty_artist(info)
	try:
		found = search_artist_name(info['name'])
		if found:
			result['surity'] = 'results'
			result['found'] = parser.get_search_url(info['name'])
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_artist_name(name):
	results = parser.search_artists(squash_str(name))
	found = find_best_match(squash_str(name), results,
	   threshold=0.7, key=lambda x:squash_str(x['name']))
	return found

def empty_series(info):
	result = {"name":"CDJapan",
	          "icon":"static/cdjapan.gif",
	          "search": parser.get_search_url(squash_str(info['name']))
	}
	return result

def search_series(info):
	result = empty_series(info)
	try:
		found = search_series_name(info['name'])
		if found:
			result['surity'] = 'results'
			result['found'] = parser.get_search_url(info['name'])
	except:
		import traceback
		logger.warning(traceback.format_exc())
		result = None
	return result

def search_series_name(name):
	results = parser.search_series(squash_str(name))
	found = find_best_match(squash_str(name), results,
	   threshold=0.7, key=lambda x:squash_str(x['name']))
	return found


if __name__ == '__main__':
	print(search_artist_name('nobuo uematsu'))
	print(search_series_name('final fantasy'))
