# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import product

base = os.path.dirname(__file__)

class TestProducts(unittest.TestCase):
	def setUp(self):
		pass

	def test_skyrim(self):
		skyrim_code = file(os.path.join(base, 'product_skyrim.html'), 'r').read()
		skyrim = product.parse_product_page(skyrim_code)
		self.assertEqual(u"2011-11-11", skyrim['release_date'])
		self.assertEqual(u"Bethesda Game Studios", skyrim['organizations'][0])
		self.assertEqual(u"The Elder Scrolls V: Skyrim", skyrim['name'])
		self.assertEqual(u"JPY (Japan)", skyrim['releases'][3]['region'])
		self.assertEqual(u"Gaming Fantasy", skyrim['albums'][3]['titles']['en'])
		self.assertEqual("2012-09-12T18:46", skyrim['meta']['added_date'])

	def test_witcher(self):
		witcher_code = file(os.path.join(base, 'product_witcher.html'), 'r').read()
		witcher = product.parse_product_page(witcher_code)
		self.assertEqual(u"2011-05-17", witcher['release_date'])
		self.assertEqual(u"The Witcher", witcher['franchises'][0]['name']['en'])
		self.assertEqual(u"The Witcher 2: Assassins of Kings", witcher['name'])
		self.assertEqual(u"Wiedźmin 2: Zabójcy królów", witcher['name_real'])
		self.assertEqual(0, len(witcher['releases']))
		self.assertEqual(u"KK25", witcher['albums'][0]['catalog'])
		self.assertEqual(u"Efendija", witcher['meta']['edited_user'])

	def test_at(self):
		at_code = file(os.path.join(base, 'product_at.html'), 'r').read()
		at = product.parse_product_page(at_code)
		self.assertEqual(u"Ar tonelico", at['name'])
		self.assertEqual(u"アルトネリコ", at['name_real'])
		self.assertEqual(4, len(at['titles']))
		self.assertEqual(u"Ar tonelico: Melody of Elemia", at['titles'][0]['name']['en'])
		self.assertEqual(u"2010-12-26T03:20", at['meta']['added_date'])
