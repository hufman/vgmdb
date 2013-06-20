from .commonutils import normalize_language_codes

import rdflib
from rdflib import Graph, Namespace, Literal, BNode, URIRef
from rdflib.namespace import NamespaceManager

from urlparse import urljoin
# fix for the base in turtle serialization
import rdflib.plugins.serializers.turtle as turtle
if not hasattr(turtle.TurtleSerializer, 'real_startDocument'):
	turtle.TurtleSerializer.real_startDocument = turtle.TurtleSerializer.startDocument
def turtle_patched_startDocument(self):
	self.real_startDocument()
	if self.base:
		self.write(self.indent() + '@base <%s> .\n'%self.base)
	if self._spacious:
		self.write('\n')

turtle.TurtleSerializer.startDocument = turtle_patched_startDocument

# Namespaces in use
from rdflib.namespace import RDF, XSD, DCTERMS, FOAF
BIO = Namespace("http://purl.org/vocab/bio/0.1/")
SCHEMA = Namespace("http://schema.org/")
MO = Namespace("http://purl.org/ontology/mo/")
EVENT = Namespace("http://purl.org/NET/c4dm/event.owl#")
TL = Namespace("http://purl.org/NET/c4dm/timeline.owl#")
ns = NamespaceManager(Graph())
namespaces = [(n.lower(), globals()[n]) for n in dict(globals()) if isinstance(globals()[n], Namespace)]
for name,namespace in namespaces:
	ns.bind(name, namespace)

def generate(config, type, data):
	global base
	base = config.BASE_URL
	graph = globals()['generate_%s'%type](config, data)
	graph.namespace_manager = ns
	return graph

def link(link):
	if len(link)>0 and link[0] == '/':
		link = link[1:]
	return urljoin(base, link)

def add_lang_names(g, subject, names, rel=[FOAF.name]):

	if isinstance(names, str) or isinstance(names, unicode):
		for r in rel:
			g.add((subject, r, Literal(names, lang='en')))
	else:
		for lang in sorted(names.keys()):
			for r in rel:
				code = normalize_language_codes(lang)
				g.add((subject, r, Literal(names[lang], lang=code)))

def add_discography(g, subject, albums, rel=[FOAF.made, SCHEMA.album], rev=[]):
	for album in albums:
		albumlink = URIRef(link(album['link'])+"#subject") if album.has_key('link') else BNode()
		g.add((albumlink, RDF.type, MO.Release))
		g.add((albumlink, RDF.type, SCHEMA.MusicAlbum))
		add_lang_names(g, albumlink, album['titles'], rel=[DCTERMS.title, SCHEMA.name])
		if album.has_key('date'):
			g.add((albumlink, DCTERMS.created, Literal(album['date'], datatype=XSD.date)))
			g.add((albumlink, SCHEMA.datePublished, Literal(album['date'], datatype=XSD.date)))
		if album.has_key('release_date'):
			g.add((albumlink, DCTERMS.created, Literal(album['release_date'], datatype=XSD.date)))
			g.add((albumlink, SCHEMA.datePublished, Literal(album['release_date'], datatype=XSD.date)))
		if album.has_key('catalog'):
			g.add((albumlink, MO.catalogue_number, Literal(album['catalog'])))
		if album.has_key('publisher'):
			pubdata = album['publisher']
			publisher = URIRef(link(pubdata['link'])+"#subject") if pubdata.has_key('link') else BNode()
			g.add((albumlink, MO.publisher, publisher))
			g.add((albumlink, SCHEMA.publisher, publisher))
			g.add((publisher, RDF.type, FOAF.Organization))
			g.add((publisher, RDF.type, SCHEMA.Organization))
			add_lang_names(g, publisher, pubdata['names'])
		for pred in rel:
			g.add((subject, pred, albumlink))
		for pred in rev:
			g.add((albumlink, pred, subject))

