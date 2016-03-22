import logging
logger = logging.getLogger(__name__)

from .. import config
from .. import cache
from .. import celery
celery = celery.celery

from . import amazon as real_amazon
from . import cdjapan as real_cdjapan
from . import discogs as real_discogs
from . import itunes as real_itunes
from . import spotify as real_spotify

def do_search(type, id, sellername):
	seller = globals()['real_'+sellername]
	info = cache.get("vgmdb/%s/%s"%(type,id))
	if info:
		cache_key = "vgmdb/%s/%s/sellers/vgmdb.sellers.%s"%(type,id,sellername)
		prev = cache.get(cache_key)
		if prev:
			return
		search = getattr(seller, 'search_%s'%(type,))
		result = search(info)
		if result:
			cache.set(cache_key, result)
	else:
		logger.warning("Failed to fetch data for vgmdb/%s/%s"%(type,id))
	return True

@celery.task(default_retry_delay=5)
def amazon(type, id):
	return do_search(type, id, 'amazon')

@celery.task(default_retry_delay=5)
def cdjapan(type, id):
	return do_search(type, id, 'cdjapan')

@celery.task(default_retry_delay=5)
def discogs(type, id):
	return do_search(type, id, 'discogs')

@celery.task(default_retry_delay=5)
def itunes(type, id):
	return do_search(type, id, 'itunes')

@celery.task(default_retry_delay=5)
def spotify(type, id):
	return do_search(type, id, 'spotify')
