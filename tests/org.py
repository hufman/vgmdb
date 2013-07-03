# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import org

base = os.path.dirname(__file__)

class TestOrgs(unittest.TestCase):
	def setUp(self):
		pass

	def test_dogear(self):
		dogear_code = file(os.path.join(base, 'org_dogear.html'), 'r').read()
		dogear = org.parse_org_page(dogear_code)
		self.assertEqual(u"Dog Ear Records Co., Ltd.", dogear['name'])
		self.assertEqual(u"Label / Imprint", dogear['type'])
		self.assertEqual(u"Japan", dogear['region'])
		self.assertEqual(u"Nobuo Uematsu", dogear['staff'][0]['names']['en'])
		self.assertEqual(u"Miyu", dogear['staff'][1]['names']['en'])
		self.assertEqual(True, dogear['staff'][0]['owner'])
		self.assertEqual(2, len(dogear['staff']))
		self.assertEqual(u"No description available", dogear['description'])
		self.assertEqual(28, len(dogear['releases']))
		self.assertEqual(u"DERP-10001", dogear['releases'][0]['catalog'])
		self.assertEqual(u"/album/5343", dogear['releases'][0]['link'])
		self.assertEqual(u"Kalaycilar", dogear['releases'][2]['titles']['en'])
		self.assertEqual(u"2008-03-19", dogear['releases'][1]['date'])
		self.assertEqual(u"Publisher", dogear['releases'][1]['role'])
		self.assertEqual(True, dogear['releases'][19]['reprint'])
		self.assertEqual(u"http://vgmdb.net/db/assets/logos-medium/135-1246205463.gif", dogear['picture_small'])
		self.assertEqual(u"http://vgmdb.net/db/assets/logos/135-1246205463.gif", dogear['picture_full'])

	def test_vagrancy(self):
		vagrancy_code = file(os.path.join(base, 'org_vagrancy.html'), 'r').read()
		vagrancy = org.parse_org_page(vagrancy_code)
		self.assertEqual(u"VAGRANCY", vagrancy['name'])
		self.assertEqual(u"Akiko Shikata", vagrancy['staff'][0]['names']['en'])
		self.assertEqual(u"志方あきこ", vagrancy['staff'][0]['names']['ja'])
		self.assertEqual(u"2012-11", vagrancy['releases'][-2]['date'])
		self.assertEqual(u"Comic Market 67", vagrancy['releases'][4]['event']['name'])
		self.assertEqual(u"/event/15", vagrancy['releases'][4]['event']['link'])
