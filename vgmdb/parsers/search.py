import bs4
import os
import whoosh
import whoosh.analysis
import whoosh.fields
import whoosh.index
import whoosh.qparser

from itertools import chain
import logging
import random
import re
import sys
import time
import threading
import urllib.parse
import urllib.request
from . import utils
import vgmdb.settings

logger = logging.getLogger(__name__)

class AppURLOpener(urllib.request.FancyURLopener):
	version = "vgmdbapi/0.2 +https://vgmdb.info"
urllib.request._urlopener = AppURLOpener()

THREAD_LOCAL = threading.local()
SEARCH_INDEX = {}

class MultiFilter(whoosh.analysis.MultiFilter):
	# https://github.com/Sygil-Dev/whoosh-reloaded/pull/82/changes
	def __call__(self, tokens):
		t = next(tokens, None)
		if t is not None:
			selected_filter = self.filters.get(t.mode, self.default_filter)
			return selected_filter(chain([t], tokens))
		return []

def generate_search_index():
	import vgmdb.fetch
	logger.info("Starting to build search index")
	start = time.time()

	def index_path():
		if not vgmdb.settings.INDEX_PATH:
			raise Exception('CACHE_PATH or INDEX_PATH is not set')
		return vgmdb.settings.INDEX_PATH

	def create_index(name):
		analyzer = whoosh.analysis.StandardAnalyzer(minsize=3) | MultiFilter(
			index=whoosh.analysis.NgramFilter(minsize=3, maxsize=20),
			query=whoosh.analysis.PassFilter(),
		)
		schema = whoosh.fields.Schema(
			title=whoosh.fields.TEXT(sortable=True, analyzer=analyzer),
			document=whoosh.fields.STORED,
		)
		if not os.path.exists(index_path()):
			os.mkdir(index_path())
		storage = whoosh.filedb.filestore.FileStorage(index_path())
		return storage.create_index(schema, indexname=name)

	def open_index(name):
		index_complete = os.path.exists(os.path.join(index_path(), '%s.sealed' % (name,)))
		if index_complete and whoosh.index.exists_in(index_path(), indexname=name):
			storage = whoosh.filedb.filestore.FileStorage(index_path())
			return storage.open_index(indexname=name)
		else:
			return None

	def add_item_to_index(index, item):
		titles = []
		for title in item.get('titles', {}).values():
			titles.append(title)
		for name in item.get('names', {}).values():
			titles.append(name)
		if 'name_real' in item:
			titles.append(item['name_real'])
		index.add_document(title='\n'.join(titles), document=item)

	def add_items_to_index(index, items):
		for item in items:
			add_item_to_index(index, item)

	count = 0
	for list, section in (('albumlist', 'albums'), ('artistlist', 'artists'), ('productlist', 'products')):
		index = open_index(section)
		if index:
			SEARCH_INDEX[section] = index
		else:
			SEARCH_INDEX[section] = create_index(section)
			writer = SEARCH_INDEX[section].writer(limitmb=256)
			for letter in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
				id = letter + '1'
				while id:
					logger.info('... %s/%s' % (list, id))
					data = vgmdb.fetch.list(list, id, use_celery=False)
					add_items_to_index(writer, data[section])
					count += len(data)
					id = data['pagination'].get('link_next', '/').split('/')[-1]  # next page
			writer.commit()
			index_seal = os.path.join(index_path(), '%s.sealed' % (section,))
			open(index_seal, 'a').close()

	section = 'orgs'
	index = open_index(section)
	if index:
		SEARCH_INDEX[section] = index
	else:
		SEARCH_INDEX[section] = create_index(section)
		writer = SEARCH_INDEX[section].writer(limitmb=256)
		data = vgmdb.fetch.list('orglist', '', use_celery=False)
		for letter_data in data[section].values():
			add_items_to_index(writer, letter_data)
			count += len(letter_data)
		writer.commit()
		index_seal = os.path.join(index_path(), '%s.sealed' % (section,))
		open(index_seal, 'a').close()

	logger.info("Building index of %s items took %s" % (count, time.time() - start))

def fetch_url(query):
	return 'https://vgmdb.net/search?q=%s'%(urllib.parse.quote(query))

def fetch_page(query):
	if SEARCH_INDEX:
		return search_locally(query)

	url = fetch_url(query)
	page = utils.fetch_page(url, return_page_object=True)
	if page.geturl() == url:
		data = page.read()
		data = data.decode('utf-8', 'ignore')
		return data
	return masquerade(url, page)


def search_locally(query):
	def open_index_searchers():
		if hasattr(THREAD_LOCAL, 'searchers'):
			return THREAD_LOCAL.searchers
		searchers = {}
		for section, index in SEARCH_INDEX.items():
			searchers[section] = index.searcher()
		THREAD_LOCAL.searchers = searchers
		return searchers
		
	sections = {'albums':[],
	            'artists':[],
	            'orgs':[],
	            'products':[]}

	start = time.time()
	for section, searcher in open_index_searchers().items():
		# check if this section has this set of keywords
		qp = whoosh.qparser.SimpleParser('title', searcher.ixreader.schema)
		q = qp.parse(query)
		results = searcher.search(q, sortedby='title', limit=2000)
		for hit in results:
			sections[section].append(hit['document'])
	logger.debug("Searching for %s locally took %s" % (query, time.time() - start,))

	fake = {
	    "meta":{},
	    "query":query,
	    "results":sections,
	    "sections":sorted(sections.keys())
	}
	return fake


