# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb.parsers import org

base = os.path.dirname(__file__)

class TestOrgRDF(TestRDF):
	data_parser = lambda self,x: org.parse_page(x)
	outputter_type = 'org'
	def setUp(self):
		pass

	def run_dogear_tests(self, graph):
		test_count_results = {
			"select ?type where { <@base#subject> rdf:type foaf:Organization . }" : 1,
			"select ?type where { <@base#subject> rdf:type schema:Organization . }" : 1,
			"select ?person where { <@base#subject> schema:member ?person . }" : 2,
			"select ?person where { ?person schema:memberOf <@base#subject> . }" : 2,
			"select ?person where { ?person foaf:member <@base#subject> . }" : 2,
			"select ?name where { ?person foaf:member <@base#subject> . ?person foaf:name \"Miyu\"@en . }" : 1,
			"select ?member where { <@base#subject> schema:member ?member . }" : 2,
			"select ?member where { ?member schema:memberOf <@base#subject> . }" : 2,
			"select ?name where { <@base#subject> schema:member ?member . ?member foaf:name ?name . filter(lang(?name)='en') }" : 2,
			"select ?album where { <@base#subject> mo:published ?album . }" : 28,
			"select ?album where { ?album mo:publisher <@base#subject> . }" : 28,
			"select ?page where { <@base#subject> foaf:page ?page . }" : 3,
			"select ?page where { <@base#subject> foaf:page <http://www.originalsoundversion.com/?p=3691> . }" : 1
		}
		test_first_result = {
			"select ?date where { ?album dcterms:created ?date . } order by ?date" : datetime.date(2007,12,19),
			"select ?date where { ?album schema:datePublished ?date . } order by ?date" : datetime.date(2007,12,19),
			"select ?catalog where { ?album schema:datePublished ?date . ?album mo:catalogue_number ?catalog . } order by ?date" : "DERP-10001",
			"select ?album where { ?album schema:datePublished ?date . } order by ?date" : "<@basealbum/5343#subject>",
			"select ?name where { ?album schema:datePublished ?date . ?album schema:name ?name . filter(lang(?name)='ja-latn') } order by ?date" : "Anata wo Yurusanai Original Soundtrack",
			"select ?name where { <@base#subject> schema:name ?name . }": "Dog Ear Records Co., Ltd.",
			"select ?name where { <@base#subject> foaf:name ?name . }": "Dog Ear Records Co., Ltd.",
			"select ?person where { ?person foaf:member <@base#subject> . ?person foaf:name \"Miyu\"@en . }" : "<@baseartist/6680#subject>",
			"select ?picture where { <@base#subject> foaf:depiction ?picture . ?picture a foaf:Image }" : "<https://vgmdb.net/db/assets/logos/135-1246205463.gif>",
			"select ?picture where { <@base#subject> schema:image ?picture . ?picture a schema:ImageObject }" : "<https://vgmdb.net/db/assets/logos/135-1246205463.gif>",
			"select ?picture where { ?picture foaf:depicts <@base#subject> . }" : "<https://vgmdb.net/db/assets/logos/135-1246205463.gif>",
			"select ?picture where { ?picture schema:about <@base#subject> . }" : "<https://vgmdb.net/db/assets/logos/135-1246205463.gif>",
			"select ?thumb where { <@base#subject> foaf:depiction ?picture . ?picture foaf:thumbnail ?thumb . ?thumb a foaf:Image }" : "<https://vgmdb.net/db/assets/logos-medium/135-1246205463.gif>",
			"select ?thumb where { <@base#subject> schema:image ?picture . ?picture schema:thumbnailUrl ?thumb . ?thumb a schema:ImageObject }" : "<https://vgmdb.net/db/assets/logos-medium/135-1246205463.gif>"
		}

		self.run_tests(graph, test_count_results, test_first_result)

		return

	def test_dogear_rdfa(self):
		graph = self.load_rdfa_data('org_dogear.html')
		self.run_dogear_tests(graph)
	def test_dogear_rdf(self):
		graph = self.load_rdf_data('org_dogear.html')
		self.run_dogear_tests(graph)


if __name__ == '__main__':
	unittest.main()
