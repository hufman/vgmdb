# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import utils

base = os.path.dirname(__file__)

class TestUtils(unittest.TestCase):
	def setUp(self):
		pass

	def test_date_parse(self):
		date = "Aug 3, 2006 01:33 AM"
		self.assertEqual("2006-08-03T01:33", utils.parse_date_time(date))
		date = "Oct 04, 2000"
		self.assertEqual("2000-10-04", utils.parse_date_time(date))
