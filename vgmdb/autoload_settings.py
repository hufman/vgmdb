import os

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

# try to load some keys from environment
env_keys = [
  'BASE_URL', 'CELERY_BROKER', 'CELERY_RESULT_BACKEND', 'CELERY_CACHE_BACKEND',
  'AMAZON_ACCESS_KEY_ID', 'AMAZON_SECRET_ACCESS_KEY', 'AMAZON_ASSOCIATE_TAG',
  'ITUNES_AFFILIATE_ID', 'ITUNES_TD_PROGRAM_ID', 'ITUNES_TD_WEBSITE_ID'
]
for key in env_keys:
	if key in os.environ:
		globals()[key] = os.environ[key]

if os.environ.has_key('GAE_BASEURL'):
	BASE_URL = os.environ['GAE_BASEURL']
