# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb import product

base = os.path.dirname(__file__)

class TestProductRDF(TestRDF):
	data_parser = lambda self,x: product.parse_product_page(x)
	outputter_type = 'product'
	def setUp(self):
		pass

	def run_skyrim_tests(self, graph):
		test_count_results = {
			"select ?type where { <@base#subject> rdf:type schema:CreativeWork . }" : 1
		}
		test_first_result = {
			"select ?name where { <@base#subject> dcterms:title ?name . }" : "The Elder Scrolls V: Skyrim",
			"select ?name where { <@base#subject> schema:name ?name . }" : "The Elder Scrolls V: Skyrim",
			"select ?catalog where { ?album mo:catalogue_number \"JOY-552\" . ?album mo:catalogue_number ?catalog . } " : "JOY-552",
			"select ?name where { ?album mo:catalogue_number \"JOY-552\" . ?album dcterms:title ?name . filter(lang(?name)='en') } " : "A Bard's Side Quest",
			"select ?date where { ?album mo:catalogue_number \"JOY-552\" . ?album dcterms:created ?date . } " : datetime.date(2013,01,18),
			"select ?about where { ?album mo:catalogue_number \"JOY-552\" . ?album schema:about ?about . } " : "<@base#subject>",
			"select ?image where { <@base#subject> foaf:depiction ?image . } " : "<http://vgmdb.net/db/assets/logos/1387-pr-1347504448.jpg>",
			"select ?image where { ?image foaf:depicts <@base#subject> . } " : "<http://vgmdb.net/db/assets/logos/1387-pr-1347504448.jpg>",
			"select ?thumb where { <@base#subject> foaf:depiction ?image . ?image foaf:thumbnail ?thumb . } " : "<http://vgmdb.net/db/assets/logos-medium/1387-pr-1347504448.jpg>"
		}

		self.run_tests(graph, test_count_results, test_first_result)

		return

	def test_skyrim_rdfa(self):
		graph = self.load_rdfa_data('product_skyrim.html')
		self.run_skyrim_tests(graph)
	def test_skyrim_rdf(self):
		graph = self.load_rdf_data('product_skyrim.html')
		self.run_skyrim_tests(graph)

	def run_witcher_tests(self, graph):
		test_count_results = {
			"select ?type where { <@base#subject> rdf:type schema:CreativeWork . }" : 1,
			"select ?thing where { ?thing rdf:type schema:CreativeWork . }" : 2,
			"select ?name where { ?product schema:name \"The Witcher\"@en . }" : 1,
			"select ?name where { ?product schema:name \"Wiedźmin\"@ja . }" : 1,
			"select ?album where { ?album schema:about <@base#subject> . }" : 8
		}
		test_first_result = {
			"select ?name where { <@base#subject> dcterms:title ?name . }" : "The Witcher 2: Assassins of Kings",
			"select ?name where { <@base#subject> schema:name ?name . }" : "The Witcher 2: Assassins of Kings"
		}

		self.run_tests(graph, test_count_results, test_first_result)

		return

	def test_witcher_rdfa(self):
		graph = self.load_rdfa_data('product_witcher.html')
		self.run_witcher_tests(graph)
	def test_witcher_rdf(self):
		graph = self.load_rdf_data('product_witcher.html')
		self.run_witcher_tests(graph)
