import os

BASE_URL = 'http://hufman.dyndns.org/vgmdb/'
AUTO_RELOAD = True

if os.environ.has_key('GAE_BASEURL'):
	BASE_URL = os.environ['GAE_BASEURL']
