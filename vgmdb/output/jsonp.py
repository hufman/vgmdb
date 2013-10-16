from __future__ import absolute_import

mimetypes = ['application/javascript']
name = 'jsonp'

class outputter(object):
	content_type = 'application/javascript; charset=utf-8'

	def __init__(self, config):
		self._config = config
		import json
		self._json = json
		try:
			import simplejson as json
			self._json = json
		except:
			pass

	def __call__(self, type, data, filterkey=None):
		callback = self._config.jsonp_callback
		return '%s(%s);'%(callback, self._json.dumps(data, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False))
