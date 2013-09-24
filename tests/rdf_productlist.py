# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb.parsers import productlist
from vgmdb.config import BASE_URL
from urlparse import urljoin

class TestArtistlistRDF(TestRDF):
	data_parser = lambda self,x: productlist.parse_page(x)
	outputter_type = 'productlist'
	def setUp(self):
		pass

	def run_list_tests(self, graph):
		test_count_results = {
			"select ?product where { ?product rdf:type schema:CreativeWork . }" : 30
		}
		test_first_result = {
			"select ?name where { <@baseproduct/856#subject> dcterms:title ?name . }" : u"Darius",
			"select ?name where { <@baseproduct/856#subject> schema:name ?name . }" : u"Darius"
		}
		self.run_tests(graph, test_count_results, test_first_result)
	def test_list_rdfa(self):
		graph = self.load_rdfa_data('productlist.html')
		self.run_list_tests(graph)
	def test_list_rdf(self):
		graph = self.load_rdf_data('productlist.html')
		self.run_list_tests(graph)

