# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import albumlist

base = os.path.dirname(__file__)

class TestAlbumList(unittest.TestCase):
	def setUp(self):
		pass

	def test_list(self):
		list_code = file(os.path.join(base, 'albumlist.html'), 'r').read()
		list = albumlist.parse_page(list_code)

		self.assertEqual(u"/album/12991", list['albums'][0]['link'])
		self.assertEqual(u"f", list['albums'][0]['titles']['en'])
		self.assertEqual(u"GFCA-7", list['albums'][1]['catalog'])
		self.assertEqual(u"2002-07-13", list['albums'][2]['release_date'])
		self.assertEqual(u"2007-08", list['albums'][22]['release_date'])
		self.assertEqual(u"1999", list['albums'][23]['release_date'])