def generate_artist(config, data):
	if data.has_key('link'):
		doc = URIRef(link(data['link']))
		uri = link(data['link'])
	else:
		doc = BNode()
		uri = base
	g = Graph('IOMemory', doc)
	subject = URIRef(uri + "#subject")
	g.add((doc, FOAF.primaryTopic, subject))

	if data.has_key('members') and len(data['members'])>0:
		g.add((subject, RDF.type, FOAF.Organization))
		g.add((subject, RDF.type, SCHEMA.MusicGroup))
	else:
		g.add((subject, RDF.type, FOAF.Person))
		g.add((subject, RDF.type, SCHEMA.Person))
		g.add((subject, RDF.type, SCHEMA.MusicGroup))
	g.add((subject, FOAF.name, Literal(data['name'])))
	if data.has_key('birthdate'):
		birthinfo = URIRef(uri + "#birthinfo")
		g.add((birthinfo, RDF.type, BIO.birth))
		g.add((birthinfo, BIO.principal, subject))
		g.add((birthinfo, BIO.date, Literal(data['birthdate'], datatype=XSD.date)))
		if data.has_key('birthplace'):
			g.add((birthinfo, BIO.place, Literal(data['birthplace'])))
	if data.has_key('deathdate'):
		deathinfo = URIRef(uri + "#deathinfo")
		g.add((deathinfo, RDF.type, BIO.death))
		g.add((deathinfo, BIO.principal, subject))
		g.add((deathinfo, BIO.date, Literal(data['deathdate'], datatype=XSD.date)))
	if data.has_key('units'):
		for unit in data['units']:
			unitlink = URIRef(link(unit['link'])) if unit.has_key('link') else BNode()
			g.add((unitlink, RDF.type, FOAF.organization))
			g.add((unitlink, RDF.type, SCHEMA.MusicGroup))
			g.add((subject, MO.member_of, unitlink))
			g.add((unitlink, FOAF.member, subject))
			g.add((unitlink, MO.member, subject))
			g.add((unitlink, SCHEMA.musicGroupMember, subject))
			add_lang_names(g, unitlink, unit['names'], rel=[FOAF.name])
	if data.has_key('members'):
		for member in data['members']:
			memberlink = URIRef(link(member['link'])) if member.has_key('link') else BNode()
			g.add((memberlink, RDF.type, FOAF.person))
			g.add((subject, FOAF.member, memberlink))
			g.add((subject, MO.member, memberlink))
			g.add((subject, SCHEMA.musicGroupMember, memberlink))
			g.add((memberlink, MO.member_of, subject))
			add_lang_names(g, memberlink, member['names'], rel=[FOAF.name])
	if data.has_key('websites'):
		for websitetype, websites in data['websites'].items():
			for website in websites:
				g.add((subject, FOAF.page, URIRef(website['link'])))
	if data.has_key('twitter_names'):
		for name in data['twitter_names']:
			account = BNode()
			g.add((account, RDF.type, FOAF.OnlineChatAccount))
			g.add((account, FOAF.accountServiceHomepage, URIRef('http://www.twitter.com/')))
			g.add((account, FOAF.accountName, Literal(name)))
			g.add((subject, FOAF.account, account))
	if data.has_key('discography'):
		add_discography(g, subject, data['discography'], rel=[FOAF.made, SCHEMA.album], rev=[DCTERMS.creator, SCHEMA.byArtist])
	if data.has_key('featured_on'):
		add_discography(g, subject, data['featured_on'], rel=[], rev=[MO.tribute_to])

	return g

