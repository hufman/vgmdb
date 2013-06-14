# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb import album

base = os.path.dirname(__file__)

class TestAlbums(unittest.TestCase):
	def setUp(self):
		pass

	def test_ff8(self):
		ff8_code = file(os.path.join(base, 'album_ff8.html'), 'r').read()
		ff8 = album.parse_album_page(ff8_code)

		self.assertEqual(u"FITHOS LUSEC WECOS VINOSEC: FINAL FANTASY VIII", ff8['name']['en'])
		self.assertEqual(u"FITHOS LUSEC WECOS VINOSEC: FINAL FANTASY VIII", ff8['name']['ja'])
		self.assertEqual(u"SSCX-10037", ff8['catalog'])
		self.assertEqual(u"SQEX-10025", ff8['reprints'][2]['catalog'])
		self.assertEqual(u"1999-11-20", ff8['release_date'])
		self.assertEqual(u"Commercial", ff8['publish_format'])
		self.assertEqual(2854.0, ff8['release_price']['price'])
		self.assertEqual(u"JPY", ff8['release_price']['currency'])
		self.assertEqual(u"CD", ff8['media_format'])
		self.assertEqual(u"Arrangement", ff8['classification'])
		self.assertEqual(u"DigiCube", ff8['publisher']['name']['en'])
		self.assertEqual(u"株式会社デジキューブ", ff8['publisher']['name']['ja'])
		self.assertEqual(u"/org/54", ff8['publisher']['link'])
		self.assertEqual(u"SME Intermedia", ff8['distributor']['name']['en'])
		self.assertEqual(u"/org/186", ff8['distributor']['link'])
		self.assertEqual(u"Nobuo Uematsu", ff8['composers'][0]['name']['en'])
		self.assertEqual(u"Shiro Hamaguchi", ff8['arrangers'][0]['name']['en'])
		self.assertEqual(u"/artist/125", ff8['arrangers'][0]['link'])
		self.assertEqual(u"Faye Wong", ff8['performers'][0]['name']['en'])
		self.assertEqual(u"Kazushige Nojima", ff8['lyricists'][0]['name']['en'])
		self.assertEqual(1, len(ff8['discs']))
		self.assertEqual(13, len(ff8['discs'][0]['tracks']))
		self.assertEqual(u"3:09", ff8['discs'][0]['tracks'][0]['track_length'])
		self.assertEqual(u"Liberi Fatali", ff8['discs'][0]['tracks'][0]['name']['English'])
		self.assertEqual(u"64:16", ff8['discs'][0]['disc_length'])
		self.assertEqual(4.47, ff8['rating'])
		self.assertEqual(43, ff8['votes'])
		self.assertEqual(u"Game", ff8['category'])
		self.assertEqual(u"Final Fantasy VIII", ff8['products'][0]['name']['en'])
		self.assertEqual(u"ファイナルファンタジーVIII", ff8['products'][0]['name']['ja'])
		self.assertEqual(u"/product/189", ff8['products'][0]['link'])
		self.assertEqual(u"PC", ff8['platforms'][0])
		self.assertEqual(u"RPGFan's Review", ff8['websites']['Review'][0]['name'])
		self.assertEqual(u"Front", ff8['covers'][0]['name'])
		self.assertEqual(u"/db/assets/covers-thumb/7/9/79-1190730814.jpg", ff8['covers'][0]['thumb'])
		self.assertEqual(u"/db/assets/covers-medium/7/9/79-1190730814.jpg", ff8['covers'][0]['medium'])
		self.assertEqual(u"/db/assets/covers/7/9/79-1190730814.jpg", ff8['covers'][0]['full'])
		self.assertEqual(u"EYES ON ME: featured in FINAL FANTASY VIII", ff8['related'][0]['name']['en'])
		self.assertEqual(u"2006-08-03T01:33", ff8['meta']['added_date'])
		self.assertEqual(u"2012-08-12T19:55", ff8['meta']['edited_date'])
		self.assertEqual(5484, ff8['meta']['visitors'])
		self.assertEqual(16, ff8['meta']['freedb'])

	def test_arciel(self):
		arciel_code = file(os.path.join(base, 'album_arciel.html'), 'r').read()
		arciel = album.parse_album_page(arciel_code)

		self.assertEqual(u"Ar tonelico III Image CD Utau Oka~Ar=Ciel Ar=Dor~", arciel['name']['en'])
		self.assertEqual(u"アルトネリコ3 イメージCD 謳う丘～Ar=Ciel Ar=Dor～", arciel['name']['ja'])
		self.assertEqual(u"FCCM-0328", arciel['catalog'])
		self.assertEqual(u"謳う丘 ～Ar=Ciel Ar=Dor～", arciel['discs'][0]['tracks'][0]['name']['Japanese'])
		self.assertEqual(u"YesAsia", arciel['stores'][1]['name'])
		self.assertTrue(u"Akiko Shikata" in arciel['notes'])

	def test_at3(self):
		at3_code = file(os.path.join(base, 'album_at3.html'), 'r').read()
		at3 = album.parse_album_page(at3_code)
		self.assertEqual(2, len(at3['discs']))
		self.assertEqual(u'EXEC_FLIP_FUSIONSPHERE/.', at3['discs'][1]['tracks'][3]['name']['Romaji'])
	def test_viking(self):
		viking_code = file(os.path.join(base, 'album_viking.html'), 'r').read()
		viking = album.parse_album_page(viking_code)

		self.assertEqual('Free', viking['release_price']['price'])
		self.assertEqual(500, viking['meta']['visitors'])
		self.assertEqual('NES (Famicom)', viking['platforms'][0])
		self.assertEqual('Duty Cycle Generator', viking['publisher']['name'])

	def test_blooming(self):
		blooming_code = file(os.path.join(base, 'album_blooming.html'), 'r').read()
		blooming = album.parse_album_page(blooming_code)

		self.assertEqual('KMCA-65', blooming['related'][0]['catalog'])
		self.assertEqual('2000-10-04', blooming['related'][1]['date'])
		self.assertEqual('CD Japan (OOP)', blooming['stores'][0]['name'])

	def test_istoria(self):
		istoria_code = file(os.path.join(base, 'album_istoria.html'), 'r').read()
		istoria = album.parse_album_page(istoria_code)

		self.assertEqual(u'Tomoki Yamada', istoria['performers'][-1]['name']['en'])
		self.assertEqual(u'Vocal, Original Work', istoria['classification'])
		self.assertEqual(u'Comic Market 81', istoria['event']['name'])
		self.assertEqual(u'C81', istoria['event']['shortname'])
		self.assertEqual(u'/event/146', istoria['event']['link'])

