# base settings
BASE_URL = 'http://vgmdb.info/'
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

try:
	from .autoload_settings import *
except:
	pass
try:
	from .local_settings import *
except:
	pass
