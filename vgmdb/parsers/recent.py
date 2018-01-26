import bs4

from . import utils
import urlparse

fetch_url = lambda type: "https://vgmdb.net/db/recent.php?do=view_%s"%(type,)
fetch_page = lambda type: utils.fetch_page(fetch_url(type))

def parse_page(html_source):
	recent_info = {}
	html_source = utils.fix_invalid_table(html_source)
	soup = bs4.BeautifulSoup(html_source)
	
	soup_innermain = soup.find(id='innermain')
	if soup_innermain == None:
		return None	# info not found

	# parse section tabs
	soup_sections = soup.find('ul', class_='tabnav')
	cur_section = _determine_section(soup_sections)
	recent_info['sections'] = _parse_sections(soup_sections)

	# parse table
	soup_codes = soup_innermain.find('div', class_='smallfont')
	color_codes = _parse_color_codes(soup_codes)
	recent_info['updates'] = _parse_table(cur_section, color_codes, soup_innermain.find('table'))

	# add what recent page this is
	recent_info['section'] = cur_section

	# add the modification time
	edited_date = sorted([u['date'] for u in recent_info['updates']])[-1]
	recent_info['meta'] = {'edited_date':edited_date}

	return recent_info

def _determine_section(soup_sections):
	soup_active = soup_sections.find('li', class_='active')
	link = soup_active.a['href']
	type = link.split('_')[-1]
	return type

def _parse_sections(soup_sections):
	sections = []
	soup_tabs = soup_sections.find_all('li', recursive=False)
	for soup_tab in soup_tabs:
		link = soup_tab.a['href']
		type = link.split('_')[-1]
		sections.append(type)
	return sections

def _parse_table(type, color_codes, soup_table):
	info = []
	for soup_row in soup_table.find_all('tr')[1:]:
		soup_cells = soup_row.find_all('td')
		info.append(globals()['_parse_table_%s'%(type,)](color_codes, soup_cells))
	return info

def _parse_table_albums(color_codes, soup_cells):
	info = {}
	info.update(_parse_catalog_release_cell(soup_cells[0]))
	info.update(_parse_title_cell('albums', color_codes, soup_cells[1]))
	info.update(_parse_contributor_cell(soup_cells[2]))
	return info


def _parse_table_media(color_codes, soup_cells):
	info = {}

	# first column
	soup_catalog = soup_cells[0]
	info['catalog'] = unicode(soup_cells[0].string)
	if info['catalog'] == 'Deleted Media':
		info['deleted'] = True

	# second column
	info.update(_parse_title_cell('media', color_codes, soup_cells[1]))

	# third column
	info.update(_parse_contributor_cell(soup_cells[2]))

	# done
	return info

def _parse_table_tracklists(color_codes, soup_cells):
	info = {}
	info.update(_parse_catalog_release_cell(soup_cells[0]))
	info.update(_parse_title_cell('tracklists', color_codes, soup_cells[1]))
	info.update(_parse_contributor_cell(soup_cells[2]))
	return info

def _parse_table_scans(color_codes, soup_cells):
	info = {}

	# first column
	soup_link = soup_cells[0].a
	info['link'] = utils.trim_absolute(soup_link['href'])
	info['edit'] = 'added'
	if soup_link.img['src'] == 'icons/del.gif':
		info['edit'] = 'deleted'
	else:
		info['image'] = utils.force_absolute(soup_link.img['src'])

	# second column
	caption = utils.parse_string(soup_cells[1])
	info['catalog'] = caption.split('\n')[0]
	if info['edit'] != 'deleted':
		info['caption'] = caption.split('\n')[1]

	# third column
	info.update(_parse_contributor_cell(soup_cells[2]))
	return info

def _parse_table_artists(color_codes, soup_cells):
	info = {}
	info.update(_parse_title_cell('artists', color_codes, soup_cells[1]))
	info.update(_parse_contributor_cell(soup_cells[2]))
	if soup_cells[0].a:
		soup_link = soup_cells[0].a
		info['linked'] = {
			"link": utils.trim_absolute(soup_link['href']),
			"catalog": unicode(soup_link.string)
		}
	return info

