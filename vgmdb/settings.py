# base settings
BASE_URL = '//vgmdb.info/'
AUTO_RELOAD = False
MEMCACHE_SERVERS = ['127.0.0.1:11211']
MEMCACHE_ARGS = {}
CELERY_BROKER = 'amqp://guest@127.0.0.1//'
CELERY_RESULT_BACKEND = 'cache'
CELERY_CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CELERY_PING = True
DATA_BACKGROUND = False

# seller backend settings
AMAZON_ACCESS_KEY_ID = None
AMAZON_SECRET_ACCESS_KEY = None
AMAZON_ASSOCIATE_TAG = None
ITUNES_AFFILIATE_ID = None
ITUNES_TD_PROGRAM_ID = None
ITUNES_TD_WEBSITE_ID = None
DISCOGS_KEY = None
DISCOGS_SECRET = None
RDIO_KEY = None
RDIO_SECRET = None
SPOTIFY_ID = None
SPOTIFY_SECRET = None

import logging
logger = logging.getLogger(__name__)
try:
	from .autoload_settings import *
except Exception as e:
	logging.warning("Could not load autoload_settings: %s" % (e,))
try:
	from .local_settings import *
except Exception as e:
	logging.warning("Could not load local_settings: %s" % (e,))