def generate_album(config, data):
	if data.has_key('link'):
		doc = URIRef(link(data['link']))
		uri = link(data['link'])
	else:
		doc = BNode()
		uri = base
	g = Graph('IOMemory', doc)
	subject = URIRef(uri + "#subject")
	musicalexpression = URIRef(uri + "#musicalexpression")
	performance = URIRef(uri + "#performance")
	musicalwork = URIRef(uri + "#musicalwork")
	composition = URIRef(uri + "#composition")
	lyrics = URIRef(uri + "#lyrics")
	g.add((doc, FOAF.primaryTopic, subject))

	g.add((subject, RDF.type, MO.Release))
	g.add((subject, RDF.type, SCHEMA.MusicAlbum))
	g.add((musicalexpression, RDF.type, MO.Signal))
	g.add((performance, RDF.type, MO.Performance))
	g.add((musicalwork, RDF.type, MO.MusicalWork))
	g.add((composition, RDF.type, MO.Composition))
	g.add((lyrics, RDF.type, MO.Lyrics))

	g.add((subject, MO.publication_of, musicalexpression))
	g.add((musicalexpression, MO.published_as, subject))
	g.add((musicalexpression, MO.records, performance))
	g.add((performance, MO.recorded_as, musicalexpression))
	g.add((performance, MO.performance_of, musicalwork))
	g.add((musicalwork, MO.performed_in, performance))
	g.add((musicalwork, MO.composed_in, composition))
	g.add((composition, MO.produced_work, musicalwork))
	g.add((musicalwork, MO.lyrics, lyrics))

	add_lang_names(g, subject, data['name'], rel=[DCTERMS.title, SCHEMA.name])
	if data.has_key('catalog'):
		g.add((subject, MO.catalogue_number, Literal(data['catalog'])))
	if data.has_key('release_date'):
		g.add((subject, DCTERMS.created, Literal(data['release_date'], datatype=XSD.date)))
		g.add((subject, SCHEMA.datePublished, Literal(data['release_date'], datatype=XSD.date)))
	if data.has_key('event'):
		event = URIRef(link(data['event']['link']))
		g.add((subject, MO.release, event))
		g.add((event, RDF.type, MO.Release))
		g.add((event, FOAF.name, Literal(data['event']['name'])))
	if data.has_key('publisher'):
		publisher = URIRef(link(data['publisher']['link'])+'#subject') if data['publisher'].has_key('link') else BNode()
		g.add((subject, MO.publisher, publisher))
		g.add((subject, SCHEMA.publisher, publisher))
		add_lang_names(g, publisher, data['publisher']['name'])


	for reprint in data['reprints']:
		reprinturi = URIRef(link(reprint['link']))
		g.add((subject, MO.other_release_of, reprinturi))
		g.add((reprinturi, RDF.type, MO.Release))
		g.add((reprinturi, MO.catalogue_number, Literal(reprint['catalog'])))
	if data.has_key('category'):
		g.add((subject, SCHEMA.genre, Literal(data['category'])))
	if data.has_key('media_format'):
		g.add((subject, MO.media_type, Literal(data['media_format'])))
	if data.has_key('rating'):
		rating = BNode()
		g.add((subject, SCHEMA.aggregateRating, rating))
		g.add((rating, RDF.type, SCHEMA.AggregateRating))
		g.add((rating, SCHEMA.ratingValue, Literal(str(data['rating']))))

	def add_people(g, subject, list, rel, rev):
		for persondata in list:
			person = URIRef(link(persondata['link'])+"#subject") if persondata.has_key('link') else BNode()
			g.add((person, RDF.type, FOAF.Person))
			add_lang_names(g, person, persondata['name'])
			for r in rel:
				g.add((subject, r, person))
			for r in rev:
				g.add((person, r, subject))
	if data.has_key('composers'):
		add_people(g, composition, data['composers'], rel=[MO.composer], rev=[FOAF.made])
	if data.has_key('performers'):
		add_people(g, performance, data['performers'], rel=[MO.performer], rev=[MO.performed])
	if data.has_key('lyricists'):
		add_people(g, lyrics, data['lyricists'], rel=[], rev=[FOAF.made])

	if data.has_key('products'):
		for productdata in data['products']:
			product = URIRef(link(productdata['link'])+"#subject") if productdata.has_key('link') else BNode()
			g.add((subject, SCHEMA.about, product))
			g.add((product, RDF.type, SCHEMA.CreativeWork))
			add_lang_names(g, product, productdata['name'])

	g.add((subject, MO.record_count, Literal(len(data['discs']), datatype=XSD.int)))
	index = 0
	for discdata in data['discs']:
		index += 1
		record = BNode()
		g.add((subject, MO.record, record))
		g.add((record, RDF.type, MO.Record))
		g.add((record, RDF.type, SCHEMA.MusicPlaylist))
		g.add((record, MO.record_name, Literal(index, datatype=XSD.int)))
		g.add((record, MO.track_count, Literal(len(discdata['tracks']), datatype=XSD.int)))
		g.add((record, SCHEMA.numTracks, Literal(len(discdata['tracks']), datatype=XSD.int)))
		trackno = 0
		for trackdata in discdata['tracks']:
			trackno += 1
			track = BNode()
			g.add((record, MO.track, track))
			g.add((record, SCHEMA.track, track))
			g.add((track, RDF.type, MO.Track))
			g.add((track, RDF.type, SCHEMA.MusicRecording))
			g.add((track, MO.track_number, Literal(trackno, datatype=XSD.int)))
			add_lang_names(g, track, trackdata['name'], rel=[SCHEMA.name, DCTERMS.title])
			if trackdata.has_key('track_length') and \
			   trackdata['track_length']:
				interval = "PT" + trackdata['track_length']
				g.add((track, SCHEMA.duration, Literal(interval, datatype=XSD.interval)))

	return g

