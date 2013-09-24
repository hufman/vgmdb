# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import product

base = os.path.dirname(__file__)

class TestProducts(unittest.TestCase):
	def setUp(self):
		pass

	def test_skyrim(self):
		skyrim_code = file(os.path.join(base, 'product_skyrim.html'), 'r').read()
		skyrim = product.parse_page(skyrim_code)
		self.assertEqual(u"2011-11-11", skyrim['release_date'])
		self.assertEqual(u"Bethesda Game Studios", skyrim['organizations'][0])
		self.assertEqual(u"The Elder Scrolls V: Skyrim", skyrim['name'])
		self.assertEqual(u"JPY (Japan)", skyrim['releases'][3]['region'])
		self.assertEqual(u"Gaming Fantasy", skyrim['albums'][3]['titles']['en'])
		self.assertEqual("2012-09-12T18:46", skyrim['meta']['added_date'])
		self.assertEqual("http://vgmdb.net/db/assets/logos/1387-pr-1347504448.jpg", skyrim['picture_full'])
		self.assertEqual("http://vgmdb.net/db/assets/logos-medium/1387-pr-1347504448.jpg", skyrim['picture_small'])

	def test_witcher(self):
		witcher_code = file(os.path.join(base, 'product_witcher.html'), 'r').read()
		witcher = product.parse_page(witcher_code)
		self.assertEqual(u"2011-05-17", witcher['release_date'])
		self.assertEqual(u"The Witcher", witcher['franchises'][0]['names']['en'])
		self.assertEqual(u"The Witcher 2: Assassins of Kings", witcher['name'])
		self.assertEqual(u"Wiedźmin 2: Zabójcy królów", witcher['name_real'])
		self.assertEqual(0, len(witcher['releases']))
		self.assertEqual(u"KK25", witcher['albums'][0]['catalog'])
		self.assertEqual(u"Efendija", witcher['meta']['edited_user'])

	def test_at(self):
		at_code = file(os.path.join(base, 'product_at.html'), 'r').read()
		at = product.parse_page(at_code)
		self.assertEqual(u"Ar tonelico", at['name'])
		self.assertEqual(u"アルトネリコ", at['name_real'])
		self.assertEqual(4, len(at['titles']))
		self.assertEqual(u"Ar tonelico: Melody of Elemia", at['titles'][0]['names']['en'])
		self.assertEqual(u"product/566", at['titles'][0]['link'])
		self.assertEqual(u"2010-12-26T03:20", at['meta']['added_date'])
		self.assertTrue(not at.has_key('picture_full'))
		two = [at['albums'][32], at['albums'][33]]
		for thing in two:	# two albums released on the same date, hard to sort
			if thing['link'] == 'album/20283':
				self.assertEqual(True, thing['reprint'])

	def test_empty(self):
		im_code = file(os.path.join(base, 'product_empty.html'), 'r').read()
		im = product.parse_page(im_code)
		self.assertEqual(u"PROJECT IM@S", im['name'])
		self.assertEqual(u"プロジェクト・アイマス", im['name_real'])
		self.assertEqual(0, len(im['titles']))
		self.assertEqual(0, len(im['albums']))
