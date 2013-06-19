# -*- coding: UTF-8 -*-
import os
import datetime
import unittest

from ._rdf import TestRDF
from vgmdb import artist

base = os.path.dirname(__file__)

class TestArtistsRDF(TestRDF):
	data_parser = lambda self,x: artist.parse_artist_page(x)
	outputter_type = 'artist'
	def setUp(self):
		pass

	def run_nobuo_tests(self, graph):
		test_count_results = {
			"select ?artist where { <@base#subject> rdf:type foaf:Person . }" : 1,
			"select ?artist where { <@base#subject> rdf:type schema:Person . }" : 1,
			"select ?artist where { <@base#subject> rdf:type schema:MusicGroup . }" : 1,
			"select ?name where { ?person rdf:type foaf:Person . ?person foaf:name ?name . }" : 1,
			"select ?album where { ?person foaf:made ?album . }" : 316,
			"select ?group where { ?person mo:member_of ?group . }" : 4,
			"select ?artist where { ?artist foaf:page <http://www.dogearrecords.com/> . }" : 1,
			"select ?site where { <@base#subject> foaf:page ?site . }" : 29,
			"select ?album where { ?album dcterms:creator ?artist . }" : 316,
			"select ?album where { ?album schema:byArtist ?artist . }" : 316,
			"select ?album where { ?album mo:tribute_to ?artist . }" : 336,
		}
		test_first_result = {
			"select ?name where { <@base#subject> foaf:name ?name . }" : "Nobuo Uematsu",
			"select ?name where { ?person rdf:type foaf:Person . ?person foaf:name ?name . }" : u'Nobuo Uematsu',
			"select ?birthdate where { ?birth rdf:type bio:birth . ?birth bio:date ?birthdate . }" : datetime.date(1959,03,21),
			"select ?name where { ?album rdf:type schema:MusicAlbum . <@base#subject> foaf:made ?album . ?album dcterms:title ?name . ?album schema:datePublished ?date . filter(lang(?name) = 'en')  } order by ?date" : 'CRUISE CHASER BLASSTY',
			"select ?name where { ?album rdf:type schema:MusicAlbum . ?artist foaf:made ?album . ?album dcterms:title ?name . ?album schema:datePublished ?date . filter(lang(?name) = 'en')  } order by ?date" : 'CRUISE CHASER BLASSTY',
			"select ?date where { ?album rdf:type schema:MusicAlbum . ?artist foaf:made ?album . ?album schema:datePublished ?date . } order by ?date" : datetime.date(1986,04,26),
			"select ?date where { ?album rdf:type mo:Release . ?artist foaf:made ?album . ?album dcterms:created ?date . } order by ?date" : datetime.date(1986,04,26),
			"select ?catalog where { ?album mo:catalogue_number ?catalog . ?album dcterms:title \"SYMPHONIC SUITE FINAL FANTASY\"@en . }" : "H28X-10007",
			"select ?handle where { ?person foaf:account ?account . ?account foaf:accountServiceHomepage <http://www.twitter.com/> . ?account foaf:accountName ?handle . }" : "UematsuNobuo"
		}

		self.run_tests(graph, test_count_results, test_first_result)

		return
	def test_nobuo_rdfa(self):
		graph = self.load_rdfa_data('artist_nobuo.html')
		self.run_nobuo_tests(graph)
	def test_nobuo_rdf(self):
		graph = self.load_rdf_data('artist_nobuo.html')
		self.run_nobuo_tests(graph)

	def run_ss_tests(self, graph):
		test_count_results = {
			"select ?artist where { <@base#subject> rdf:type foaf:Organization . }" : 1,
			"select ?artist where { <@base#subject> rdf:type schema:MusicGroup . }" : 1,
			"select ?name where { ?person schema:musicGroupMember ?member . ?member foaf:name ?name . }" : 2,
		}
		test_first_result = {
			"select ?name where { ?group schema:album ?album . ?album dcterms:title ?name . ?album schema:datePublished ?date . filter(lang(?name)='en') } order by ?date" : u'Square Enix Music Powered Vol.1'
		}

		self.run_tests(graph, test_count_results, test_first_result)

		return
	def test_ss_rdfa(self):
		graph = self.load_rdfa_data('artist_ss.html')
		self.run_ss_tests(graph)
	def test_ss_rdf(self):
		graph = self.load_rdf_data('artist_ss.html')
		self.run_ss_tests(graph)

	def run_offenbach_tests(self, graph):
		test_count_results = {
			"select ?artist where { <@base#subject> rdf:type foaf:Person . }" : 1,
			"select ?artist where { <@base#subject> rdf:type schema:MusicGroup . }" : 1
		}
		test_first_result = {
			"select ?date where { ?birth bio:principal <@base#subject> . ?birth a bio:birth . ?birth bio:date ?date . }" : datetime.date(1819,6,20),
			"select ?date where { ?death bio:principal <@base#subject> . ?death a bio:death . ?death bio:date ?date . }" : datetime.date(1880,10,05)
		}

		self.run_tests(graph, test_count_results, test_first_result)

		return
	def test_offenbach_rdfa(self):
		graph = self.load_rdfa_data('artist_offenbach.html')
		self.run_offenbach_tests(graph)
	def test_offenbach_rdf(self):
		graph = self.load_rdf_data('artist_offenbach.html')
		self.run_offenbach_tests(graph)
