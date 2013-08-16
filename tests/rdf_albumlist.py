# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb import albumlist
from vgmdb.config import BASE_URL
from urlparse import urljoin

class TestAlbumlistRDF(TestRDF):
	data_parser = lambda self,x: albumlist.parse_page(x)
	outputter_type = 'albumlist'
	def setUp(self):
		pass

	def run_list_tests(self, graph):
		test_count_results = {
			"select ?album where { ?album rdf:type mo:Release . }" : 99,
			"select ?album where { ?album rdf:type schema:MusicAlbum . }" : 99
		}
		test_first_result = {
			"select ?published where { <@basealbum/12991#subject> schema:datePublished ?published . }" : datetime.date(2004,04,29),
			"select ?published where { <@basealbum/12991#subject> dcterms:created ?published . }" : datetime.date(2004,04,29),
			"select ?published where { <@basealbum/12991#subject> mo:catalogue_number ?published . }" : "OEMM-0073",
			"select ?name where { <@basealbum/12992#subject> dcterms:title ?name . FILTER(lang(?name)='en') }" : "f II"
		}

		self.run_tests(graph, test_count_results, test_first_result)
	def test_list_rdfa(self):
		graph = self.load_rdfa_data('albumlist.html')
		self.run_list_tests(graph)
	def test_list_rdf(self):
		graph = self.load_rdf_data('albumlist.html')
		self.run_list_tests(graph)

