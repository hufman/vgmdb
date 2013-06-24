from __future__ import absolute_import

mimetypes = ['application/json']
name = 'json'

class outputter(object):
	content_type = 'application/json; charset=utf-8'

	def __init__(self):
		import json
		self._json = json
		try:
			import simplejson as json
			self._json = json
		except:
			pass

	def __call__(self, type, data, filterkey=None):
		return self._json.dumps(data, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
