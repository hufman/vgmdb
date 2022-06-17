from .settings import *

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
	if settings.BASE_URL == '//vgmdb.info/':	# setting hasn't been configured
		if request.get_header('Host'):
			settings.BASE_URL = '//%s/'%(request.get_header('Host'),)
		if request.get_header('base_url'):
			settings.BASE_URL = request.get_header('base_url')
		if request.get_header('base-url'):
			settings.BASE_URL = request.get_header('base-url')
	if request.query.get('callback'):
		settings.jsonp_callback = request.query.get('callback')
	return settings
