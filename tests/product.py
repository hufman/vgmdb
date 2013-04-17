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

	def test_witcher(self):
		witcher_code = file(os.path.join(base, 'product_witcher.html'), 'r').read()
		witcher = product.parse_product_page(witcher_code)
		self.assertEqual(u"2011-05-17", witcher['release_date'])
		self.assertEqual(u"The Witcher", witcher['franchises'][0]['name']['en'])
		self.assertEqual(u"The Witcher 2: Assassins of Kings", witcher['name'])
		self.assertEqual(u"Wiedźmin 2: Zabójcy królów", witcher['name_real'])
		self.assertEqual(0, len(witcher['releases']))
		self.assertEqual(u"KK25", witcher['albums'][0]['catalog'])

