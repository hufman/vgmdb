import bs4

import re
from . import utils

def parse_search_page(html_source):
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
		section_type = soup_section['id']
		if not section_types.has_key(section_type):
			continue
		section_type = section_types[section_type]
		parse = globals()['_parse_'+section_type]
		search_info['sections'].append(section_type)
		search_info['results'][section_type] = parse(soup_section)

	# parse the query
	match = re.search(r'\$\("#simplesearch"\).val\(\'(.*)\'\);', html_source)
	if match:
		search_info['query'] = match.groups(1)[0]

	# parse page meat
	search_info['meta'] = {}
	
	return search_info

def _parse_albums(soup_section):
	list = []
	for soup_row in soup_section.find_all('tr', recursive=True)[1:]:
		list.append(_parse_album(soup_row))
	return list
def _parse_album(soup_row):
	soup_cells = soup_row.find_all('td', recursive=False)
	catalog = soup_cells[0].span.string
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

def _parse_list(soup_section):
	list = []
	for soup_row in soup_section.find_all('tr', recursive=True)[1:]:
		item = _parse_listitem(soup_row)
		if item:
			list.append(item)
	return list

def _parse_listitem(soup_row):
	soup_cells = soup_row.find_all('td', recursive=False)
	if len(soup_cells) < 1:
		import ipdb; ipdb.set_trace()
	soup_link = soup_cells[0].a
	names = utils.parse_names(soup_link)
	link = soup_link['href']
	link = utils.trim_absolute(link)
	info = {'link':link,
	        'names':names
	}
	soup_aliases = soup_cells[0].span
	if soup_aliases:
		aliases = utils.parse_string(soup_aliases)
		aliases = [piece.strip() for piece in aliases.split('/') if piece.strip()!='']
		info['aliases'] = aliases
	return info
_parse_artists = _parse_list
_parse_orgs = _parse_list
_parse_products = _parse_list

