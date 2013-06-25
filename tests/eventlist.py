# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import eventlist

base = os.path.dirname(__file__)

class TestOrgList(unittest.TestCase):
	def setUp(self):
		pass

	def test_list(self):
		list_code = file(os.path.join(base, 'eventlist.html'), 'r').read()
		list = eventlist.parse_eventlist_page(list_code)

		self.assertEqual(16, len(list['events'].keys()))
		self.assertEqual(u"/event/92", list['events']['1998'][0]['link'])
		self.assertEqual(u"Tokyo Game Show 1998 Spring", list['events']['1998'][0]['names']['en'])
		self.assertEqual(u"コミックマーケット54", list['events']['1998'][1]['names']['ja'])
		self.assertEqual(u"C55", list['events']['1998'][2]['shortname'])
		self.assertEqual(u"1998-03-19", list['events']['1998'][0]['startdate'])
		self.assertEqual(u"1998-03-21", list['events']['1998'][0]['enddate'])
		self.assertEqual(u"2000-04-22", list['events']['2000'][0]['startdate'])
		self.assertEqual(u"2000-04-22", list['events']['2000'][0]['enddate'])
