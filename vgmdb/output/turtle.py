import sys
import vgmdb.config

mimetypes = ['application/x-turtle', 'text/turtle']
name = 'turtle'

class outputter(object):
	content_type = 'text/turtle; charset=utf-8'

	def __init__(self):
		if vgmdb.config.AUTO_RELOAD and \
                   'vgmdb.output.rdf' in sys.modules.keys():
			reload(sys.modules['vgmdb.output.rdf'])
		import rdf
		self._rdf = rdf

	def __call__(self, type, data):
		return self._rdf.generate(vgmdb.config, type, data).serialize(format="turtle")
