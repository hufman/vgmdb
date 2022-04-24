import os
import logging

logger = logging.getLogger(__name__)

# load cloud settings for defaults
if os.environ.get('AMQP_PORT_5672_TCP') or os.environ.get('AMQP_HOST'):
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
	logger.info("Docker AMQP link detected, guessing %s" % (CELERY_BROKER,))

# detect docker links
if os.environ.get('MEMCACHED_PORT_11211_TCP'):
	MEMCACHE_SERVERS = ["%s:%s" % (
	    os.environ['MEMCACHED_PORT_11211_TCP_ADDR'],
	    os.environ['MEMCACHED_PORT_11211_TCP_PORT']
	)]
	logger.info("Docker Memcache link detected, guessing %s" % (MEMCACHE_SERVERS,))

# detect docker redis
if os.environ.get('REDIS_PORT_6379_TCP_PORT'):
	REDIS_HOST = os.environ.get('REDIS_PORT_6379_TCP_ADDR', '127.0.0.1')
	logger.info("Docker Redis link detected, guessing %s" % (REDIS_HOST,))

# detect openshift
if os.environ.get('OPENSHIFT_MEMCACHED_HOST') and \
   os.environ.get('OPENSHIFT_MEMCACHED_PORT'):
	MEMCACHE_SERVERS = ["%s:%s" % (
	    os.environ['OPENSHIFT_MEMCACHED_HOST'],
	    os.environ['OPENSHIFT_MEMCACHED_PORT']
	)]
	MEMCACHE_ARGS = {
	  'username': os.environ['OPENSHIFT_MEMCACHED_USERNAME'],
	  'password': os.environ['OPENSHIFT_MEMCACHED_PASSWORD']
	}
	logger.info("Openshift Memcache link detected, guessing %s" % (MEMCACHE_SERVERS,))

# some fancy processing
if os.environ.get('DATA_BACKGROUND'):
	if os.environ['DATA_BACKGROUND'].lower() in ['yes', 'true']:
		DATA_BACKGROUND = True
		logger.info("Loading DATA_BACKGROUND from environ: %s" % (DATA_BACKGROUND,))
	if os.environ['DATA_BACKGROUND'].lower() in ['no', 'false']:
		DATA_BACKGROUND = False
		logger.info("Loading DATA_BACKGROUND from environ: %s" % (DATA_BACKGROUND,))
if os.environ.get('GAE_BASEURL'):
	BASE_URL = os.environ['GAE_BASEURL']
	logger.info("Loading BASE_URL from GAE: %s" % (BASE_URL,))
if os.environ.get('MEMCACHE_SERVER'):
	MEMCACHE_SERVERS = [os.environ['MEMCACHE_SERVER']]
	logger.info("Loading MEMCACHE_SERVER from environ: %s" % (MEMCACHE_SERVERS[0],))
if os.environ.get('MEMCACHE_SERVERS'):
	MEMCACHE_SERVERS = os.environ['MEMCACHE_SERVERS'].split(',')
	MEMCACHE_SERVERS = [s.strip() for s in MEMCACHE_SERVERS]
	logger.info("Loading MEMCACHE_SERVERS from environ: %s" % (MEMCACHE_SERVERS,))

# make sure the memcache servers have ports
if 'MEMCACHE_SERVERS' in globals():
	def add_port(host, port):
		if ':' not in host:
			return "%s:%s" % (host, port)
		return host
	MEMCACHE_SERVERS = [add_port(s, '11211') for s in MEMCACHE_SERVERS]

# try to load some keys from environment
env_keys = [
  'BASE_URL',
  'CELERY_BROKER', 'CELERY_RESULT_BACKEND', 'CELERY_CACHE_BACKEND',
  'REDIS_HOST',
  'AMAZON_ACCESS_KEY_ID', 'AMAZON_SECRET_ACCESS_KEY', 'AMAZON_ASSOCIATE_TAG',
  'ITUNES_AFFILIATE_ID', 'ITUNES_TD_PROGRAM_ID', 'ITUNES_TD_WEBSITE_ID',
  'DISCOGS_KEY', 'DISCOGS_SECRET', 'RDIO_KEY', 'RDIO_SECRET',
  'SPOTIFY_ID', 'SPOTIFY_SECRET'
]
for key in env_keys:
	if os.environ.get(key):
		globals()[key] = os.environ[key]
		logger.info("Loading %s from environ: %s" % (key, os.environ[key]))

# now autoload up some Celery configs
if 'CELERY_BROKER' not in globals() and 'REDIS_HOST' in globals():
	CELERY_BROKER = 'redis://%s:6379/0' % (REDIS_HOST,)

if 'CELERY_RESULT_BACKEND' not in globals() and 'REDIS_HOST' in globals():
	CELERY_RESULT_BACKEND = 'redis://%s:6379/0' % (REDIS_HOST,)

# guess the final celery cache string based on the discovered MEMCACHE_SERVERS
if 'CELERY_CACHE_BACKEND' not in globals() and 'MEMCACHE_SERVERS' in globals():
	CELERY_CACHE_BACKEND = 'memcached://%s/' % (';'.join(MEMCACHE_SERVERS), )
	logger.info("Guessing Celery cache backend at: %s" % (CELERY_CACHE_BACKEND,))
