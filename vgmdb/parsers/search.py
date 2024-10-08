from bloom_filter import BloomFilter
import bs4

from itertools import combinations
import logging
import random
import re
import sys
import time
from . import utils
import urllib

logger = logging.getLogger(__name__)

class AppURLOpener(urllib.FancyURLopener):
	version = "vgmdbapi/0.2 +https://vgmdb.info"
urllib._urlopener = AppURLOpener()

BLOOM_INDEX = {}
SEARCH_INDEX = {}

def generate_search_index():
	import vgmdb.fetch
	logger.info("Starting to build search index")
	start = time.time()

	def add_keyword(bloom_filter, keyword):
		keyword = keyword.lower()
		length = len(keyword)
		for start, end in combinations(range(length), r=2):
			if start + 2 >= end:  # a string of length <=3
				continue
			if start + 15 < end:  # a string of length >= 16
				continue
			bloom_filter.add(keyword[start:end+1].encode('utf-8'))
	def add_keywords(bloom_filter, phrase):
		for piece in phrase.split():
			add_keyword(bloom_filter, piece)
	def add_items(bloom_filter, items):
		for item in items:
			for title in set(item.get('titles', {}).values()):
				add_keywords(bloom_filter, title)
			for name in set(item.get('names', {}).values()):
				add_keywords(bloom_filter, name)
			if 'name_real' in item:
				add_keywords(bloom_filter, item['name_real'])

	for list, section in (('albumlist', 'albums'), ('artistlist', 'artists'), ('productlist', 'products')):
		bloom_elements = 100000000 if section == 'albums' else 1000000
		BLOOM_INDEX[section] = BloomFilter(max_elements=bloom_elements, error_rate=0.1)
		SEARCH_INDEX[section] = []
		for letter in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
			id = letter + '1'
			while id:
				logger.info('... %s/%s' % (list, id))
				data = vgmdb.fetch.list(list, id, use_celery=False)
				SEARCH_INDEX[section].extend(data[section])
				add_items(BLOOM_INDEX[section], data[section])
				id = data['pagination'].get('link_next', '/').split('/')[-1]  # next page

	data = vgmdb.fetch.list('orglist', '', use_celery=False)
	SEARCH_INDEX['orgs'] = []
	for letter_data in data['orgs'].values():
		SEARCH_INDEX['orgs'].extend(letter_data)
	# insert into bloom filter
	BLOOM_INDEX['orgs'] = BloomFilter(max_elements=100000, error_rate=0.1)
	add_items(BLOOM_INDEX['orgs'], SEARCH_INDEX['orgs'])

	count = 0
	for section_data in SEARCH_INDEX.values():
		count += len(section_data)
	logger.info("Building index of %s items took %s" % (count, time.time() - start))

def fetch_url(query):
	return 'https://vgmdb.net/search?q=%s'%(urllib.quote(query))
def fetch_page(query, retries=2):
	if SEARCH_INDEX:
		return search_locally(query)

	try:
		url = fetch_url(query)
		page = urllib.urlopen(url)
	except urllib2.HTTPError, error:
		print >> sys.stderr, "HTTPError %s while fetching %s" % (error.code, url)
		if error.code == 503 and retries:
			time.sleep(random.randint(500, 3000)/1000.0)
			return fetch_page(url, retries-1)
		print >> sys.stderr, error.read()
		raise

	if page.geturl() == url:
		data = page.read()
		data = data.decode('utf-8', 'ignore')
		return data
	return masquerade(url, page)

def search_locally(query):
	sections = {'albums':[],
	            'artists':[],
	            'orgs':[],
	            'products':[]}

	start = time.time()
	pieces = [p.decode('utf-8').lower() for p in query.split() if len(p) >= 3]
	substrings = ["(?=.*%s)"%(re.escape(p),) for p in pieces]
	needle = re.compile("".join(substrings), re.I)
	for section, data in SEARCH_INDEX.iteritems():
		# check if this section has this set of keywords
		if not all(piece[:16].encode('utf-8') in BLOOM_INDEX[section] for piece in pieces):
			logger.debug("%s not found in %s" % (pieces, section))
			continue  # and skip if not
		for item in data:
			# albums
			if any(needle.match(t) for t in item.get('titles', {}).values()):
				sections[section].append(item)
			# others
			elif any(needle.match(t) for t in item.get('names', {}).values()):
				sections[section].append(item)
			elif needle.match(item.get('name_real', '')):
				sections[section].append(item)
	logger.debug("Searching for %s locally took %s" % (pieces, time.time() - start,))
	fake = {
	    "meta":{},
	    "query":query,
	    "results":sections,
	    "sections":sorted(sections.keys())
	}
	return fake

def masquerade(url, page):
	import urlparse
	import importlib
	sections = {'albums':[],
	            'artists':[],
	            'orgs':[],
	            'products':[]}
	parsed = urlparse.urlparse(page.geturl())
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
	orig_parsed = urlparse.urlparse(url)
	query = urlparse.parse_qs(orig_parsed.query)['q'][0]
	query = urllib.unquote(query)
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
	soup = bs4.BeautifulSoup(html_source)
	soup_innermain = soup.find(id='innermain')
	if soup_innermain == None:
		return None	# info not found

	# parse the section
	for soup_section in soup_innermain.div.find_all('div'):
		if not soup_section.has_attr('id'):
			continue
		section_type = soup_section['id']
		if not section_types.has_key(section_type):
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
	catalog = unicode(soup_cells[0].span.string)
	special = soup_cells[1].img
	soup_album = soup_cells[2]
	link = soup_album.a['href']
	link = utils.trim_absolute(link)
	names = utils.parse_names(soup_album.a)
	date = utils.parse_date_time(soup_cells[3].string)
	media_format = unicode(soup_cells[4].string)
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
