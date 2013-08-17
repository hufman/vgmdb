from .. import album
from .. import artist
from .. import cache

from . import discogs

search_modules = [discogs]

def search(type, id):
	"""
	itemid should be something like album/79 or artist/77
	"""
	if type in ['album','artist']:
		module = globals()[type]
		prevdata = cache.get("%s/%s"%(type,id))
		if not prevdata:
			fetch_page = getattr(module, "fetch_page")
			parse_page = getattr(module, "parse_page")
			page = fetch_page(id)
			info = parse_page(page)
			cache.set("%s/%s"%(type,id), info)
		else:
			info = prevdata
		return search_all(type,info)
	else:
		return []

def search_all(type,info):
	results = []
	for module in search_modules:
		search = getattr(module, "search_%s"%(type,), None)
		if search:
			ret = search(info)
			if ret:
				results.append(ret)
	return results
