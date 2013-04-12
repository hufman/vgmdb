# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import artist

base = os.path.dirname(__file__)

class TestArtists(unittest.TestCase):
	def setUp(self):
		pass

	def test_nobuo(self):
		nobuo_code = file(os.path.join(base, 'artist_nobuo.html'), 'r').read()
		nobuo = artist.parse_artist_page(nobuo_code)
		print(nobuo)
		self.assertEqual(nobuo['name'], 'Nobuo Uematsu')
		self.assertEqual(nobuo['sex'], 'male')

	def test_nobuo_name(self):
		""" Japanese name """
		nobuo_name = u"植松 伸夫 (うえまつ のぶお)"
		name_info = artist._parse_full_name(nobuo_name)
		self.assertEqual(u'植松 伸夫', name_info['name_real'])
		self.assertEqual(u'うえまつ のぶお', name_info['name_trans'])

	def test_sungwoon_name(self):
		""" Korean name """
		sung_name = u"장 성운 (ジャン ソンウン)"
		name_info = artist._parse_full_name(sung_name)
		self.assertEqual( u'장 성운',name_info['name_real'])
		self.assertEqual(u'ジャン ソンウン', name_info['name_trans'])

	def test_jeremy_name(self):
		""" English names don't have anything in this field """
		jeremy_name = u""
		name_info = artist._parse_full_name(jeremy_name)
		self.assertEqual(0, len(name_info.keys()))
