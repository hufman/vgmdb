# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import utils
from vgmdb.output import commonutils as outpututils

base = os.path.dirname(__file__)

class TestUtils(unittest.TestCase):
	def setUp(self):
		pass

	def test_date_parse(self):
		date = "Aug 3, 2006 01:33 AM"
		self.assertEqual("2006-08-03T01:33", utils.parse_date_time(date))
		date = "Aug 3, 2006 12:33 PM"
		self.assertEqual("2006-08-03T12:33", utils.parse_date_time(date))
		date = "Oct 04, 2000"
		self.assertEqual("2000-10-04", utils.parse_date_time(date))
		date = "November 11, 2011"
		self.assertEqual("2011-11-11", utils.parse_date_time(date))
		date = "Sep, 2011"
		self.assertEqual("2011-09", utils.parse_date_time(date))
		date = "Oct 2011"
		self.assertEqual("2011-10", utils.parse_date_time(date))
		date = "October 2011"
		self.assertEqual("2011-10", utils.parse_date_time(date))
		date = "2011"
		self.assertEqual("2011", utils.parse_date_time(date))
		date = "Jan 7"
		self.assertEqual("0000-01-07", utils.parse_date_time(date))
		date = "Dec, 9"
		self.assertEqual("0000-12-09", utils.parse_date_time(date))
		date = "0"
		self.assertEqual(None, utils.parse_date_time(date))

	def test_dotted_year(self):
		""" Make sure that weird dates with unknown month and days work """
		date = utils.normalize_dotted_date("2007.??.??")
		self.assertEqual("2007", date)
	def test_dotted_month(self):
		""" Make sure that weird dates with unknown days work """
		date = utils.normalize_dotted_date("2007.02.??")
		self.assertEqual("2007-02", date)
	def test_dotted_day(self):
		""" Make sure that conversion from YYYY.MM.DD to YYYY-MM-DD works """
		date = utils.normalize_dotted_date("2007.02.20")
		self.assertEqual("2007-02-20", date)
	def test_dotted_shortday(self):
		""" Make sure that conversion from YYYY.M.D to YYYY-MM-DD works """
		date = utils.normalize_dotted_date("2007.2.9")
		self.assertEqual("2007-02-09", date)
	def test_dashed_shortmonth(self):
		""" Make sure that conversion from YYYY.M.D to YYYY-MM-DD works """
		date = utils.normalize_dashed_date("2007-2")
		self.assertEqual("2007-02", date)

	def test_invalid_html(self):
		invalid = '<table><tr></tr><table five>asdf</table><table>'
		correct = '<table><tr></tr></table><table five>asdf</table><table>'
		self.assertEqual(correct, utils.fix_invalid_table(invalid))
		invalid = '<table><tr><tr></tr></table>'
		correct = '<table><tr></tr></table>'
		self.assertEqual(correct, utils.fix_invalid_table(invalid))
		invalid = '<table><tr></tr></tr></table>'
		correct = '<table><tr></tr></table>'
		self.assertEqual(correct, utils.fix_invalid_table(invalid))

	def test_languagecodes(self):
		tests = {
		    'Japanese':'ja',
		    'Japanese 1':'ja',
		    'Korean, Chinese':'ko-zd',
		    'English':'en',
		    'English iTunes':'en',
		    'English Gaelic':'gd',
		    'Gaelic':'gd'
		}
		for test,expected in tests.items():
			got = outpututils.normalize_language_codes(test)
			self.assertEqual(expected, got)

class TestLinks(unittest.TestCase):
	def test_trim_absolute(self):
		self.assertEqual('album/29', utils.trim_absolute('http://vgmdb.net/album/29'))
		self.assertEqual('http://wikipedia.org/album/29', utils.trim_absolute('http://wikipedia.org/album/29'))

	def test_force_absolute(self):
		self.assertEqual('http://vgmdb.net/album/29', utils.force_absolute('album/29'))
		self.assertEqual('http://wikipedia.org/album/29', utils.force_absolute('http://wikipedia.org/album/29'))

	def test_parse_vgmdb_link(self):
		self.assertEqual('album/29', utils.parse_vgmdb_link('album/29'))
		self.assertEqual('release/29', utils.parse_vgmdb_link('db/release.php?id=29'))

if __name__ == '__main__':
	unittest.main()