def generate_product(config, data):
	if data.has_key('link'):
		doc = URIRef(link(data['link']))
		uri = link(data['link'])
	else:
		doc = BNode()
		uri = base
	g = Graph('IOMemory', doc)
	subject = URIRef(uri + "#subject")
	g.add((subject, RDF.type, SCHEMA.CreativeWork))
	g.add((subject, DCTERMS.title, Literal(data['name'])))
	g.add((subject, SCHEMA.name, Literal(data['name'])))
	if data.has_key('release_date'):
		g.add((subject, DCTERMS.created, Literal(data['release_date'], datatype=XSD.date)))
		g.add((subject, SCHEMA.datePublished, Literal(data['release_date'], datatype=XSD.date)))
	if data.has_key('franchises'):
		for franchisedata in data['franchises']:
			franchise = URIRef(link(franchisedata['link'])+"#subject") if franchisedata.has_key('link') else BNode()
			g.add((franchise, RDF.type, SCHEMA.CreativeWork))
			add_lang_names(g, franchise, franchisedata['names'], rel=[DCTERMS.title, SCHEMA.name])
	if data.has_key('titles'):
		for titledata in data['titles']:
			title = URIRef(link(titledata['link'])+"#subject") if titledata.has_key('link') else BNode()
			g.add((title, RDF.type, SCHEMA.CreativeWork))
			g.add((title, SCHEMA.datePublished, Literal(titledata['date'], datatype=XSD.date)))
			g.add((title, DCTERMS.created, Literal(titledata['date'], datatype=XSD.date)))
			add_lang_names(g, title, titledata['names'], rel=[DCTERMS.title, SCHEMA.name])
	add_discography(g, subject, data['albums'], rel=[], rev=[SCHEMA.about])

	return g

def generate_org(config, data):
	if data.has_key('link'):
		doc = URIRef(link(data['link']))
		uri = link(data['link'])
	else:
		doc = BNode()
		uri = base
	g = Graph('IOMemory', doc)
	subject = URIRef(uri + "#subject")
	g.add((subject, RDF.type, FOAF.Organization))
	g.add((subject, RDF.type, SCHEMA.Organization))
	g.add((subject, FOAF.name, Literal(data['name'])))
	g.add((subject, SCHEMA.name, Literal(data['name'])))
	if data.has_key('staff'):
		for staffdata in data['staff']:
			staff = URIRef(link(staffdata['link'])+"#subject") if staffdata.has_key('link') else BNode()
			g.add((subject, SCHEMA.member, staff))
			g.add((staff, FOAF.member, subject))
			g.add((staff, SCHEMA.memberOf, subject))
			g.add((staff, RDF.type, FOAF.Person))
			g.add((staff, RDF.type, SCHEMA.Person))
			g.add((staff, RDF.type, SCHEMA.MusicGroup))
			add_lang_names(g, staff, staffdata['names'], rel=[FOAF.name])
	if data.has_key('websites'):
		for websitetype, websites in data['websites'].items():
			for website in websites:
				g.add((subject, FOAF.page, URIRef(website['link'])))
	add_discography(g, subject, data['releases'], rel=[MO.published], rev=[MO.publisher])

	return g

def generate_event(config, data):
	if data.has_key('link'):
		doc = URIRef(link(data['link']))
		uri = link(data['link'])
	else:
		doc = BNode()
		uri = base
	g = Graph('IOMemory', doc)
	subject = URIRef(uri + "#subject")
	g.add((subject, RDF.type, MO.ReleaseEvent))
	g.add((subject, RDF.type, SCHEMA.MusicEvent))
	release_event = URIRef(uri + "#release_event")
	g.add((subject, EVENT.time, release_event))
	g.add((release_event, RDF.type, TL.Instant))
	g.add((release_event, TL.at, Literal(data['date'], datatype=XSD.date)))
	g.add((subject, SCHEMA.startDate, Literal(data['date'], datatype=XSD.date)))
	add_discography(g, subject, data['releases'], rel=[MO.release], rev=[])

	return g

def generate_albumlist(config, data):
	g = Graph('IOMemory', BNode())
	add_discography(g, None, data['albums'], rel=[], rev=[])
	return g
def generate_artistlist(config, data):
	g = Graph('IOMemory', BNode())
	for artist_data in data['artists']:
		artist = URIRef(link(artist_data['link'])+"#subject")
		g.add((artist, FOAF.name, Literal(artist_data['name'])))
		g.add((artist, RDF.type, SCHEMA.MusicGroup))
	return g
def generate_productlist(config, data):
	g = Graph('IOMemory', BNode())
	for product_data in data['products']:
		product = URIRef(link(product_data['link'])+"#subject")
		g.add((product, SCHEMA.name, Literal(product_data['name'])))
		g.add((product, DCTERMS.title, Literal(product_data['name'])))
		g.add((product, RDF.type, SCHEMA.CreativeWork))
	return g
