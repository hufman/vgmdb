import bs4

from . import utils

fetch_url = lambda id: utils.url_info_page('product', id)
fetch_page = lambda id: utils.fetch_info_page('product', id)

def parse_page(html_source):
	product_info = {}
	soup = bs4.BeautifulSoup(html_source)
	soup_profile = soup.find(id='innermain')
	soup_right_column = soup.find(id='rightcolumn')
	if soup_profile == None:
		return None	# info not found

	soup_name = soup_profile.h1
	product_info['name'] = soup_name.span.string.strip()
	soup_real_name = soup_profile.find(id='subtitle')
	if soup_real_name:
		soup_real_name = soup_real_name.span
		if len(soup_real_name.contents) == 1:
			product_info['name_real'] = soup_real_name.string
		elif len(soup_real_name.contents) > 1:
			product_info['name_real'] = soup_real_name.contents[0].string

	soup_type = soup_name.find_next_sibling('span')
	if soup_type:
		product_info['type'] = soup_type.string[1:-1]

	soup_profile = soup_profile.find(id='innercontent')
	if soup_profile.find(id='innermain'):
		soup_profile = soup_profile.find(id='innermain')
	soup_profile_sections = soup_profile.find_all('div', recursive=False)

	soup_pic_div = soup_profile_sections[0]
	if soup_pic_div.a and soup_pic_div.a.img:
		full_link = soup_pic_div.a['href']
		medium_link = soup_pic_div.a.img['src']
		product_info['picture_full'] = utils.force_absolute(full_link)
		product_info['picture_small'] = utils.force_absolute(medium_link)

	if soup_profile.find('h3').find_previous_sibling('div'):	# full profile
		soup_profile_info = soup_profile_sections[1].div.dl
		product_info.update(_parse_product_info(soup_profile_info))

	soup_section_heads = soup_profile.find_all('h3', recursive=False)
	for soup_section_head in soup_section_heads:
		section_name = soup_section_head.string
		soup_section = soup_section_head.find_next_sibling('div')
		if section_name == 'Titles':
			product_info['titles'] = _parse_franchise_titles(soup_section.div.table)
		if section_name == 'Releases':
			product_info['releases'] = _parse_product_releases(soup_section.div.table)
		if section_name == 'Albums | Credits':
			product_info['albums'] = utils.parse_discography(soup_section.div.table, 'classifications')

	soup_divs = soup_right_column.find_all('div', recursive=False)
	product_info['meta'] = utils.parse_meta(soup_divs[-1].div)

	return product_info

def _parse_product_info(soup_profile_info):
	""" Receives a dl list from a product's info box """
	product_info = {}
	name = None
	value = None
	for soup_child in soup_profile_info:
		if not isinstance(soup_child, bs4.Tag):
			continue
		if soup_child.name == 'dt':
		   	name = soup_child.b.string
			value = None
		if soup_child.name == 'dd':
			if soup_child.div:
				value = []
				for soup_child_div in soup_child.find_all('div', recursive=False):
					for soup_child_link in soup_child_div.find_all('a', recursive=False):
						item = {}
						item['names'] = utils.parse_names(soup_child_link)
						item['link'] = utils.trim_absolute(soup_child_link['href'])
						value.append(item)
			else:
				value = soup_child.string

			if name == 'Franchises' and isinstance(value, list):
				product_info['franchises'] = value
			if name == 'Release Date' and value != None:
				product_info['release_date'] = utils.parse_date_time(value)
			if name == 'Organizations' and value != None:
				if isinstance(value, list):
					product_info['organizations'] = value
				else:
					product_info['organizations'] = [value]
			if name == 'Description' and value != None:
				product_info['description'] = value
	return product_info

def _parse_product_releases(soup_table):
	releases = []
	if not soup_table:
		return releases
	soup_rows = soup_table.find_all('tr', recursive=False)
	if len(soup_rows) == 0:
		return releases
	for soup_row in soup_rows[1:]:
		soup_cells = soup_row.find_all('td', recursive=False)
		if len(soup_cells) < 4:
			continue
		release = {}
		release['date'] = utils.normalize_dashed_date(soup_cells[0].span.string)
		release['names'] = utils.parse_names(soup_cells[1].span)
		release['region'] = soup_cells[2].span.string
		release['platform'] = soup_cells[3].span.string
		releases.append(release)
	releases = sorted(releases, key=lambda e:e['date'])
	return releases

def _parse_franchise_titles(soup_table):
	titles = []
	if not soup_table:
		return titles
	soup_rows = soup_table.find_all('tr', recursive=False)
	if len(soup_rows) == 0:
		return titles
	for soup_row in soup_rows[1:]:
		soup_cells = soup_row.find_all('td', recursive=False)
		if len(soup_cells) < 2:
			continue
		if soup_cells[1].span.string == 'No titles found':
			continue
		title = {}
		title['date'] = utils.normalize_dashed_date(soup_cells[0].span.string)
		title['names'] = utils.parse_names(soup_cells[1].span)
		if soup_cells[1].a:
			title['link'] = utils.trim_absolute(soup_cells[1].a['href'])
		titles.append(title)
	titles = sorted(titles, key=lambda e:e['date'])
	return titles

