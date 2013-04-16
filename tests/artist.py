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
		self.assertEqual(u'Nobuo Uematsu', nobuo['name'])
		self.assertEqual(u'male', nobuo['sex'])
		self.assertEqual(u'Mar 21, 1959', nobuo['info']['Birthdate'])
		self.assertEqual(1, len(nobuo['info']['Organizations']))
		self.assertEqual(1, len(nobuo['organizations']))
		self.assertEqual(u'Dog Ear Records', nobuo['info']['Organizations'][0]['name'])
		self.assertEqual(u'Dog Ear Records', nobuo['organizations'][0]['name'])
		self.assertEqual(u'Earthbound Papas', nobuo['units'][0]['name'])
		self.assertEqual(u'CRUISE CHASER BLASSTY', nobuo['discography'][0]['titles']['en'])
		self.assertEqual(u'/album/11113', nobuo['discography'][0]['link'])
		self.assertEqual(u'/album/719', nobuo['featured_on'][0]['link'])
		self.assertEqual(u'bonus', nobuo['discography'][0]['type'])
		self.assertEqual(u'1986-04-26', nobuo['discography'][0]['date'])
		self.assertEqual(u'H25X-20015', nobuo['discography'][2]['catalog'])
		self.assertTrue(u'Composer' in nobuo['discography'][0]['roles'])
		self.assertEqual(u'DOGEARRECORDS', nobuo['websites']['Official'][0]['name'])
		self.assertEqual('UematsuNobuo', nobuo['twitter_names'][0])

	def test_nobuo_name(self):
		""" Japanese name """
		nobuo_name = u"植松 伸夫 (うえまつ のぶお)"
		name_info = artist._parse_full_name(nobuo_name)
		self.assertEqual(u'植松 伸夫', name_info['name_real'])
		self.assertEqual(u'うえまつ のぶお', name_info['name_trans'])

	def test_black_mages_name(self):
		""" no trans name """
		blackmages_name = u"ザ・ブラックメイジーズ"
		name_info = artist._parse_full_name(blackmages_name)
		self.assertEqual(u'ザ・ブラックメイジーズ', name_info['name_real'])
		self.assertTrue(not name_info.has_key('name_trans'))

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

	def test_year(self):
		""" Make sure that weird dates with unknown month and days work """
		date = artist._normalize_date("2007.??.??")
		self.assertEqual("2007", date)
	def test_month(self):
		""" Make sure that weird dates with unknown days work """
		date = artist._normalize_date("2007.02.??")
		self.assertEqual("2007-02", date)
	def test_day(self):
		""" Make sure that conversion from YYYY.MM.DD to YYYY-MM-DD works """
		date = artist._normalize_date("2007.02.20")
		self.assertEqual("2007-02-20", date)

	def test_ss(self):
		ss_code = file(os.path.join(base, 'artist_ss.html'), 'r').read()
		ss = artist.parse_artist_page(ss_code)
		self.assertEqual(u'Composer (as HAPPY-SYNTHESIZER)', ss['discography'][12]['roles'][0])
		self.assertEqual(u'Arranger (as (S_S))', ss['discography'][13]['roles'][0])
		self.assertEqual(u'HAPPY-SYNTHESIZER', ss['aliases'][1]['name'])
		self.assertEqual(u'Takeshi Nagai', ss['members'][0]['name'])
