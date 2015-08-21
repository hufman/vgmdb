import os
import logging

logger = logging.getLogger(__name__)

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
	logger.info("Docker AMQP link detected, guessing %s" % (CELERY_BROKER,))

# detect docker links
if 'MEMCACHED_PORT_11211_TCP' in os.environ:
	MEMCACHE_SERVERS = ["%s:%s" % (
	    os.environ['MEMCACHED_PORT_11211_TCP_ADDR'],
	    os.environ['MEMCACHED_PORT_11211_TCP_PORT']
	)]
	logger.info("Docker Memcache link detected, guessing %s" % (MEMCACHE_SERVERS,))

# detect openshift
if 'OPENSHIFT_MEMCACHED_HOST' in os.environ and \
   'OPENSHIFT_MEMCACHED_PORT' in os.environ:
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
if os.environ.has_key('BACKGROUND_DATA'):
	if os.environ['BACKGROUND_DATA'].lower() in ['yes', 'true']:
		BACKGROUND_DATA = True
	if os.environ['BACKGROUND_DATA'].lower() in ['no', 'false']:
		BACKGROUND_DATA = False
if os.environ.has_key('GAE_BASEURL'):
	BASE_URL = os.environ['GAE_BASEURL']
	logger.info("Loading BASE_URL from GAE: %s" % (BASE_URL,))
if os.environ.has_key('MEMCACHE_SERVER'):
	MEMCACHE_SERVERS = [os.environ['MEMCACHE_SERVER']]
	logger.info("Loading MEMCACHE_SERVER from environ: %s" % (MEMCACHE_SERVERS[0],))
if os.environ.has_key('MEMCACHE_SERVERS'):
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

# guess the final celery cache string based on the discovered MEMCACHE_SERVERS
if 'MEMCACHE_SERVERS' in globals():
	CELERY_CACHE_BACKEND = 'memcached://%s/' % (';'.join(MEMCACHE_SERVERS), )
	logger.info("Guessing Celery cache backend at: %s" % (CELERY_CACHE_BACKEND,))

# try to load some keys from environment
env_keys = [
  'BASE_URL',
  'CELERY_BROKER', 'CELERY_RESULT_BACKEND', 'CELERY_CACHE_BACKEND',
  'AMAZON_ACCESS_KEY_ID', 'AMAZON_SECRET_ACCESS_KEY', 'AMAZON_ASSOCIATE_TAG',
  'ITUNES_AFFILIATE_ID', 'ITUNES_TD_PROGRAM_ID', 'ITUNES_TD_WEBSITE_ID',
  'DISCOGS_KEY', 'DISCOGS_SECRET', 'RDIO_KEY', 'RDIO_SECRET'
]
for key in env_keys:
	if key in os.environ:
		globals()[key] = os.environ[key]
		logger.info("Loading %s from environ: %s" % (key, os.environ[key]))
