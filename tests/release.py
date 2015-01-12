# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import release

base = os.path.dirname(__file__)

class TestReleases(unittest.TestCase):
	def setUp(self):
		pass

	def test_ataraxiavita(self):
		at_code = file(os.path.join(base, 'release_hollowataraxiavita.html'), 'r').read()
		at = release.parse_page(at_code)
		self.assertEqual(u'Fate/hollow ataraxia', at['name'])
		self.assertEqual(u'Fate/hollow ataraxia', at['products'][0]['names']['en'])
		self.assertEqual(u'product/2029', at['products'][0]['link'])
		self.assertEqual(u'VLJM-35123', at['catalog'])
		self.assertEqual(u'4997766201689', at['upc'])
		self.assertEqual(u'2014-11-27', at['release_date'])
		self.assertEqual(u'Official Release', at['release_type'])
		self.assertEqual(u'Sony PlayStation Vita', at['platform'])
		self.assertEqual(u'JPY (Japan)', at['region'])
		self.assertEqual(2, len(at['release_albums']))
		self.assertEqual(25, len(at['product_albums']))
		self.assertEqual(u'broKen NIGHT / Aimer', at['release_albums'][0]['titles']['en'])
		self.assertEqual(u'DFCL-2100', at['release_albums'][0]['catalog'])
		self.assertEqual([u'Vocal', u'OP/ED/Insert'], at['release_albums'][0]['classifications'])
		self.assertEqual(u'album/48061', at['release_albums'][0]['link'])
		self.assertEqual(u'game', at['release_albums'][0]['type'])
		self.assertEqual(u'2014-12-17', at['release_albums'][0]['date'])
		self.assertEqual(u'TYPE-MOON Fes. Drama CD', at['product_albums'][-2]['titles']['en'])
		self.assertEqual(u'ANZX-6458', at['product_albums'][-2]['catalog'])
		self.assertEqual([u'Drama'], at['product_albums'][-2]['classifications'])
		self.assertEqual(u'album/37706', at['product_albums'][-2]['link'])
		self.assertEqual(u'bonus', at['product_albums'][-2]['type'])
		self.assertEqual(u'2013-01-16', at['product_albums'][-2]['date'])
		self.assertEqual(u'2014-09-13T08:01', at['meta']['added_date'])
		self.assertEqual(u'2014-09-13T08:01', at['meta']['edited_date'])
		self.assertEqual(112, at['meta']['visitors'])

	def test_ataraxiapc(self):
		at_code = file(os.path.join(base, 'release_hollowataraxiapc.html'), 'r').read()
		at = release.parse_page(at_code)
		self.assertEqual(0, len(at['release_albums']))	# this release doesn't have albums
		self.assertEqual(25, len(at['product_albums']))
		self.assertEqual(u'ANZX-6458', at['product_albums'][-2]['catalog'])
		self.assertEqual([u'Drama'], at['product_albums'][-2]['classifications'])
		self.assertEqual(u'album/37706', at['product_albums'][-2]['link'])
		self.assertEqual(u'bonus', at['product_albums'][-2]['type'])
		self.assertEqual(u'2013-01-16', at['product_albums'][-2]['date'])

if __name__ == '__main__':
	unittest.main()
