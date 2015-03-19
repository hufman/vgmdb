import bs4

import re
from . import utils
import urllib

class AppURLOpener(urllib.FancyURLopener):
	version = "vgmdbapi/0.2 +http://vgmdb.info"
urllib._urlopener = AppURLOpener()

def fetch_url(query):
	return 'http://vgmdb.net/search?q=%s'%(urllib.quote(query))
def fetch_page(query):
	url = fetch_url(query)
	page = urllib.urlopen(url)
	if page.geturl() == url:
		data = page.read()
		data = data.decode('utf-8', 'ignore')
		return data
	return masquerade(url, page)

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
	copy_keys = ['aliases', 'catalog','release_date']
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
	match = re.search(r'\$\("#simplesearch"\).val\(\'(.*)\'\);', html_source)
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
	info = {'link':link,
	        'catalog':catalog,
	        'titles':names,
	        'release_date':date
	}
	return info
_parse_artist = _parse_listitem
_parse_org = _parse_listitem
def _parse_product(soup_row):
	product_colors = {
		'#CEFFFF': 'Game',
		'yellowgreen': 'Animation',
		'silver': 'Radio & Drama',
		'white': 'Print Publication',
		'violet': 'Goods',
		'yellow': 'Franchise'
	}
	soup_cells = soup_row.find_all('td', recursive=False)
	soup_link = soup_cells[0].a
	names = utils.parse_names(soup_link.span.span)
	link = soup_link['href']
	link = utils.trim_absolute(link)
	info = {'link':link}
	# aliases could be aliases or name_trans, dunno
	soup_color = soup_cells[0].span
	if soup_color:
		style = soup_color['style']
		if 'color:' in style:
			color = style.split(':')[1]
			if color in product_colors:
				info['type'] = product_colors[color]
		soup_names = soup_color.span
		if soup_names:
			names = utils.parse_names(soup_color)
			info['names'] = names
	return info
