# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb.parsers import event

base = os.path.dirname(__file__)

class TestEventRDF(TestRDF):
	data_parser = lambda self,x: event.parse_page(x)
	outputter_type = 'event'
	def setUp(self):
		pass

	def run_m3_tests(self, graph):
		test_count_results = {
			"select ?type where { <@base#subject> rdf:type mo:ReleaseEvent . }" : 1,
			"select ?type where { <@base#subject> rdf:type schema:MusicEvent . }" : 1,
			"select ?person where { <@base#subject> event:time <@base#release_event> . }" : 1,
			"select ?date where { <@base#release_event> tl:start ?date . }" : 1,
			"select ?date where { <@base#release_event> tl:end ?date . }" : 1,
			"select ?album where { <@base#subject> mo:release ?album . }" : 30
		}
		test_first_result = {
			"select ?date where { <@base#release_event> tl:start ?date . }" : datetime.date(2012,10,28),
			"select ?date where { <@base#release_event> tl:end ?date . }" : datetime.date(2012,10,28),
			"select ?date where { <@base#subject> schema:startDate ?date . }" : datetime.date(2012,10,28),
			"select ?date where { <@base#subject> schema:endDate ?date . }" : datetime.date(2012,10,28),
			"select ?catalog where { ?album mo:catalogue_number ?catalog . ?album schema:name ?title . ?album schema:name \"a Tale\"@en . }" : "N/A",
			"select ?catalog where { ?album mo:catalogue_number ?catalog . ?album schema:name ?title . ?album schema:name \"AD:60\"@en . }" : "DVSP-0084",
			"select ?release_date where { ?album dcterms:created ?release_date . ?album schema:name \"a Tale\"@en . }" : datetime.date(2012,10,28),
			"select ?release_date where { ?album schema:datePublished ?release_date . ?album schema:name \"a Tale\"@en . }" : datetime.date(2012,10,28),
			"select ?publisher where { ?album schema:name \"AD:60\"@en . ?album mo:publisher ?publisher . }" : "<@baseorg/331#subject>",
			"select ?name where { ?album mo:publisher ?publisher . ?publisher foaf:name ?name . ?album dcterms:title \"a Tale\"@en . filter(lang(?name)='en') }" : "Clinochlore"
		}

		self.run_tests(graph, test_count_results, test_first_result)

		return
	def test_m3_rdfa(self):
		graph = self.load_rdfa_data('event_m3.html')
		self.run_m3_tests(graph)
	def test_m3_rdf(self):
		graph = self.load_rdf_data('event_m3.html')
		self.run_m3_tests(graph)

	def run_cm54_tests(self, graph):
		test_count_results = {
			"select ?type where { <@base#subject> rdf:type mo:ReleaseEvent . }" : 1,
			"select ?type where { <@base#subject> rdf:type schema:MusicEvent . }" : 1,
			"select ?person where { <@base#subject> event:time <@base#release_event> . }" : 1,
			"select ?date where { <@base#release_event> tl:start ?date . }" : 1,
			"select ?date where { <@base#release_event> tl:end ?date . }" : 1,
		}
		test_first_result = {
			"select ?date where { <@base#release_event> tl:start ?date . }" : datetime.date(1998,8,14),
			"select ?date where { <@base#release_event> tl:end ?date . }" : datetime.date(1998,8,16),
			"select ?date where { <@base#subject> schema:startDate ?date . }" : datetime.date(1998,8,14),
			"select ?date where { <@base#subject> schema:endDate ?date . }" : datetime.date(1998,8,16),
		}

		self.run_tests(graph, test_count_results, test_first_result)

		return
	def test_cm54_rdfa(self):
		graph = self.load_rdfa_data('event_cm54.html')
		self.run_cm54_tests(graph)
	def test_cm54_rdf(self):
		graph = self.load_rdf_data('event_cm54.html')
		self.run_cm54_tests(graph)


if __name__ == '__main__':
	unittest.main()
