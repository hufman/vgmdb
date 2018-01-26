import bs4

from . import utils

fetch_url = lambda id: 'https://vgmdb.net/db/release.php?id=%s'%(id)
fetch_page = lambda id: utils.fetch_page(fetch_url(id))

def parse_page(html_source):
	release_info = {}
	soup = bs4.BeautifulSoup(html_source)
	soup_profile = soup.find(id='innermain')
	soup_right_column = soup.find(id='rightcolumn')
	if soup_profile == None:
		return None	# info not found

	soup_name = soup_profile.h1
	release_info['name'] = soup_name.span.string.strip()
	soup_real_name = soup_profile.find(id='subtitle')
	if soup_real_name:
		soup_real_name = soup_real_name.span
		if len(soup_real_name.contents) == 1:
			release_info['name_real'] = unicode(soup_real_name.string)
		elif len(soup_real_name.contents) > 1:
			release_info['name_real'] = unicode(soup_real_name.contents[0].string)

	soup_type = soup_name.find_next_sibling('span')
	if soup_type:
		release_info['type'] = soup_type.string[1:-1]

	soup_profile = soup_profile.find(id='innercontent')
	if soup_profile.find(id='innermain'):
		soup_profile = soup_profile.find(id='innermain')
	soup_profile_sections = soup_profile.find_all('div', recursive=False)

	soup_pic_div = soup_profile_sections[0]
	if soup_pic_div.a and soup_pic_div.a.img:
		full_link = soup_pic_div.a['href']
		medium_link = soup_pic_div.a.img['src']
		release_info['picture_full'] = utils.force_absolute(full_link)
		release_info['picture_small'] = utils.force_absolute(medium_link)

	soup_section_heads = soup_profile.find_all('h3', recursive=False)
	for soup_section_head in soup_section_heads:
		section_name = unicode(soup_section_head.string)
		soup_section = soup_section_head.find_next_sibling('div')
		if section_name == 'Products':
			release_info['products'] = _parse_products(soup_section.div)
		if section_name == 'Release Information':
			release_info.update(_parse_release_info(soup_section.div))
		if section_name == 'Albums | Credits':
			soup_discos = soup_section.div.find_all('div', recursive=False)
			maybe_soup_table = utils.next_sibling_tag(soup_discos[0])
			if maybe_soup_table.name == 'table':
				release_info['release_albums'] = utils.parse_discography(maybe_soup_table, 'classifications')
			else:
				release_info['release_albums'] = []
			maybe_soup_table = utils.next_sibling_tag(soup_discos[1])
			if maybe_soup_table.name == 'table':
				release_info['product_albums'] = utils.parse_discography(maybe_soup_table, 'classifications')
			else:
				release_info['product_albums'] = []

	soup_divs = soup_right_column.find_all('div', recursive=False)
	release_info['meta'] = utils.parse_meta(soup_divs[-1].div)

	return release_info

def _parse_products(soup_div):
	products = []
	if not soup_div:
		return products
	soup_rows = soup_div.find_all('div', recursive=False)
	if len(soup_rows) == 0:
		return products
	for soup_row in soup_rows:
		product = {}
		if soup_row.find('a', recursive=False):
			product['link'] = utils.parse_vgmdb_link(soup_row.a['href'])
			product['names'] = utils.parse_names(soup_row.a)
		if 'names' in product:
			products.append(product)
	return products

def _parse_release_info(soup_profile_info):
	""" Receives a dl list from a release's info box """
	release_info = {}
	name = None
	value = None
	for soup_column in soup_profile_info.find_all('div', recursive=False):
		if not soup_column.dl:
			continue
		for soup_child in soup_column.dl:
			if not isinstance(soup_child, bs4.Tag):
				continue
			if soup_child.name == 'dt':
				name = unicode(soup_child.b.string)
				value = None
			if soup_child.name == 'dd':
				value = unicode(soup_child.string)
				maps = {
					'Catalog': 'catalog', 'EAN/UPC/JAN': 'upc',
					'Release Type': 'release_type',
					'Platform': 'platform', 'Region': 'region'
				}
				info_key = maps.get(name, None)
				if info_key:
					release_info[info_key] = value
				if name == 'Release Date':
					release_info['release_date'] = utils.parse_date_time(value)

	return release_info