def _parse_table_products(color_codes, soup_cells):
	info = {}
	info.update(_parse_title_cell('products', color_codes, soup_cells[1]))
	info.update(_parse_contributor_cell(soup_cells[2]))
	if info['edit'] == 'Album Linkup':
		soup_link = soup_cells[0].a
		info['linked'] = {
			"link": utils.trim_absolute(soup_link['href']),
			"catalog": unicode(soup_link.string)
		}
	return info

def _parse_table_labels(color_codes, soup_cells):
	info = {}
	info.update(_parse_title_cell('labels', color_codes, soup_cells[1]))
	info.update(_parse_contributor_cell(soup_cells[2]))
	if info['edit'] == 'Album Linkup':
		soup_link = soup_cells[0].a
		info['linked'] = {
			"link": utils.trim_absolute(soup_link['href']),
			"catalog": unicode(soup_link.string)
		}
	if info['edit'] == 'Artist Linkup':
		soup_link = soup_cells[0].a
		info['linked'] = {
			"link": utils.trim_absolute(soup_link['href']),
			"names": {'en':unicode(soup_link.string)}
		}
	return info

def _parse_table_links(color_codes, soup_cells):
	info = {}
	info.update(_parse_title_cell('links', color_codes, soup_cells[1]))
	info.update(_parse_contributor_cell(soup_cells[2]))
	soup_link = soup_cells[0].a
	if 'link_type' in info and info['link_type'] in \
	   ['Album Link', 'Purchase Link']:
		info.update({
			"link": utils.trim_absolute(soup_link['href']),
			"catalog": unicode(soup_link.string)
		})
	if 'link_type' in info and info['link_type'] in \
	   ['Artist Link']:
		soup_link = soup_cells[0].a
		info.update({
			"link": utils.trim_absolute(soup_link['href']),
			"names": {'en':unicode(soup_link.string)}
		})
	if 'link_type' in info and info['link_type'] in \
	   ['Organization Link', 'Product Link']:
		soup_link = soup_cells[0].a
		item_link = utils.trim_absolute(soup_link['href'])
		parsed_link = urlparse.urlparse(item_link)
		parsed_qs = urlparse.parse_qs(parsed_link[4])
		item_id = parsed_qs.get('id', None)
		if item_id:
			if info['link_type'] == 'Organization Link':
				item_link = 'org/' + item_id[0]
			if info['link_type'] == 'Product Link':
				item_link = 'product/' + item_id[0]
		info.update({
			"link": item_link,
			"names": {'en':unicode(soup_link.string)}
		})
	return info

def _parse_table_ratings(color_codes, soup_cells):
	info = {}
	info.update(_parse_catalog_release_cell(soup_cells[0]))
	info.update(_parse_title_cell('ratings', color_codes, soup_cells[1]))
	info['rating'] = soup_cells[2]['title']
	info.update(_parse_contributor_cell(soup_cells[3]))
	return info

# Type code utilities
def _parse_color_codes(soup_container):
	""" Returns a mapping of color_codes to their information

	The information tables' title column applies a color code
	The end of the page has a color key
	Albums and Ratings use class names to match the colors
	The other sections use direct style:color attributes

	The information texts mean different things on different pages
	Albums and Ratings:
		class name is the ['type'] found in albumlist
		information is the ['category'] found in album info
	Media:
		information is the album info's ['media_format']
	Tracklists:
		information is the ['category'] found in album info
	Products:
		information is the edit type
	Labels:
		information is the edit type
	Links:
		information is the changed link type
	"""
	color_codes = {}
	for soup_type in soup_container.find_all('span'):
		name = unicode(soup_type.string)
		if soup_type.has_attr('style') and 'color' in soup_type['style']:
			style = soup_type['style']
			color = style.split(':')[-1].strip()
			color_codes[color] = name
	return color_codes