def masquerade(url, page):
	import importlib
	sections = {'albums':[],
	            'artists':[],
	            'orgs':[],
	            'products':[]}
	parsed = urllib.parse.urlparse(page.geturl())
	data = page.read()
	data = data.decode('utf-8', 'ignore')
	for section in sections.keys():
		type = section[:-1]
		prefix = '/%s/'%type
		if parsed.path[:len(prefix)] == prefix:
			module = importlib.import_module('.parsers.'+type, 'vgmdb')
			parse_page = getattr(module, "parse_page")
			info = parse_page(data)
			info['link'] = parsed.path[1:]
			fake = generate_fakeresult(info)
			sections[section].append(fake)
	orig_parsed = urllib.parse.urlparse(url)
	query = urllib.parse.parse_qs(orig_parsed.query)['q'][0]
	query = urllib.parse.unquote(query)
	fake = {
	    "meta":{},
	    "query":query,
	    "results":sections,
	    "sections":sorted(sections.keys())
	}
	return fake

def generate_fakeresult(info):
	fake = {'link':info['link']}
	copy_keys = ['aliases', 'category', 'catalog', 'media_format', 'release_date']
	for key in copy_keys:
		if key in info:
			fake[key] = info[key]
	if 'names' in info:
		fake['titles'] = info['names']
	if not 'names' in info:
		if 'name' in info:
			fake['names'] = {}
			fake['names']['en'] = info['name']
		if 'name_real' in info:
			fake['names']['ja'] = info['name_real']
			fake['aliases'] = [info['name_real']]
			fake['names']['ja-latn'] = info['name']
		if 'name_trans' in info:
			fake['names']['ja-latn'] = info['name_trans']
	return fake


def parse_page(html_source):
	if isinstance(html_source, dict):
		# fake result generated by redirect
		return html_source
	section_types = {
		'albumresults': 'albums',
		'artistresults': 'artists',
		'orgresults': 'orgs',
		'productresults': 'products'
	}

	search_info = {}
	search_info['results'] = {}
	search_info['sections'] = []
	html_source = utils.fix_invalid_table(html_source)
	soup = bs4.BeautifulSoup(html_source, features="lxml")
	soup_innermain = soup.find(id='innermain')
	if soup_innermain == None:
		return None	# info not found

	# parse the section
	for soup_section in soup_innermain.div.find_all('div'):
		if not soup_section.has_attr('id'):
			continue
		section_type = soup_section['id']
		if section_type not in section_types:
			continue
		section_type = section_types[section_type]
		parse_item = globals()['_parse_'+section_type[:-1]]
		search_info['sections'].append(section_type)
		search_info['results'][section_type] = _parse_list(soup_section, parse_item)

	# parse the query
	match = re.search(r'\$\("#simplesearch"\).val\("(.*)"\);', html_source)
	if match:
		search_info['query'] = match.groups(1)[0].replace("\\'","'")

	# parse page meat
	search_info['meta'] = {}
	
	return search_info

def _parse_list(soup_section, item_parser):
	list = []
	for soup_row in soup_section.find_all('tr', recursive=True)[1:]:
		item = item_parser(soup_row)
		if item:
			list.append(item)
	return list

def _parse_listitem(soup_row):
	soup_cells = soup_row.find_all('td', recursive=False)
	soup_link = soup_cells[0].a
	names = utils.parse_names(soup_link)
	link = soup_link['href']
	link = utils.trim_absolute(link)
	info = {'link':link,
	        'names':names
	}
	# aliases could be aliases or name_trans, dunno
	soup_aliases = soup_cells[0].span
	if soup_aliases:
		aliases = utils.parse_string(soup_aliases)
		aliases = [piece.strip() for piece in aliases.split('/') if piece.strip()!='']
		info['aliases'] = aliases
	return info

def _parse_album(soup_row):
	soup_cells = soup_row.find_all('td', recursive=False)
	catalog = soup_cells[0].span.string
	special = soup_cells[1].img
	soup_album = soup_cells[2]
	link = soup_album.a['href']
	link = utils.trim_absolute(link)
	names = utils.parse_names(soup_album.a)
	date = utils.parse_date_time(soup_cells[3].string)
	media_format = soup_cells[4].string
	info = {'link':link,
	        'catalog':catalog,
	        'titles':names,
	        'release_date':date,
	        'media_format':media_format
	}
	typelist = [s.replace('album-','') for s in soup_album.a['class'] if 'album-' in s]
	info['category'] = utils.type_category(typelist[0])
	return info
_parse_artist = _parse_listitem
_parse_org = _parse_listitem
def _parse_product(soup_row):
	soup_cells = soup_row.find_all('td', recursive=False)
	soup_link = soup_cells[0].a
	names = utils.parse_names(soup_link.span.span)
	link = soup_link['href']
	link = utils.trim_absolute(link)
	info = {'link':link}
	# aliases could be aliases or name_trans, dunno
	soup_color = soup_cells[0].span
	if soup_color:
		info['type'] = utils.product_color_type(soup_color)
		soup_names = soup_color.span
		if soup_names:
			names = utils.parse_names(soup_color)
			info['names'] = names
	return info
