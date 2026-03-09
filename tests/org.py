# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import org

base = os.path.dirname(__file__)

class TestOrgs(unittest.TestCase):
	def setUp(self):
		pass

	def test_dogear(self):
		dogear_code = file(os.path.join(base, 'org_dogear.html'), 'r').read()
		dogear = org.parse_page(dogear_code)
		self.assertEqual(u"Dog Ear Records Co., Ltd.", dogear['name'])
		self.assertEqual(u"Media / Entertainment Company", dogear['type'])
		self.assertEqual(u"Japan", dogear['region'])
		self.assertEqual(u"Nobuo Uematsu", dogear['staff'][1]['names']['en'])
		self.assertEqual(u"Hiroki Ogawa", dogear['staff'][0]['names']['en'])
		self.assertEqual(True, dogear['staff'][0]['owner'])
		self.assertEqual(7, len(dogear['staff']))
		self.assertEqual(u"", dogear['description'])
		self.assertEqual(30, len(dogear['releases']))
		self.assertEqual(u"DERP-10012~4", dogear['releases'][0]['catalog'])
		self.assertEqual(u"album/22773", dogear['releases'][0]['link'])
		self.assertEqual(u"THE LAST STORY Original Soundtrack", dogear['releases'][0]['titles']['en'])
		self.assertEqual(u"2011-02-23", dogear['releases'][0]['date'])
		self.assertEqual(u"Publisher", dogear['releases'][0]['role'])
		self.assertEqual(u"https://thumb-media.vgm.io/orgs/53/135/135-1246205463.gif", dogear['picture_small'])
		self.assertEqual(u"https://media.vgm.io/orgs/53/135/135-1246205463.gif", dogear['picture_full'])

	def test_vagrancy(self):
		vagrancy_code = file(os.path.join(base, 'org_vagrancy.html'), 'r').read()
		vagrancy = org.parse_page(vagrancy_code)
		self.assertEqual(u"VAGRANCY", vagrancy['name'])
		self.assertEqual(u"Akiko Shikata", vagrancy['staff'][0]['names']['en'])
		self.assertEqual(u"志方あきこ", vagrancy['staff'][0]['names']['ja'])
		self.assertEqual(u"2012-11", vagrancy['releases'][8]['date'])
		self.assertEqual(u"Comic Market 74", vagrancy['releases'][0]['event']['name'])
		self.assertEqual(u"C74", vagrancy['releases'][0]['event']['shortname'])
		self.assertEqual(u"event/29", vagrancy['releases'][0]['event']['link'])

	def test_vagrancy_logged_in(self):
		vagrancy_code = file(os.path.join(base, 'org_vagrancy_logged_in.html'), 'r').read()
		vagrancy = org.parse_page(vagrancy_code)
		self.assertEqual(u"Doujin Group / Independent", vagrancy['type'])
		self.assertEqual(30, len(vagrancy['releases']))

if __name__ == '__main__':
	unittest.main()
