import bs4

from . import utils

fetch_url = lambda id: utils.url_info_page('product', id)
fetch_page = lambda id: utils.fetch_info_page('product', id)

def parse_page(html_source):
	product_info = {}
	product_info['description'] = ''
	product_info['websites'] = {}
	product_info['albums'] = []
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
			product_info['name_real'] = unicode(soup_real_name.string)
		elif len(soup_real_name.contents) > 1:
			product_info['name_real'] = unicode(soup_real_name.contents[0].string)

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

	last_div = soup_profile.find('h3').find_previous_sibling('div')
	if last_div:	# full profile info box
		soup_profile_info = last_div.find('dl')
		if soup_profile_info:
			product_info.update(_parse_product_info(soup_profile_info))
		else:
			# comment box
			product_info['description'] = utils.parse_string(last_div).strip()

	soup_section_heads = soup_profile.find_all('h3', recursive=False)
	for soup_section_head in soup_section_heads:
		section_name = unicode(soup_section_head.string)
		soup_section = soup_section_head.find_next_sibling('div')
		if section_name == 'Belongs to':
			product_info['superproduct'] = _parse_franchise_superproduct(soup_section.div.div)
		if section_name == 'Subproducts':
			product_info['subproducts'] = _parse_franchise_subproducts(soup_section.div.table)
		if section_name == 'Titles':
			product_info['titles'] = _parse_franchise_titles(soup_section.div.table)
		if section_name == 'Releases':
			product_info['releases'] = _parse_product_releases(soup_section.div.table)
		if section_name == 'Albums | Credits':
			product_info['albums'] = utils.parse_discography(soup_section.div.table, 'classifications')

	soup_right_divs = soup_right_column.find_all('div', recursive=False)
	for soup_right_section in soup_right_divs[:-1]:
		if 'rtop' in soup_right_section.find('b', recursive=False)['class']:
			section_head = unicode(soup_right_section.div.h3.string)
		if 'rbot' in soup_right_section.find('b', recursive=False)['class']:
			soup_section_body = soup_right_section.div
			if section_head == 'Websites':
				product_info['websites'] = {}
				for soup_website_section in soup_section_body.find_all('div', recursive=False):
					website_type = unicode(soup_website_section.b.string)
					websites = []
					for soup_site in soup_website_section.find_all('a', recursive=False):
						link = utils.strip_redirect(soup_site['href'])
						name = unicode(soup_site.string)
						websites.append({"link":link,"name":name})
					product_info['websites'][website_type] = websites
	product_info['meta'] = utils.parse_meta(soup_right_divs[-1].div)

	# make sure required things are in place
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
			name = unicode(soup_child.b.string)
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
				if soup_child.string:
					value = unicode(soup_child.string)

			if name == 'Franchises' and isinstance(value, list):
				product_info['franchises'] = value
			if name == 'Release Date' and value != None:
				product_info['release_date'] = utils.parse_date_time(value)
				if not product_info['release_date']:
					del product_info['release_date']
			if name == 'Organizations' and value != None:
				if isinstance(value, list):
					product_info['organizations'] = value
				else:
					product_info['organizations'] = [value]
				# Turn them into named items
			if name == 'Description' and value != None:
				product_info['description'] = value
	required_arrays = ['franchises', 'organizations']
	for key in required_arrays:
		if not key in product_info:
			product_info[key] = []
		named_array = []
		for item in product_info[key]:
			if isinstance(item, dict):
				named_array.append(item)
			else:
				named_array.append({"names": {"en": item}})
		product_info[key] = named_array
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
		if soup_cells[1].find('a', recursive=False):
			release['link'] = utils.parse_vgmdb_link(soup_cells[1].a['href'])
			release['names'] = utils.parse_names(soup_cells[1].a)
		else:
			release['names'] = utils.parse_names(soup_cells[1].span)
		release['region'] = unicode(soup_cells[2].span.string)
		release['platform'] = unicode(soup_cells[3].span.string)
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
		if not title['date']:
			del title['date']
		title['names'] = utils.parse_names(soup_cells[1].span)
		if soup_cells[1].a:
			title['link'] = utils.trim_absolute(soup_cells[1].a['href'])
			type = utils.product_color_type(soup_cells[1].a.span)
			title['type'] = type
		titles.append(title)
	titles = sorted(titles, key=lambda e:e.get('date',''))
	return titles

def _parse_franchise_superproduct(soup_element):
	superproduct = {}
	superproduct['names'] = utils.parse_names(soup_element.a)
	if soup_element.a:
		superproduct['link'] = utils.trim_absolute(soup_element.a['href'])
	return superproduct

def _parse_franchise_subproducts(soup_table):
	subproducts = []
	if not soup_table:
		return titles
	soup_rows = soup_table.find_all('tr', recursive=False)
	if len(soup_rows) == 0:
		return subproducts
	for soup_row in soup_rows[1:]:
		soup_cells = soup_row.find_all('td', recursive=False)
		if len(soup_cells) < 2:
			continue
		if soup_cells[1].span.string == 'No titles found':
			continue
		product = {}
		product['date'] = utils.normalize_dashed_date(soup_cells[0].span.string)
		if not product['date']:
			del product['date']
		product['names'] = utils.parse_names(soup_cells[1].span)
		if soup_cells[1].a:
			product['link'] = utils.trim_absolute(soup_cells[1].a['href'])
			type = utils.product_color_type(soup_cells[1].a.span)
			product['type'] = type
		subproducts.append(product)
	subproducts = sorted(subproducts, key=lambda e:e.get('date',''))
	return subproducts

