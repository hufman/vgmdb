# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import event

base = os.path.dirname(__file__)

class TestEvents(unittest.TestCase):
	def setUp(self):
		pass

	def test_m3(self):
		m3_code = file(os.path.join(base, 'event_m3.html'), 'r').read()
		m3 = event.parse_event_page(m3_code)
		self.assertEqual(u'M3-2012 Fall', m3['name'])
		self.assertEqual(u'2012-10-27', m3['startdate'])
		self.assertEqual(u'2012-10-27', m3['enddate'])
		self.assertEqual(u'New Release', m3['releases'][0]['release_type'])
		self.assertEqual(u'works', m3['releases'][0]['album_type'])
		self.assertEqual(u'DVSP-0084', m3['releases'][1]['catalog'])
		self.assertEqual(u'AD:TECHNO', m3['releases'][2]['titles']['en'])
		self.assertEqual(u'Clinochlore', m3['releases'][0]['publisher']['names']['en'])
		self.assertEqual(u'Diverse System', m3['releases'][1]['publisher']['names']['en'])
		self.assertEqual(u'/org/331', m3['releases'][1]['publisher']['link'])
		self.assertEqual(u'2012-10-28', m3['releases'][5]['release_date'])
		self.assertEqual(39, len(m3['releases']))

	def test_cm54(self):
		cm54_code = file(os.path.join(base, 'event_cm54.html'), 'r').read()
		cm54 = event.parse_event_page(cm54_code)
		self.assertEqual(u'Comic Market 54', cm54['name'])
		self.assertEqual(u'1998-08-13', cm54['startdate'])
		self.assertEqual(u'1998-08-15', cm54['enddate'])
		self.assertEqual(6, len(cm54['releases']))
