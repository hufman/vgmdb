# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import productlist

base = os.path.dirname(__file__)

def read_file(name):
	with open(os.path.join(base, name), 'r', errors='ignore') as data:
		return data.read()

class TestProductList(unittest.TestCase):
	def setUp(self):
		pass

	def test_list(self):
		list_code = read_file('productlist.html')
		list = productlist.parse_page(list_code)

		self.assertEqual(u"product/856", list['products'][0]['link'])
		self.assertEqual(u"Darius", list['products'][0]['names']['en'])
		self.assertEqual(u"Franchise", list['products'][0]['type'])
		self.assertEqual(30, len(list['products']))


if __name__ == '__main__':
	unittest.main()
