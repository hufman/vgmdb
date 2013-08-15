import sys

mimetypes = ['application/x-turtle', 'text/turtle']
name = 'turtle'

class outputter(object):
	content_type = 'text/turtle; charset=utf-8'

	def __init__(self, config):
		self._config = config
		if self._config.AUTO_RELOAD and \
                   'vgmdb.output.rdf' in sys.modules.keys():
			reload(sys.modules['vgmdb.output.rdf'])
		import rdf
		self._rdf = rdf

	def __call__(self, type, data, filterkey=None):
		return self._rdf.generate(self._config, type, data).serialize(format="turtle", base=vgmdb.config.BASE_URL)
