# -*- coding: UTF-8 -*-
import os
import sys
import datetime
import isodate
import unittest
import rdflib
from rdflib import Graph, URIRef

from vgmdb import output
from vgmdb import config

base = os.path.dirname(__file__)

namespaces = {
	"dcterms": "http://purl.org/dc/terms/",
	"schema": "http://schema.org/",
	"foaf": "http://xmlns.com/foaf/0.1/",
	"bio": "http://purl.org/vocab/bio/0.1/",
	"xsd": "http://www.w3.org/2001/XMLSchema#",
	"mo": "http://purl.org/ontology/mo/",
	"event": "http://purl.org/NET/c4dm/event.owl#",
	"tl": "http://purl.org/NET/c4dm/timeline.owl#"
}

class TestRDF(unittest.TestCase):
	data_parser = lambda self,x: x/0

	outputter_type = ''	# set to album or whatever
	def setUp(self):
		pass

	def assertGreater(self, a, b, msg=None):
		self.assertTrue(a > b, msg)

	def assertGreaterEqual(self, a, b, msg=None):
		self.assertTrue(a >= b, msg)

	def read_data(self, filename):
		with open(os.path.join(base, filename), 'r', errors='ignore') as data:
			return data.read()

	def load_data(self, filename, output_format, parse_format, filterkey=None, **parse_kwargs):
		code = self.read_data(filename)
		data = self.data_parser(code)
		outputter = output.get_outputter(config, output_format, None)
		output_data = outputter(self.outputter_type, data, filterkey=filterkey)
		with open('/tmp/rdftest.%s.%s'%(self.outputter_type,output_format),'w') as output_file:
			output_file.write(output_data)
		graph = Graph()
		graph.parse(data=output_data, format=parse_format, **parse_kwargs)
		with open('/tmp/rdftest.parsed.%s.%s'%(self.outputter_type,output_format),'w') as output_file:
			output_file.write(graph.serialize(format='turtle'))
		return graph
	def load_rdfa_data(self, filename, filterkey=None):
		return self.load_data(filename, 'html', 'rdfa', filterkey=filterkey, media_type="text/html")
	def load_rdf_data(self, filename):
		return self.load_data(filename, 'rdf', 'xml')
	def run_tests(self, graph, test_count_results, test_first_result):
		def replace_base(query):
			if len(config.BASE_URL) > 0 and config.BASE_URL[-1] == '/':
				query = query.replace('@base/', config.BASE_URL)
			query = query.replace('@base', config.BASE_URL)
			return query
		for query, count in test_count_results.items():
			query = replace_base(query)
			try:
				res = graph.query(query, initNs=namespaces)
			except:
				self.fail("Invalid query: %s\n%s"%(query,sys.exc_info()[1]))
				raise
			self.assertEqual(len(res), count, "Results for %s: %s vs %s"%(query, len(res), count))
		for query, answer in test_first_result.items():
			query = replace_base(query)
			if isinstance(answer, str):
				answer = replace_base(answer)
			try:
				res = graph.query(query, initNs=namespaces)
			except:
				self.fail("Invalid query: %s\n%s"%(query,sys.exc_info()[1]))
				raise
			self.assertGreaterEqual(len(res), 1, "Didn't find an answer for %s"%query)
			for row in res:
				if row[0] == None:
					value = None
				elif isinstance(row[0], URIRef):
					value = "<%s>"%row[0]
				else:
					value = row[0].value
				if row[0] != None and value == None:
					value = str(row[0])
				if isinstance(value, datetime.timedelta):
					answer = isodate.isoduration.parse_duration(answer)
				self.assertEqual(value, answer, "Result for %s: '%s'(%s) vs '%s'(%s)"%(query, value, type(value), answer, type(answer)))
				break