def _parse_color_code(color_codes, color_code):
	return color_codes.get(color_code)

# Parse common cells
def _parse_catalog_release_cell(soup_release):
	info = {}
	text = utils.parse_string(soup_release)
	lines = text.strip().split('\n')
	if len(lines) < 2:
		info['deleted'] = True
		return info
	info['catalog'] = lines[0]
	info['release_date'] = utils.parse_date_time(lines[1])
	return info

def _parse_title_cell(type, color_codes, soup_cell):
	info = {}
	info['edit'] = 'updated'
	soup_badges = soup_cell.find_all('img')
	for soup_badge in soup_badges:
		if soup_badge['title'] == 'Child Album':
			info['reprint'] = True
		if soup_badge['title'] == 'New Submission':
			info['edit'] = 'new'
			info['new'] = True
		if soup_badge['title'] == 'Deleted Album':
			info['edit'] = 'deleted'
		if soup_badge['title'] == 'Deleted Link':
			info['edit'] = 'deleted'
		if soup_badge['title'] == 'Rejected Submission':
			info['edit'] = 'rejected'
	soup_title = None
	soup_link = soup_cell.a
	name_key = 'titles'
	if type == 'artists':
		name_key = 'names'
	if soup_link:
		if not soup_link.string and not soup_link.contents:
			soup_title = soup_link
		if soup_link.string:
			soup_title = soup_link
		if soup_link.span and soup_link.span.has_attr('lang'):
			soup_title = soup_link
		if soup_link.span and not soup_link.span.has_attr('lang'):
			soup_title = soup_link.span
		if soup_link.span and soup_link.span.span and soup_link.span.span.has_attr('lang'):
			soup_title = soup_link.span
		info[name_key] = utils.parse_names(soup_title)
	else:
		# some deleted album
		if soup_cell.span:
			info[name_key] = utils.parse_names(soup_cell.span)
		else:
			info[name_key] = utils.parse_names(soup_cell)
		info['deleted'] = True
		return info
	# check for category
	if soup_link.has_attr('class') and len(soup_link['class']) > 1:
		klass = soup_link['class'][-1]
		info['type'] = klass.split('-')[-1]
		info['category'] = utils.type_category(info['type'])
	# check for media format
	style = None
	color = None
		# find the style tag
	if soup_link.has_attr('style'):
		style = soup_link['style']
	if soup_link.span and soup_link.span.has_attr('style'):
		style = soup_link.span['style']
		# parse out the color from the style
	if style and 'color' in style:
		color = style.split(':')[-1].strip()
		# figure out what the color means
	if not color and type in ['labels','links']:
		color = '#CEFFFF'
	if color:
		info_text = _parse_color_code(color_codes, color)
		if type in ['albums', 'ratings', 'tracklists']:
			info['category'] = info_text
			info['type'] = utils.category_type(info['category'])
		if type == 'media':
			info['media_format'] = info_text
		if type == 'products':
			info['edit'] = info_text
		if type == 'labels':
			info['edit'] = info_text
		if type == 'links':
			info['link_type'] = info_text
			del info['titles']
	if type == 'links':
		info['link_data'] = {
			'link': utils.force_absolute(soup_link['href']),
			'title': unicode(soup_link.string or '')
		}
	else:
		info['link'] = utils.trim_absolute(soup_link['href'])
	if type == 'products' and info['edit'] == 'Release Edit':
		# don't know how to link to Releases yet
		del info['link']
	return info

def _parse_contributor_cell(soup_cell):
	info = {}
	soup_link = soup_cell.a
	info['contributor'] = {
	    'name': unicode(soup_link.string),
	    'link': utils.force_absolute(soup_link['href'])
	}
	soup_date = soup_cell.br.next_element
	date_str = unicode(soup_date) + unicode(soup_date.next_element.string)
	info['date'] = utils.parse_date_time(date_str)
	return info
