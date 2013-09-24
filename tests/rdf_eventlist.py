# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb.parsers import eventlist
from vgmdb.config import BASE_URL
from urlparse import urljoin

class TestOrglistRDF(TestRDF):
	data_parser = lambda self,x: eventlist.parse_page(x)
	outputter_type = 'eventlist'
	def setUp(self):
		pass

	def run_list_tests(self, graph):
		test_count_results = {
			"select ?event where { ?event rdf:type mo:ReleaseEvent . }" : 152,
			"select ?event where { ?event rdf:type schema:MusicEvent . }" : 152,
			"select ?name where { <@baseevent/44#subject> schema:name ?name . FILTER(lang(?name)='en')}" : 1,
			"select ?name where { <@baseevent/158#subject> schema:name ?name . FILTER(lang(?name)='en')}" : 1
		}
		test_first_result = {
			"select ?name where { <@baseevent/44#subject> schema:name ?name . FILTER(lang(?name)='en')}" : u"BrightSeason9",
			"select ?name where { <@baseevent/158#subject> schema:name ?name . FILTER(lang(?name)='en')}" : u"M3-2013 Spring",
			"select ?name where { <@baseevent/22#subject> schema:name ?name . FILTER(lang(?name)='ja')}" : u"コミックマーケット60",
			"select ?name where { <@baseevent/157#subject> schema:name ?name . FILTER(lang(?name)='ja')}" : u"コミックマーケット８４"
		}
		self.run_tests(graph, test_count_results, test_first_result)
	def run_list_tests_2001(self, graph):
		test_count_results = {
			"select ?event where { ?event rdf:type mo:ReleaseEvent . }" : 4,
			"select ?event where { ?event rdf:type schema:MusicEvent . }" : 4,
			"select ?name where { <@baseevent/44#subject> schema:name ?name . FILTER(lang(?name)='en')}" : 1,
			"select ?name where { <@baseevent/158#subject> schema:name ?name . FILTER(lang(?name)='en')}" : 0
		}
		test_first_result = {
			"select ?name where { <@baseevent/44#subject> schema:name ?name . FILTER(lang(?name)='en')}" : u"BrightSeason9",
			"select ?name where { <@baseevent/22#subject> schema:name ?name . FILTER(lang(?name)='ja')}" : u"コミックマーケット60"
		}
		self.run_tests(graph, test_count_results, test_first_result)
	def run_list_tests_2013(self, graph):
		test_count_results = {
			"select ?event where { ?event rdf:type mo:ReleaseEvent . }" : 3,
			"select ?event where { ?event rdf:type schema:MusicEvent . }" : 3,
			"select ?name where { <@baseevent/44#subject> schema:name ?name . FILTER(lang(?name)='en')}" : 0,
			"select ?name where { <@baseevent/158#subject> schema:name ?name . FILTER(lang(?name)='en')}" : 1
		}
		test_first_result = {
			"select ?name where { <@baseevent/158#subject> schema:name ?name . FILTER(lang(?name)='en')}" : u"M3-2013 Spring",
			"select ?name where { <@baseevent/157#subject> schema:name ?name . FILTER(lang(?name)='ja')}" : u"コミックマーケット８４"
		}
		self.run_tests(graph, test_count_results, test_first_result)
	def test_list_rdfa_2001(self):
		graph = self.load_rdfa_data('eventlist.html', '2001')
		self.run_list_tests_2001(graph)
	def test_list_rdfa_2013(self):
		graph = self.load_rdfa_data('eventlist.html', '2013')
		self.run_list_tests_2013(graph)
	def test_list_rdfa(self):
		graph = self.load_rdfa_data('eventlist.html')
		self.run_list_tests(graph)
	def test_list_rdf(self):
		graph = self.load_rdf_data('eventlist.html')
		self.run_list_tests(graph)

