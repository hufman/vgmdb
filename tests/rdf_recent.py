# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb.parsers import recent
from vgmdb.config import BASE_URL
from urlparse import urljoin

class TestRecentRDF(TestRDF):
	data_parser = lambda self,x: recent.parse_page(x)
	outputter_type = 'recent'
	def setUp(self):
		pass

	def run_albums_tests(self, graph):
		test_count_results = {
			"select ?album where { ?album rdf:type mo:Release . }" : 27,
			"select ?album where { ?album rdf:type schema:MusicAlbum . }" : 27
		}
		test_first_result = {
			"select ?catalog where { <@basealbum/14302#subject> mo:catalogue_number ?catalog . }" : "SDEX-0057",
			"select ?name where { <@basealbum/14302#subject> dcterms:title ?name . FILTER(lang(?name)='en') }" : "Chikyuu wa Tamagotchi?!",
			"select ?name where { <@basealbum/14302#subject> schema:name ?name . FILTER(lang(?name)='en') }" : "Chikyuu wa Tamagotchi?!",
			"select ?name where { <@basealbum/14302#subject> dcterms:title ?name . FILTER(lang(?name)='ja-latn') }" : "Chikyuu wa Tamagotchi?!",
			"select ?name where { <@basealbum/14302#subject> schema:name ?name . FILTER(lang(?name)='ja-latn') }" : "Chikyuu wa Tamagotchi?!"
		}

		self.run_tests(graph, test_count_results, test_first_result)
	def test_albums_rdfa(self):
		graph = self.load_rdfa_data('recent_albums.html')
		self.run_albums_tests(graph)
	def test_albums_rdf(self):
		graph = self.load_rdf_data('recent_albums.html')
		self.run_albums_tests(graph)

	def run_media_tests(self, graph):
		test_count_results = {
			"select ?album where { ?album rdf:type mo:Release . }" : 35,
			"select ?album where { ?album rdf:type schema:MusicAlbum . }" : 35
		}
		test_first_result = {
			"select ?catalog where { <@basealbum/14302#subject> mo:catalogue_number ?catalog . }" : "SDEX-0057",
			"select ?name where { <@basealbum/14302#subject> dcterms:title ?name . FILTER(lang(?name)='en') }" : "Chikyuu wa Tamagotchi?!",
			"select ?name where { <@basealbum/14302#subject> schema:name ?name . FILTER(lang(?name)='en') }" : "Chikyuu wa Tamagotchi?!"
		}

		self.run_tests(graph, test_count_results, test_first_result)
	def test_media_rdfa(self):
		graph = self.load_rdfa_data('recent_media.html')
		self.run_media_tests(graph)
	def test_media_rdf(self):
		graph = self.load_rdf_data('recent_media.html')
		self.run_media_tests(graph)

	def run_tracklists_tests(self, graph):
		test_count_results = {
			"select ?album where { ?album rdf:type mo:Release . }" : 32,
			"select ?album where { ?album rdf:type schema:MusicAlbum . }" : 32
		}
		test_first_result = {
			"select ?catalog where { <@basealbum/10310#subject> mo:catalogue_number ?catalog . }" : "KDSD-00222",
			"select ?name where { <@basealbum/10310#subject> dcterms:title ?name . FILTER(lang(?name)='en') }" : "Tindharia no Tane / Haruka Shimotsuki",
			"select ?name where { <@basealbum/10310#subject> schema:name ?name . FILTER(lang(?name)='en') }" : "Tindharia no Tane / Haruka Shimotsuki",
			"select ?name where { <@basealbum/10310#subject> dcterms:title ?name . FILTER(lang(?name)='ja-latn') }" : "Tindharia no Tane / Haruka Shimotsuki",
			"select ?name where { <@basealbum/10310#subject> schema:name ?name . FILTER(lang(?name)='ja-latn') }" : "Tindharia no Tane / Haruka Shimotsuki"
		}

		self.run_tests(graph, test_count_results, test_first_result)
	def test_tracklists_rdfa(self):
		graph = self.load_rdfa_data('recent_tracklists.html')
		self.run_tracklists_tests(graph)
	def test_tracklists_rdf(self):
		graph = self.load_rdf_data('recent_tracklists.html')
		self.run_tracklists_tests(graph)

	def run_scans_tests(self, graph):
		test_count_results = {
			"select ?album where { ?album rdf:type mo:Release . }" : 17,
			"select ?album where { ?album rdf:type schema:MusicAlbum . }" : 17
		}
		test_first_result = {
			"select ?catalog where { <@basealbum/12019#subject> mo:catalogue_number ?catalog . }" : "BCR-005"
		}

		self.run_tests(graph, test_count_results, test_first_result)
	def test_scans_rdfa(self):
		graph = self.load_rdfa_data('recent_scans.html')
		self.run_scans_tests(graph)
	def test_scans_rdf(self):
		graph = self.load_rdf_data('recent_scans.html')
		self.run_scans_tests(graph)

	def run_artists_tests(self, graph):
		test_count_results = {
			"select ?artist where { ?artist rdf:type schema:MusicGroup . }" : 45
		}
		test_first_result = {
			"select ?name where { <@baseartist/1891#subject> schema:name ?name . FILTER(lang(?name)='en') }" : "Masaya Matsuura"
		}

		self.run_tests(graph, test_count_results, test_first_result)
	def test_artists_rdfa(self):
		graph = self.load_rdfa_data('recent_artists.html')
		self.run_artists_tests(graph)
	def test_artists_rdf(self):
		graph = self.load_rdf_data('recent_artists.html')
		self.run_artists_tests(graph)

	def run_products_tests(self, graph):
		test_count_results = {
			"select ?product where { ?product rdf:type schema:CreativeWork . }" : 16,
			"select ?product where { ?product rdf:type rdfs:Resource . }": 1
		}
		test_first_result = {
			"select ?name where { <@baseproduct/1143#subject> schema:name ?name . FILTER(lang(?name)='en') }" : "Guild Wars 2",
			"select ?name where { <@baseproduct/1143#subject> dcterms:title ?name . FILTER(lang(?name)='en') }" : "Guild Wars 2"
		}

		self.run_tests(graph, test_count_results, test_first_result)
	def test_products_rdfa(self):
		graph = self.load_rdfa_data('recent_products.html')
		self.run_products_tests(graph)
	def test_products_rdf(self):
		graph = self.load_rdf_data('recent_products.html')
		self.run_products_tests(graph)

	def run_labels_tests(self, graph):
		test_count_results = {
			"select ?product where { ?product rdf:type schema:Organization . }" : 17,
			"select ?product where { ?product rdf:type foaf:Organization . }" : 17
		}
		test_first_result = {
			"select ?name where { <@baseorg/1144#subject> schema:name ?name . FILTER(lang(?name)='en') }" : "Walt Disney Records",
			"select ?name where { <@baseorg/1144#subject> dcterms:title ?name . FILTER(lang(?name)='en') }" : "Walt Disney Records"
		}

		self.run_tests(graph, test_count_results, test_first_result)
	def test_labels_rdfa(self):
		graph = self.load_rdfa_data('recent_labels.html')
		self.run_labels_tests(graph)
	def test_labels_rdf(self):
		graph = self.load_rdf_data('recent_labels.html')
		self.run_labels_tests(graph)

	def run_links_tests(self, graph):
		test_count_results = {
			"select ?album where { ?album rdf:type mo:Release . }" : 28,
			"select ?album where { ?album rdf:type schema:MusicAlbum . }" : 28
		}
		test_first_result = {
			"select ?catalog where { <@basealbum/21381#subject> mo:catalogue_number ?catalog . }" : "TASS-0002"
		}

		self.run_tests(graph, test_count_results, test_first_result)
	def test_links_rdfa(self):
		graph = self.load_rdfa_data('recent_links.html')
		self.run_links_tests(graph)
	def test_links_rdf(self):
		graph = self.load_rdf_data('recent_links.html')
		self.run_links_tests(graph)

	def run_ratings_tests(self, graph):
		test_count_results = {
			"select ?album where { ?album rdf:type mo:Release . }" : 48,
			"select ?album where { ?album rdf:type schema:MusicAlbum . }" : 48
		}
		test_first_result = {
			"select ?catalog where { <@basealbum/38376#subject> mo:catalogue_number ?catalog . }" : "WM-0701~2",
			"select ?value where { <@basealbum/38376#subject> schema:review ?review . ?review schema:reviewRating ?rating . ?rating schema:ratingValue ?value . }" : 5,
			"select ?value where { <@basealbum/38376#subject> schema:review ?review . ?review schema:reviewRating ?rating . ?rating schema:bestRating ?value . }" : 5,
			"select ?name where { <@basealbum/38376#subject> dcterms:title ?name . FILTER(lang(?name)='en') }" : "Mahou Daisakusen Original Soundtrack",
			"select ?name where { <@basealbum/38376#subject> schema:name ?name . FILTER(lang(?name)='en') }" : "Mahou Daisakusen Original Soundtrack",
			"select ?name where { <@basealbum/38376#subject> dcterms:title ?name . FILTER(lang(?name)='ja-latn') }" : "Mahou Daisakusen Original Soundtrack",
			"select ?name where { <@basealbum/38376#subject> schema:name ?name . FILTER(lang(?name)='ja-latn') }" : "Mahou Daisakusen Original Soundtrack"
		}

		self.run_tests(graph, test_count_results, test_first_result)
	def test_ratings_rdfa(self):
		graph = self.load_rdfa_data('recent_ratings.html')
		self.run_ratings_tests(graph)
	def test_ratings_rdf(self):
		graph = self.load_rdf_data('recent_ratings.html')
		self.run_ratings_tests(graph)


if __name__ == '__main__':
	unittest.main()
