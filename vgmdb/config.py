import os
try:
	from .config_private import *
except:
	pass
private_keys = [
  'AMAZON_ACCESS_KEY_ID', 'AMAZON_SECRET_ACCESS_KEY', 'AMAZON_ASSOCIATE_TAG',
  'ITUNES_AFFILIATE_ID', 'ITUNES_TD_PROGRAM_ID', 'ITUNES_TD_WEBSITE_ID'
]
for key in private_keys:
	if key in os.environ:
		globals()[key] = os.environ[key]

BASE_URL = 'http://vgmdb.info/'
AUTO_RELOAD = False
CELERY_BROKER = 'amqp://guest@127.0.0.1//'
CELERY_RESULT_BACKEND = 'cache'
CELERY_CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CELERY_PING = True

# load cloud settings for defaults
if 'AMQP_PORT_5672_TCP' in os.environ:
	CELERY_BROKER = 'amqp://guest@%s//' % (
	    os.environ['AMQP_PORT_5672_TCP_ADDR']
	)
if 'MEMCACHED_PORT_11211_TCP' in os.environ:
	CELERY_CACHE_BACKEND = 'memcached://%s:%s/' % (
	    os.environ['MEMCACHED_PORT_11211_TCP_ADDR'],
	    os.environ['MEMCACHED_PORT_11211_TCP_PORT']
	)

env_keys = [
  'BASE_URL', 'CELERY_BROKER', 'CELERY_RESULT_BACKEND', 'CELERY_CACHE_BACKEND'
]
for key in env_keys:
	if key in os.environ:
		globals()[key] = os.environ[key]


if os.environ.has_key('GAE_BASEURL'):
	BASE_URL = os.environ['GAE_BASEURL']

class Settings(object):
	pass

def get_defaults():
	settings = Settings()
	settings.BASE_URL = BASE_URL
	settings.AUTO_RELOAD = AUTO_RELOAD
	settings.jsonp_callback = 'jsonp_callback'
	return settings

def for_request(request):
	settings = get_defaults()
	if request.get_header('Host'):
		settings.BASE_URL = 'http://%s/'%(request.get_header('Host'),)
	if request.get_header('base_url'):
		settings.BASE_URL = request.get_header('base_url')
	if request.get_header('base-url'):
		settings.BASE_URL = request.get_header('base-url')
	if request.query.get('callback'):
		settings.jsonp_callback = request.query.get('callback')
	return settings
