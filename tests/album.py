# -*- coding: UTF-8 -*-
import os
import unittest

from vgmdb.parsers import album

base = os.path.dirname(__file__)

class TestAlbums(unittest.TestCase):
	def setUp(self):
		pass

	def test_ff8(self):
		ff8_code = file(os.path.join(base, 'album_ff8.html'), 'r').read()
		ff8 = album.parse_page(ff8_code)

		self.assertEqual(u"FITHOS LUSEC WECOS VINOSEC: FINAL FANTASY VIII [Limited Edition]", ff8['names']['en'])
		self.assertEqual(u"FITHOS LUSEC WECOS VINOSEC: FINAL FANTASY VIII [Limited Edition]", ff8['names']['ja'])
		self.assertEqual(u"SSCX-10037", ff8['catalog'])
		self.assertEqual(u"SQEX-10025", ff8['reprints'][2]['catalog'])
		self.assertEqual(u"1999-11-20", ff8['release_date'])
		self.assertEqual(u"Commercial, Limited Edition", ff8['publish_format'])
		self.assertEqual(2854.0, ff8['release_price']['price'])
		self.assertEqual(u"JPY", ff8['release_price']['currency'])
		self.assertEqual(u"CD", ff8['media_format'])
		self.assertEqual(u"Arrangement", ff8['classification'])
		self.assertEqual(u"DigiCube", ff8['publisher']['names']['en'])
		self.assertEqual(u"株式会社デジキューブ", ff8['publisher']['names']['ja'])
		self.assertEqual(u"org/54", ff8['publisher']['link'])
		self.assertEqual(u"DigiCube", ff8['organizations'][0]['names']['en'])
		self.assertEqual(u"株式会社デジキューブ", ff8['organizations'][0]['names']['ja'])
		self.assertEqual(u"org/54", ff8['organizations'][0]['link'])
		self.assertEqual(u"publisher", ff8['organizations'][0]['role'])
		self.assertEqual(u"SME Intermedia", ff8['distributor']['names']['en'])
		self.assertEqual(u"org/186", ff8['distributor']['link'])
		self.assertEqual(u"SME Intermedia", ff8['organizations'][1]['names']['en'])
		self.assertEqual(u"org/186", ff8['organizations'][1]['link'])
		self.assertEqual(u"distributor", ff8['organizations'][1]['role'])
		self.assertEqual(u"Nobuo Uematsu", ff8['composers'][0]['names']['en'])
		self.assertEqual(u"Shiro Hamaguchi", ff8['arrangers'][0]['names']['en'])
		self.assertEqual(u"artist/125", ff8['arrangers'][0]['link'])
		self.assertEqual(u"Faye Wong", ff8['performers'][0]['names']['en'])
		self.assertEqual(u"Kazushige Nojima", ff8['lyricists'][0]['names']['en'])
		self.assertEqual(1, len(ff8['discs']))
		self.assertEqual(13, len(ff8['discs'][0]['tracks']))
		self.assertEqual(u"3:09", ff8['discs'][0]['tracks'][0]['track_length'])
		self.assertEqual(u"Liberi Fatali", ff8['discs'][0]['tracks'][0]['names']['English'])
		self.assertEqual(u"64:16", ff8['discs'][0]['disc_length'])
		self.assertEqual(4.46, ff8['rating'])
		self.assertEqual(50, ff8['votes'])
		self.assertEqual(u"Game", ff8['category'])
		self.assertEqual(u"Final Fantasy VIII", ff8['products'][0]['names']['en'])
		self.assertEqual(u"ファイナルファンタジーVIII", ff8['products'][0]['names']['ja'])
		self.assertEqual(u"product/189", ff8['products'][0]['link'])
		self.assertEqual(u"Sony PlayStation", ff8['platforms'][0])
		self.assertEqual(u"RPGFan's Review", ff8['websites']['Review'][0]['name'])
		self.assertEqual(u"Booklet Front", ff8['covers'][0]['name'])
		self.assertEqual(u"http://medium.media.vgm.io/albums/97/79/79-1264618929.png", ff8['picture_small'])
		self.assertEqual(u"http://media.vgm.io/albums/97/79/79-1264618929.png", ff8['picture_full'])
		self.assertEqual(u"http://thumb.media.vgm.io/albums/97/79/79-1264618929.png", ff8['covers'][0]['thumb'])
		self.assertEqual(u"http://medium.media.vgm.io/albums/97/79/79-1264618929.png", ff8['covers'][0]['medium'])
		self.assertEqual(u"http://media.vgm.io/albums/97/79/79-1264618929.png", ff8['covers'][0]['full'])
		self.assertEqual(u"EYES ON ME: featured in FINAL FANTASY VIII", ff8['related'][0]['names']['en'])
		self.assertEqual(u"PRT-8429", ff8['related'][0]['catalog'])
		self.assertEqual(u"bonus", ff8['related'][0]['type'])
		self.assertEqual(u"2006-08-03T01:33", ff8['meta']['added_date'])
		self.assertEqual(u"2015-01-06T17:23", ff8['meta']['edited_date'])
		self.assertEqual(9382, ff8['meta']['visitors'])
		self.assertEqual(24, ff8['meta']['freedb'])

	def test_arciel(self):
		arciel_code = file(os.path.join(base, 'album_arciel.html'), 'r').read()
		arciel = album.parse_page(arciel_code)

		self.assertEqual(u"Ar tonelico III Image CD Utau Oka~Ar=Ciel Ar=Dor~", arciel['names']['en'])
		self.assertEqual(u"アルトネリコ3 イメージCD 謳う丘～Ar=Ciel Ar=Dor～", arciel['names']['ja'])
		self.assertEqual(u"FCCM-0328", arciel['catalog'])
		self.assertEqual(u"謳う丘 ～Ar=Ciel Ar=Dor～", arciel['discs'][0]['tracks'][0]['names']['Japanese'])
		self.assertEqual(u"CD Japan", arciel['stores'][1]['name'])
		self.assertTrue(u"Akiko Shikata" in arciel['notes'])

	def test_at3(self):
		at3_code = file(os.path.join(base, 'album_at3.html'), 'r').read()
		at3 = album.parse_page(at3_code)
		self.assertEqual(2, len(at3['discs']))
		self.assertEqual(u'EXEC_FLIP_FUSIONSPHERE/.', at3['discs'][1]['tracks'][3]['names']['Romaji'])
	def test_viking(self):
		viking_code = file(os.path.join(base, 'album_viking.html'), 'r').read()
		viking = album.parse_page(viking_code)

		self.assertEqual('Free', viking['release_price']['price'])
		self.assertEqual(1188, viking['meta']['visitors'])
		self.assertEqual('NES (Famicom)', viking['platforms'][0])
		self.assertEqual('Duty Cycle Generator', viking['publisher']['names']['en'])

	def test_blooming(self):
		blooming_code = file(os.path.join(base, 'album_blooming.html'), 'r').read()
		blooming = album.parse_page(blooming_code)

		self.assertEqual('KMCA-65', blooming['related'][0]['catalog'])
		self.assertEqual('2000-10-04', blooming['related'][1]['date'])
		self.assertEqual('CD Japan (OOP)', blooming['stores'][1]['name'])

	def test_istoria(self):
		istoria_code = file(os.path.join(base, 'album_istoria.html'), 'r').read()
		istoria = album.parse_page(istoria_code)

		self.assertEqual(u'Tomoki Yamada', istoria['performers'][-1]['names']['en'])
		self.assertEqual(u'Vocal, Original Work', istoria['classification'])
		self.assertEqual(u'Comic Market 81', istoria['release_events'][0]['name'])
		self.assertEqual(u'C81', istoria['release_events'][0]['shortname'])
		self.assertEqual(u'event/146', istoria['release_events'][0]['link'])

	def test_zwei(self):
		zwei_code = file(os.path.join(base, 'album_zwei.html'), 'r').read()
		zwei = album.parse_page(zwei_code)
		self.assertEqual(5, len(zwei['composers']))
		self.assertEqual(u'Falcom Sound Team jdk', zwei['composers'][0]['names']['en'])
		self.assertEqual('artist/293', zwei['composers'][0]['link'])
		self.assertEqual(u'Atsushi Shirakawa', zwei['composers'][1]['names']['en'])

	def test_bootleg(self):
		bootleg_code = file(os.path.join(base, 'album_bootleg.html'), 'r').read()
		bootleg = album.parse_page(bootleg_code)
		self.assertEqual('GAME-119', bootleg['catalog'])
		self.assertEqual(True, bootleg['bootleg'])
		self.assertEqual('album/722', bootleg['bootleg_of']['link'])
		self.assertEqual('N30D-021', bootleg['bootleg_of']['catalog'])

	def test_brokennight(self):
		# has a linked release
		night_code = file(os.path.join(base, 'album_brokennight.html'), 'r').read()
		night = album.parse_page(night_code)
		self.assertEqual('DFCL-2101~2', night['catalog'])
		self.assertEqual('Sony PlayStation Vita', night['platforms'][0])
		self.assertEqual('release/3993', night['products'][0]['link'])
		self.assertEqual('Unknown', night['discs'][1]['tracks'][0]['track_length'])
		self.assertEqual('Unknown', night['discs'][1]['disc_length'])

	def test_touhou(self):
		# has multiple releases
		touhou_code = file(os.path.join(base, 'album_touhou.html'), 'r').read()
		touhou = album.parse_page(touhou_code)
		self.assertEqual('IO-0212', touhou['catalog'])
		self.assertEqual(2, len(touhou['release_events']))
		self.assertEqual('event/155', touhou['release_events'][0]['link'])
		self.assertEqual('Touhou Kouroumu 8', touhou['release_events'][0]['shortname'])
		self.assertEqual('Touhou Kouroumu 8', touhou['release_events'][0]['name'])
		self.assertEqual('event/152', touhou['release_events'][1]['link'])
		self.assertEqual('M3-30', touhou['release_events'][1]['shortname'])
		self.assertEqual('M3-2012 Fall', touhou['release_events'][1]['name'])

	def test_million(self):
		# has multiple publishers
		million_code = file(os.path.join(base, 'album_million.html'), 'r').read()
		million = album.parse_page(million_code)
		self.assertEqual(2, len(million['organizations']))
		self.assertEqual(u'Key Sounds Label', million['publisher']['names']['en'])
		self.assertEqual(u'Key Sounds Label', million['publisher']['names']['ja'])
		self.assertEqual(u'org/1', million['publisher']['link'])
		self.assertEqual(u'Key Sounds Label', million['organizations'][0]['names']['en'])
		self.assertEqual(u'Key Sounds Label', million['organizations'][0]['names']['ja'])
		self.assertEqual(u'org/1', million['organizations'][0]['link'])
		self.assertEqual(u'publisher', million['organizations'][0]['role'])
		self.assertEqual(u"Visual Art's", million['organizations'][1]['names']['en'])
		self.assertEqual(u'株式会社ビジュアルアーツ', million['organizations'][1]['names']['ja'])
		self.assertEqual(u'org/429', million['organizations'][1]['link'])
		self.assertEqual(u'publisher', million['organizations'][1]['role'])

	def test_got(self):
		# has unlinked publisher and a distributor
		got_code = file(os.path.join(base, 'album_got.html'), 'r').read()
		got = album.parse_page(got_code)
		self.assertEqual(2, len(got['organizations']))
		self.assertEqual(u'Game Audio Factory', got['publisher']['names']['en'])
		self.assertNotIn(u'link', got['publisher'])
		self.assertEqual(u'Bandcamp', got['distributor']['names']['en'])
		self.assertEqual(u'org/965', got['distributor']['link'])
if __name__ == '__main__':
	unittest.main()
