# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import artist

base = os.path.dirname(__file__)

class TestArtists(unittest.TestCase):
	def setUp(self):
		pass

	def test_nobuo(self):
		nobuo_code = file(os.path.join(base, 'artist_nobuo.html'), 'r').read()
		nobuo = artist.parse_page(nobuo_code)
		self.assertEqual(u'Nobuo Uematsu', nobuo['name'])
		self.assertEqual(u'male', nobuo['sex'])
		self.assertEqual(u'Mar 21, 1959', nobuo['info']['Birthdate'])
		self.assertEqual('1959-03-21', nobuo['birthdate'])
		self.assertEqual(1, len(nobuo['info']['Organizations']))
		self.assertEqual(1, len(nobuo['organizations']))
		self.assertEqual(u'Dog Ear Records', nobuo['info']['Organizations'][0]['names']['en'])
		self.assertEqual(u'Dog Ear Records', nobuo['organizations'][0]['names']['en'])
		self.assertEqual(u'Individual', nobuo['type'])
		self.assertEqual(u'Earthbound Papas', nobuo['units'][0]['names']['en'])
		self.assertEqual(u'CRUISE CHASER BLASSTY', nobuo['discography'][0]['titles']['en'])
		self.assertEqual(u'album/11113', nobuo['discography'][0]['link'])
		self.assertEqual(u'album/718', nobuo['featured_on'][0]['link'])
		self.assertEqual(u'bonus', nobuo['discography'][0]['type'])
		self.assertEqual(u'1986-04-26', nobuo['discography'][0]['date'])
		self.assertEqual(u'H25X-20015', nobuo['discography'][2]['catalog'])
		self.assertTrue(u'Composer' in nobuo['discography'][0]['roles'])
		self.assertEqual(u'DOGEARRECORDS', nobuo['websites']['Official'][0]['name'])
		self.assertEqual('UematsuNobuo', nobuo['twitter_names'][0])
		self.assertEqual('2007-10-17T09:14', nobuo['meta']['added_date'])
		self.assertEqual('https://thumb-media.vgm.io/artists/77/77/77-1345913713.jpg', nobuo['picture_small'])
		self.assertEqual('https://media.vgm.io/artists/77/77/77-1345913713.jpg', nobuo['picture_full'])

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

	def test_ss(self):
		ss_code = file(os.path.join(base, 'artist_ss.html'), 'r').read()
		ss = artist.parse_page(ss_code)
		self.assertEqual(u'Composer (as HAPPY-SYNTHESIZER)', ss['discography'][13]['roles'][0])
		self.assertEqual(u'Arranger (as (S_S))', ss['discography'][14]['roles'][0])
		self.assertEqual(u'DIRTY-SYNTHESIZER', ss['aliases'][1]['names']['en'])
		self.assertEqual(u'HAPPY-SYNTHESIZER', ss['aliases'][3]['names']['en'])
		self.assertEqual(u'Takeshi Nagai', ss['members'][0]['names']['en'])
		self.assertEqual(u'2011-10-03T05:45', ss['meta']['edited_date'])
		self.assertEqual(u'Unit', ss['type'])

	def test_s_s(self):
		# sexy synthesizer alias
		ss_code = file(os.path.join(base, 'artist_s_s.html'), 'r').read()
		ss = artist.parse_page(ss_code)
		self.assertEqual(u'(S_S)', ss['name'])
		self.assertEqual(u'Alias', ss['type'])

	def test_offenbach(self):
		offenbach_code = file(os.path.join(base, 'artist_offenbach.html'), 'r').read()
		offenbach = artist.parse_page(offenbach_code)
		self.assertEqual(u'Jacques Offenbach', offenbach['name'])
		self.assertEqual(u'male', offenbach['sex'])
		self.assertEqual(u'Individual', offenbach['type'])
		self.assertEqual('1819-06-20', offenbach['birthdate'])
		self.assertEqual('1880-10-05', offenbach['deathdate'])

	def test_key(self):
		key_code = file(os.path.join(base, 'artist_key.html'), 'r').read()
		key = artist.parse_page(key_code)
		self.assertEqual(u'Jun Maeda', key['name'])
		self.assertEqual(u'Individual', key['type'])
		self.assertEqual(u'male', key['sex'])
		self.assertEqual(1, len(key['aliases']))
		self.assertEqual(u'KEY', key['aliases'][0]['names']['en'])

	def test_rookies(self):
		rookies_code = file(os.path.join(base, 'artist_rookies.html'), 'r').read()
		rookies = artist.parse_page(rookies_code)
		self.assertEqual(u"ROOKiEZ is PUNK'D", rookies['name'])
		self.assertEqual(3, len(rookies['info']['Members']))
		self.assertEqual(u'Unit', rookies['type'])
		self.assertFalse('link' in rookies['info']['Members'][0])
		self.assertEqual(u'RYOTA', rookies['info']['Members'][0]['names']['en'])
		self.assertEqual(u'artist/15569', rookies['info']['Members'][2]['link'])
		self.assertEqual(u'SHiNNOSUKE', rookies['info']['Members'][2]['names']['en'])
		self.assertFalse('link' in rookies['info']['Former Members'][0])
		self.assertEqual(u'2RASH', rookies['info']['Former Members'][0]['names']['en'])

	def test_horie(self):
		horie_code = file(os.path.join(base, 'artist_horie.html'), 'r').read()
		horie = artist.parse_page(horie_code)
		self.assertEqual('B', horie['info']['Bloodtype'])

if __name__ == '__main__':
	unittest.main()
