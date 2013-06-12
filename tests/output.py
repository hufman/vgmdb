# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import output

base = os.path.dirname(__file__)

mime_names = {"text/html": "html",
              "application/json": "json",
              "text/json": "json",
              "application/x-turtle": "turtle",
              "text/x-turtle": "turtle",
              "application/rdf+xml": "rdf",
              "text/rdf+xml": "rdf"
}


class TestDummyOutput(unittest.TestCase):
	def setUp(self):
		for (key,value) in mime_names.items():
			output.add_mime_name(key, value)
		for name in mime_names.values():
			output.add_name_handler(key, lambda x,y:x)

	def test_decide_format(self):
		self.assertEqual("html", output.decide_format("html", "application/json"))
		self.assertEqual("html", output.decide_format("invalid", "text/html"))
		self.assertEqual("html", output.decide_format("invalid", "text/html,text/json"))
		self.assertEqual("json", output.decide_format("invalid", "text/json,text/html"))
		self.assertEqual("turtle", output.decide_format("invalid", "text/x-turtle,text/html"))
		self.assertEqual("rdf", output.decide_format("invalid", "text/x-turtle,text/rdf+xml;q=2"))
