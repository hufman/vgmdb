# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb import artistlist
from vgmdb.config import BASE_URL
from urlparse import urljoin

class TestArtistlistRDF(TestRDF):
	data_parser = lambda self,x: artistlist.parse_artistlist_page(x)
	outputter_type = 'artistlist'
	def setUp(self):
		pass

	def run_list_tests(self, graph):
		test_count_results = {
			"select ?artist where { ?artist rdf:type schema:MusicGroup . }" : 99
		}
		test_first_result = {
			"select ?name where { <@baseartist/6616#subject> foaf:name ?name . }" : u"Aaron Harmon"
		}
		self.run_tests(graph, test_count_results, test_first_result)
	def test_list_rdfa(self):
		graph = self.load_rdfa_data('artistlist.html')
		self.run_list_tests(graph)
	def test_list_rdf(self):
		graph = self.load_rdf_data('artistlist.html')
		self.run_list_tests(graph)

