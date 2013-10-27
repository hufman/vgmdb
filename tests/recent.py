# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import recent

base = os.path.dirname(__file__)

class TestRecent(unittest.TestCase):
	def setUp(self):
		pass

	def test_albums(self):
		html = file(os.path.join(base, 'recent_albums.html'), 'r').read()
		data = recent.parse_page(html)
		up = data['updates']

		self.assertEqual(u'albums', data['section'])
		self.assertTrue(up[0]['deleted'])
		self.assertTrue(up[1]['deleted'])
		self.assertEqual(u'deleted', up[0]['edit'])
		self.assertEqual(u'Deleted/Inactive Album', up[0]['titles']['en'])
		self.assertEqual(u'rejected', up[1]['edit'])
		self.assertEqual(u'東方人 -TOHO BEAT-', up[1]['titles']['en'])
		self.assertEqual(u'new', up[5]['edit'])
		self.assertTrue(u'new' in up[5])
		self.assertFalse(u'catalog' in up[0])
		self.assertEqual(u'N/A', up[2]['catalog'])
		self.assertEqual(u'album/42368', up[2]['link'])
		self.assertEqual(u'2013-08-12', up[2]['release_date'])
		self.assertEqual(u'bonus', up[2]['type'])
		self.assertEqual(u'Enclosure/Promo', up[2]['category'])
		self.assertEqual(u'Efendija', up[0]['contributor']['name'])
		self.assertEqual(u'http://vgmdb.net/forums/member.php?u=10807', up[0]['contributor']['link'])
		self.assertEqual(u'2013-10-20T15:40', up[0]['date'])

	def test_media(self):
		html = file(os.path.join(base, 'recent_media.html'), 'r').read()
		data = recent.parse_page(html)
		up = data['updates']

		self.assertEqual(u'media', data['section'])
		self.assertEqual(u'new', up[0]['edit'])
		self.assertEqual(u'N/A', up[0]['catalog'])
		self.assertEqual(u'album/42368', up[0]['link'])
		self.assertTrue(up[5]['deleted'])
		self.assertEqual(u'SDEX-0057', up[3]['catalog'])
		self.assertEqual(u'album/14302', up[3]['link'])
		self.assertEqual(u'CD', up[3]['media_format'])
		self.assertEqual(u'Digital', up[-3]['media_format'])

		self.assertEqual(u'ritsukai', up[0]['contributor']['name'])
		self.assertEqual(u'http://vgmdb.net/forums/member.php?u=606', up[0]['contributor']['link'])
		self.assertEqual(u'2013-10-20T15:11', up[0]['date'])

	def test_tracklists(self):
		html = file(os.path.join(base, 'recent_tracklists.html'), 'r').read()
		data = recent.parse_page(html)
		up = data['updates']

		self.assertEqual(u'tracklists', data['section'])
		self.assertEqual(u'new', up[0]['edit'])
		self.assertEqual(u'N/A', up[0]['catalog'])
		self.assertEqual(u'album/42368', up[0]['link'])
		self.assertEqual(u'KDSD-00402', up[2]['catalog'])
		self.assertEqual(u'album/21317', up[2]['link'])
		self.assertEqual(u'bonus', up[0]['type'])
		self.assertEqual(u'Enclosure/Promo', up[0]['category'])
		self.assertEqual(u'game', up[2]['type'])
		self.assertEqual(u'Game', up[2]['category'])

		self.assertEqual(u'ritsukai', up[0]['contributor']['name'])
		self.assertEqual(u'http://vgmdb.net/forums/member.php?u=606', up[0]['contributor']['link'])
		self.assertEqual(u'2013-10-20T15:17', up[0]['date'])

	def test_scans(self):
		html = file(os.path.join(base, 'recent_scans.html'), 'r').read()
		data = recent.parse_page(html)
		up = data['updates']

		self.assertEqual(u'scans', data['section'])
		self.assertEqual(u'deleted', up[0]['edit'])
		self.assertEqual(u'AICL-2608', up[0]['catalog'])
		self.assertEqual(u'album/41585', up[0]['link'])
		self.assertEqual(u'added', up[-1]['edit'])
		self.assertEqual(u'VICL-60930', up[-1]['catalog'])
		self.assertEqual(u'album/42362', up[-1]['link'])

		self.assertEqual(u'Myrkul', up[0]['contributor']['name'])
		self.assertEqual(u'http://vgmdb.net/forums/member.php?u=65', up[0]['contributor']['link'])
		self.assertEqual(u'2013-10-20T15:43', up[0]['date'])
		self.assertEqual(u'boogiepop', up[-1]['contributor']['name'])
		self.assertEqual(u'http://vgmdb.net/forums/member.php?u=11507', up[-1]['contributor']['link'])
		self.assertEqual(u'2013-10-20T07:56', up[-1]['date'])

	def test_artists(self):
		html = file(os.path.join(base, 'recent_artists.html'), 'r').read()
		data = recent.parse_page(html)
		up = data['updates']

		self.assertEqual(u'artists', data['section'])
		self.assertEqual(u'YSCD-0023', up[0]['linked']['catalog'])
		self.assertEqual(u'album/29823', up[0]['linked']['link'])
		self.assertTrue(up[0]['deleted'])
		self.assertEqual(u'Stephen Erdody', up[-1]['names']['en'])
		self.assertEqual(u'artist/13131', up[-1]['link'])
		self.assertFalse(u'deleted' in up[-1])

		self.assertEqual(u'Efendija', up[-1]['contributor']['name'])
		self.assertEqual(u'http://vgmdb.net/forums/member.php?u=10807', up[-1]['contributor']['link'])
		self.assertEqual(u'2013-10-20T11:28', up[-1]['date'])

	def test_products(self):
		html = file(os.path.join(base, 'recent_products.html'), 'r').read()
		data = recent.parse_page(html)
		up = data['updates']

		self.assertEqual(u'products', data['section'])
		self.assertEqual(u'Album Linkup', up[0]['edit'])
		self.assertEqual(u'product/1143', up[0]['link'])
		self.assertEqual(u'Guild Wars 2', up[0]['titles']['en'])
		self.assertEqual(u'album/42352', up[0]['linked']['link'])
		self.assertEqual(u'N/A', up[0]['linked']['catalog'])

		self.assertEqual(u'Lashiec', up[0]['contributor']['name'])
		self.assertEqual(u'http://vgmdb.net/forums/member.php?u=13861', up[0]['contributor']['link'])
		self.assertEqual(u'2013-10-19T06:50', up[0]['date'])

	def test_labels(self):
		html = file(os.path.join(base, 'recent_labels.html'), 'r').read()
		data = recent.parse_page(html)
		up = data['updates']

		self.assertEqual(u'labels', data['section'])
		self.assertEqual(u'Album Linkup', up[0]['edit'])
		self.assertEqual(u'org/1022', up[0]['link'])
		self.assertEqual(u'Varèse Sarabande', up[0]['titles']['en'])
		self.assertEqual(u'album/42366', up[0]['linked']['link'])
		self.assertEqual(u'302 066 978 2', up[0]['linked']['catalog'])

		self.assertEqual(u'Efendija', up[0]['contributor']['name'])
		self.assertEqual(u'http://vgmdb.net/forums/member.php?u=10807', up[0]['contributor']['link'])
		self.assertEqual(u'2013-10-20T10:57', up[0]['date'])

		self.assertEqual(u'Label Page Edit', up[-3]['edit'])
		self.assertEqual(u'org/1227', up[-3]['link'])
		self.assertEqual(u'Klang-Gear', up[-3]['titles']['en'])
		self.assertTrue(up[-3]['new'])
		self.assertFalse('linked' in up[-3])

		self.assertEqual(u'Artist Linkup', up[-4]['edit'])
		self.assertEqual(u'org/1227', up[-4]['link'])
		self.assertEqual(u'Klang-Gear', up[-4]['titles']['en'])
		self.assertFalse(u'new' in up[-4])
		self.assertEqual(u'artist/14980', up[-4]['linked']['link'])
		self.assertEqual(u'Martin', up[-4]['linked']['names']['en'])

	def test_links(self):
		html = file(os.path.join(base, 'recent_links.html'), 'r').read()
		data = recent.parse_page(html)
		up = data['updates']

		self.assertEqual(u'links', data['section'])
		self.assertEqual(u'Album Link', up[0]['link_type'])
		self.assertEqual(u'album/42367', up[0]['link'])
		self.assertEqual(u'N/A', up[0]['catalog'])
		self.assertEqual(u'Crossfade Demo', up[0]['link_data']['title'])
		self.assertEqual(u'http://vgmdb.net/redirect/65785/www.amazon.co.jp/dp/B00FXMYERU/', up[1]['link_data']['link'])
		self.assertEqual(u'amazon.co.jp', up[1]['link_data']['title'])
		self.assertEqual(u'http://', up[3]['link_data']['link'])
		self.assertEqual(u'', up[3]['link_data']['title'])

		self.assertEqual(u'ritsukai', up[0]['contributor']['name'])
		self.assertEqual(u'http://vgmdb.net/forums/member.php?u=606', up[0]['contributor']['link'])
		self.assertEqual(u'2013-10-20T15:28', up[0]['date'])

		self.assertEqual(u'Purchase Link', up[1]['link_type'])
		self.assertEqual(u'album/41181', up[1]['link'])
		self.assertEqual(u'REC-092', up[1]['catalog'])

		self.assertEqual(u'Artist Link', up[6]['link_type'])
		self.assertEqual(u'artist/2277', up[6]['link'])
		self.assertEqual(u'Tainokobone', up[6]['names']['en'])

	def test_ratings(self):
		html = file(os.path.join(base, 'recent_ratings.html'), 'r').read()
		data = recent.parse_page(html)
		up = data['updates']

		self.assertEqual(u'ratings', data['section'])
		self.assertEqual(u'WM-0701~2', up[0]['catalog'])
		self.assertEqual(u'2013-04-24', up[0]['release_date'])
		self.assertEqual(u'album/38376', up[0]['link'])
		self.assertEqual(u'game', up[0]['type'])
		self.assertEqual(u'Game', up[0]['category'])
		self.assertEqual(u'Mahou Daisakusen Original Soundtrack', up[0]['titles']['en'])
		self.assertEqual(u'魔法大作戦 オリジナルサウンドトラック', up[0]['titles']['ja'])
		self.assertEqual(u'5', up[0]['rating'])

		self.assertEqual(u'Jodo Kast', up[0]['contributor']['name'])
		self.assertEqual(u'http://vgmdb.net/forums/member.php?u=1254', up[0]['contributor']['link'])
		self.assertEqual(u'2013-10-20T13:34', up[0]['date'])
