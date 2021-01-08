from __future__ import absolute_import

mimetypes = ['application/json+singleline']
name = 'jsonl'

class outputter(object):
	content_type = 'application/json; charset=utf-8'

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
		return self._json.dumps(data, sort_keys=True, ensure_ascii=False)
