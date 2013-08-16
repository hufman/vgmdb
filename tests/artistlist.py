# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import artistlist

base = os.path.dirname(__file__)

class TestArtistList(unittest.TestCase):
	def setUp(self):
		pass

	def test_list(self):
		list_code = file(os.path.join(base, 'artistlist.html'), 'r').read()
		list = artistlist.parse_page(list_code)

		self.assertEqual(99, len(list['artists']))
		self.assertEqual(u"/artist/3535", list['artists'][0]['link'])
		self.assertEqual(u"/artist/12702", list['artists'][3]['link'])
		self.assertEqual(u"/artist/11699", list['artists'][96]['link'])
		self.assertEqual(u"A BONE", list['artists'][0]['names']['en'])
		self.assertEqual(u"アービー", list['artists'][3]['name_real'])
