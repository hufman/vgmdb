import os
import os.path
import logging
import glob
import unittest
import json
import jsonschema
import vgmdb.request
import vgmdb.parsers

base = os.path.dirname(__file__)
project = os.path.dirname(base)

def get_draft4_validator(schema_absolute_path):
	with open(schema_absolute_path) as schema_file:
		schema = json.load(schema_file)
	resolver = jsonschema.RefResolver("file://" + schema_absolute_path, schema)
	return jsonschema.Draft4Validator(schema, resolver=resolver)

class TestJsonSchemaMeta(type):
	def __new__(mcs, name, bases, dict):
		""" The metaclass client class must define:
			schema_path - a path to the schema to validate against
			glob_path - a pattern of html files
			parser_module - a module to parse each file
		"""
		def gen_test(schema, filename, parser):
			def test(self):
				logging.info('Validating json schema %s with file %s' % (schema, filename))
				code = file(filename, 'r').read()
				data = parser.parse_page(code)
				data['link'] = 'unknown/1'
				data['vgmdb_link'] = 'http://vgmdb.net/unknown/1'
				vgmdb.request._calculate_ttl(data)
				validator = get_draft4_validator(schema)
				validator.validate(data)
			return test

		files = glob.glob(dict['glob_path'])
		for filename in files:
			test_name = "test_%s" % (os.path.basename(filename),)
			test = gen_test(dict['schema_path'], filename, dict['parser_module'])
			test.__name__ = test_name
			dict[test_name] = test
		return type.__new__(mcs, name, bases, dict)

class TestJsonAlbums(unittest.TestCase):
	__metaclass__ = TestJsonSchemaMeta
	schema_path = os.path.join(project, "schema", "album.json")
	glob_path = "%s/album_*html" % base
	import vgmdb.parsers.album as parser_module

class TestJsonArtists(unittest.TestCase):
	__metaclass__ = TestJsonSchemaMeta
	schema_path = os.path.join(project, "schema", "artist.json")
	glob_path = "%s/artist_*html" % base
	import vgmdb.parsers.artist as parser_module

class TestJsonOrgs(unittest.TestCase):
	__metaclass__ = TestJsonSchemaMeta
	schema_path = os.path.join(project, "schema", "org.json")
	glob_path = "%s/org_*html" % base
	import vgmdb.parsers.org as parser_module

class TestJsonEvents(unittest.TestCase):
	__metaclass__ = TestJsonSchemaMeta
	schema_path = os.path.join(project, "schema", "event.json")
	glob_path = "%s/event_*html" % base
	import vgmdb.parsers.event as parser_module

class TestJsonProducts(unittest.TestCase):
	__metaclass__ = TestJsonSchemaMeta
	schema_path = os.path.join(project, "schema", "product.json")
	glob_path = "%s/product_*html" % base
	import vgmdb.parsers.product as parser_module

class TestJsonSearch(unittest.TestCase):
	__metaclass__ = TestJsonSchemaMeta
	schema_path = os.path.join(project, "schema", "search.json")
	glob_path = "%s/search*html" % base
	import vgmdb.parsers.search as parser_module

class TestJsonAlbumList(unittest.TestCase):
	__metaclass__ = TestJsonSchemaMeta
	schema_path = os.path.join(project, "schema", "albumlist.json")
	glob_path = "%s/albumlist.html" % base
	import vgmdb.parsers.albumlist as parser_module

class TestJsonArtistList(unittest.TestCase):
	__metaclass__ = TestJsonSchemaMeta
	schema_path = os.path.join(project, "schema", "artistlist.json")
	glob_path = "%s/artistlist.html" % base
	import vgmdb.parsers.artistlist as parser_module

class TestJsonOrgList(unittest.TestCase):
	__metaclass__ = TestJsonSchemaMeta
	schema_path = os.path.join(project, "schema", "orglist.json")
	glob_path = "%s/orglist.html" % base
	import vgmdb.parsers.orglist as parser_module

if __name__ == '__main__':
	unittest.main()
