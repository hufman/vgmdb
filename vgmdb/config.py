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
DATA_BACKGROUND = False

# load cloud settings for defaults
if 'AMQP_PORT_5672_TCP' in os.environ or 'AMQP_HOST' in os.environ:
	amqp_user = os.environ.get('AMQP_USER', 'guest')
	amqp_pass = os.environ.get('AMQP_PASSWORD', 'guest')
	amqp_ip = os.environ.get('AMQP_HOST', '127.0.0.1')
	amqp_ip = os.environ.get('AMQP_PORT_5672_TCP_ADDR', amqp_ip)
	amqp_port = os.environ.get('AMQP_PORT', '5672')
	amqp_port = os.environ.get('AMQP_PORT_5672_TCP_PORT', amqp_port)
	amqp_vhost = os.environ.get('AMQP_VHOST', '/')
	CELERY_BROKER = 'amqp://%s:%s@%s:%s/%s' % (
		amqp_user, amqp_pass, amqp_ip, amqp_port, amqp_vhost
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
