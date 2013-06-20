# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import productlist

base = os.path.dirname(__file__)

class TestProductList(unittest.TestCase):
	def setUp(self):
		pass

	def test_list(self):
		list_code = file(os.path.join(base, 'productlist.html'), 'r').read()
		list = productlist.parse_productlist_page(list_code)

		self.assertEqual(u"/product/856", list['products'][0]['link'])
		self.assertEqual(u"Darius", list['products'][0]['name'])
		self.assertEqual(u"Franchise", list['products'][0]['type'])
		self.assertEqual(30, len(list['products']))
