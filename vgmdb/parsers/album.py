import bs4

from . import utils

fetch_url = lambda id: utils.url_info_page('album', id)
fetch_page = lambda id: utils.fetch_info_page('album', id)

def parse_page(html_source):
	album_info = {}
	html_source = utils.fix_invalid_table(html_source)
	soup = bs4.BeautifulSoup(html_source)
	soup_profile = soup.find(id='innermain')
	soup_right_column = soup.find(id='rightcolumn')
	if soup_profile == None:
		return None	# info not found

	# parse names
	soup_names = soup_profile.h1
	album_info['names'] = utils.parse_names(soup_names)
	album_info['name'] = album_info['names']['en']

	# main cover
	soup_cover = soup_profile.find(id='coverart')
	if soup_cover:
		style = soup_cover.get('style', '')
		medium_link = utils.extract_background_image(style)
		if medium_link:
			medium_link = utils.force_absolute(medium_link)
			full_link = utils.media_full(medium_link)
			thumb_link = utils.media_thumb(medium_link)
			album_info['picture_thumb'] = thumb_link
			album_info['picture_small'] = medium_link
			album_info['picture_full'] = full_link

	# main info header
	soup_info = soup_profile.find(id='rightfloat').div.div.table
	album_info.update(_parse_album_info(soup_info))

	# credit list
	soup_credithead = _find_element_named(soup_profile, 'span', 'Credits')
	if soup_credithead is not None:
		soup_creditinfo = soup_credithead.parent.parent
		soup_creditlist = soup_creditinfo.div.div.table
		album_info.update(_parse_album_info(soup_creditlist))

	# track list
	soup_tracklist = _find_element_named(soup_profile, 'h3', 'Tracklist').parent.parent
	album_info['discs'] = _parse_tracklist(soup_tracklist)

	# stats
	album_info.update(_parse_right_column(soup_right_column))

	# notes
	soup_notes_container = _find_element_named(soup_profile, 'h3', 'Notes').parent
	album_info['notes'] = utils.parse_string(soup_notes_container.div.div).strip()

	# add any required properties
	required_lists = ['arrangers', 'composers', 'covers', 'lyricists', 'organizations', 'performers']
	for key in required_lists:
		if not key in album_info:
			album_info[key] = []
	return album_info

def _find_element_named(soup_profile, tagname, name):
	for element in soup_profile.find_all(tagname):
		if element.text and element.text.strip() == name:
			return element

def _parse_album_info(soup_info):
	def addOrganization(info, role='publisher'):
		if not 'organizations' in album_info:
			album_info['organizations'] = []
		info = dict(info)
		if info.get('link', "").startswith("search"):
			del info['link']
		album_info['organizations'].append(info)
		album_info['organizations'][-1]['role'] = role
		is_publisher = role in ('publisher', 'label')
		is_distributor = role in ('distributor', 'retailer')
		if (is_publisher and 'publisher' not in album_info):
			album_info['publisher'] = info
		if is_distributor and 'distributor' not in album_info:
			album_info['distributor'] = info
		if len(album_info['organizations']) == 1 and not is_distributor:
			album_info['publisher'] = info

	album_info = {}
	if 'class' in soup_info.attrs and \
	   soup_info['class'][0] == 'bootleg':
		album_info['bootleg'] = True
	if soup_info.tbody is not None:
		soup_info = soup_info.tbody
	soup_info_rows = soup_info.find_all('tr', recursive=False)
	for soup_row in soup_info_rows:
		if soup_row.td is None:
			continue
		name = utils.parse_names(soup_row.td.find('b'))['en']
		name = unicode(name)
		soup_value = soup_row.td.find_next_sibling('td')
		names_single = {'Publish Format':'publish_format',
		                'Media Format':'media_format',
		                'Classification':'classification',
		                'Barcode':'barcode'}
		names_multiple = {'Composed by':'composers',
		                  'Arranged by':'arrangers',
		                  'Performed by':'performers',
		                  'Lyrics by':'lyricists',
		                  'Composer':'composers',
		                  'Arranger':'arrangers',
		                  'Performer':'performers',
		                  'Lyricist':'lyricists',
		                  'Vocals':'vocals',
		                  'All Composed by':'composers',
		                  'All Music Composed by':'composers',
		                  'All Arranged by':'arrangers',
		                  'All Music Arranged by':'arrangers',
		                  'Music':'composers',
		                 }
		organization_names = ["Publisher", "Distributor",
		                      "Retailer", "Exclusive Retailer",
		                      "Manufacturer", "Label"]

		if name == "Catalog Number":
			for child in soup_value.descendants:
				if not isinstance(child, bs4.Tag):
					text = child.string.strip()
					if len(text) > 0:
						catalog = text
						break
			catalog = catalog.split('(')[0].strip()
			reprints = []
			for soup_reprint in soup_value.find_all('a'):
				if soup_reprint.get('href') == '#':
					continue
				note = None
				link = soup_reprint['href']
				link = utils.trim_absolute(link)
				name = soup_reprint.string.strip()
				if name.find('(') != -1:
					left = name.find('(')
					right = name.find(')', left)
					note = name[left+1:right]
					name = name[:left].strip()
					if name == '':
						name = 'N/A'
				if name == catalog:
					continue
				reprint_info = {"catalog": name, "link": link}
				if note:
					reprint_info['note'] = note
				else:
					reprint_info['note'] = ''
				reprints.append(reprint_info)
			album_info['catalog'] = catalog
			if 'bootleg' in album_info and len(reprints)>0:
				album_info['bootleg_of'] = reprints[0]
				album_info['reprints'] = []
			else:
				album_info['reprints'] = reprints
		elif name == "Release Date":
			soup_events = []
			soup_children = soup_value.contents
			if isinstance(soup_children[0], bs4.Tag):
				if soup_children[0].name == 'a':	# link to calendar
					date = soup_value.a['href'].split('#')[1]
					if date.isdigit():
						album_info['release_date'] = '%s-%s-%s'%(date[0:4], date[4:6], date[6:8])
					else: # link to calendar, but date is ambiguous (Jul 1997)
						album_info['release_date'] = utils.parse_date_time(soup_value.a.string)
					soup_event = soup_value.a.find_next_sibling('a')
				else:			# freeform text
					album_info['release_date'] = soup_value.value
			if isinstance(soup_children[0], bs4.NavigableString):
				if 'release_date' not in album_info:
					album_info['release_date'] = str(soup_children[0]).strip()
			for soup_event in soup_children[1:]:
				if not isinstance(soup_event, bs4.Tag): continue
				if 'Pending edit' in soup_event.get('title'):
					# Pending edit pencil
					continue
				link = utils.trim_absolute(soup_event['href'])
				event = {}
				event['name'] = soup_event['title']
				event['shortname'] = unicode(soup_event.string)
				event['link'] = link
				soup_events.append(event)
			album_info['release_events'] = soup_events
		elif name == 'Release Price':
			price = soup_value.contents[0].strip()
			price = price.split('(')[0].strip()
			album_info['release_price'] = {"price":price}
			try:
				price = float(soup_value.contents[0])
				currency = soup_value.acronym.string.strip()
				album_info['release_price'] = {"price":price, "currency":currency}
			except:
				pass
		elif name in organization_names:
			anchors = soup_value.find_all('a')
			for anchor in anchors:
				if anchor:
					link = anchor['href']
					link = utils.trim_absolute(link)
					info = {}
					info['link'] = link
					info['names'] = utils.parse_names(anchor)
					addOrganization(info, name.split()[-1].lower())
		elif name == 'Organizations':
			soup_links = soup_value.find_all('a')
			if len(soup_links) == 0:
				addOrganization({'names':{'en':soup_value.string.strip()}}, 'publisher')
			# Organizations row has some expando-javascript
			for soup_child in soup_value.children:
				if isinstance(soup_child, bs4.Tag) and soup_child.name == 'span' and soup_child.get('id') == 'publisher_less':
					soup_value = soup_child
					break

			info = None
			role = 'publisher'

			for soup_child in soup_value.children:
				if isinstance(soup_child, bs4.Tag) and soup_child.name == 'a':
					# found a new org, commit any previous one
					if info is not None:
						addOrganization(info, role)
						info = None

					link = soup_child['href']
					link = utils.trim_absolute(link)
					info = {}
					info['link'] = link
					info['names'] = utils.parse_names(soup_child)
				else:
					text = unicode(soup_child.string).strip()
					splits = text.split('(', 1)
					if len(splits) == 2 and len(splits[0].strip()) > 3:
						# unlinked publisher
						info = {'names': {'en': splits[0].strip()}}
					if len(splits) == 2:
						roles = splits[1].split(',')
						for role in roles:
							role = role.strip()
							role = role.strip(')')
							role = role.strip()
							addOrganization(info, role.lower())
						info = None
			if info is not None:
				addOrganization(info, role)
		elif name in names_single.keys():
			key = names_single[name]
			soup_value = soup_value.contents[0]
			value = soup_value.string.strip()
			album_info[key] = value
		elif name in names_multiple.keys():
			key = names_multiple[name]
			value = []
			for soup_child in soup_value.children:
				if isinstance(soup_child, bs4.Tag) and soup_child.name=='a':
					link = {}
					link['link'] = utils.trim_absolute(soup_child['href'])
					link['names'] = utils.parse_names(soup_child)
					value.append(link)
				elif isinstance(soup_child, bs4.Tag):
					# Skipping unknown tag
					pass
				else:
					snippet = soup_child.string
					snippet = snippet.strip('()')
					pieces = snippet.split(',')
					pieces = [a.strip() for a in pieces if len(a.strip())>0]
					names = [{'names':{'en':name}} for name in pieces]
					value.extend(names)
			album_info[key] = value
		else:
			# unknown key
			pass
	return album_info

def _parse_tracklist(soup_tracklist):
	discs = []
	soup_sections = soup_tracklist.find_all('div', recursive=False)
	languages = [unicode(li.a.string) for li in soup_sections[0].ul.find_all('li', recursive=False)]
	soup_tabs = soup_sections[1].div.find_all('span', recursive=False)
	tab_index = -1
	for soup_tab in soup_tabs:
		tab_index += 1
		tab_language = languages[tab_index]
		index = 0
		soup_cur = soup_tab.span
		while soup_cur:
			disc_name = unicode(soup_cur.b.string)
			soup_tracklist = soup_cur.find_next_sibling('table')
			soup_cur = soup_tracklist.find_next_sibling('span')
			maybe_disc_length = soup_cur.find_all('span')[-1].string
			if maybe_disc_length:
				disc_length = unicode(maybe_disc_length)
			else:
				disc_length = u'Unknown'
			if len(discs) < index+1:
				discs.append({})
			discs[index]['name'] = disc_name
			discs[index]['disc_length'] = disc_length
			if not discs[index].has_key('tracks'):
				discs[index]['tracks'] = []
			track_no = -1
			for soup_track in soup_tracklist.find_all('tr', recursive=False):
				soup_cells = soup_track.find_all('td')
				if len(soup_cells) != 3:
					continue
				track_no += 1
				track_name = unicode(soup_cells[1].string).strip()
				maybe_track_length = soup_cells[2].span.string
				if maybe_track_length:
					track_length = unicode(maybe_track_length)
				else:
					track_length = u'Unknown'
				if len(discs[index]['tracks']) < track_no + 1:
					discs[index]['tracks'].append({'names':{},'track_length':track_length})
				discs[index]['tracks'][track_no]['names'][tab_language] = track_name
			soup_cur = soup_cur.find_next_sibling('span')
			index += 1
	return discs

def _parse_right_column(soup_right_column):
	album_info = {}
	soup_div = soup_right_column.div
	while soup_div:
		soup_section = soup_div.find_next_sibling('div')
		if soup_div.div.h3:
			section_title = unicode(soup_div.div.h3.string)
			if section_title == 'Album Stats':
				album_info.update(_parse_section_album_stats(soup_section.div))
			if section_title == 'Related Albums':
				album_info['related'] = _parse_section_related_albums(soup_section.span)
			if section_title == 'Available at':
				album_info['stores'] = _parse_section_stores(soup_section.div)
			if section_title == 'Websites':
				album_info['websites'] = _parse_section_websites(soup_section.div)
			if section_title == 'Covers':
				# frickin covers section is different format
				soup_section = soup_div.find('div', id='cover_gallery')
				# do the parsing
				album_info['covers'] = _parse_section_covers(soup_section)
				#import ipdb; ipdb.set_trace()
				soup_section = soup_div.find_next_sibling()	# allow the next_sibling loop to work
				if not soup_section:
					soup_section = soup_div
				pass
			soup_div = soup_section.find_next_sibling('div')
		else:
			# found entry stats
			soup_section = soup_div.div
			album_info['meta'] = utils.parse_meta(soup_section)
			soup_div = None
			pass
	return album_info

def _parse_section_album_stats(soup_section):
	album_info = {}
	soup_divs = soup_section.find_all('div', recursive=False)
	soup_rating = soup_divs[0].find_all('span', recursive=False)
	if len(soup_rating) <= 1:
		album_info['votes'] = 0
	else:
		splits = soup_rating[1].string.split()
		if splits[0] == 'Nobody':
			album_info['votes'] = 0
		else:
			album_info['rating'] = float(splits[1])
			album_info['votes'] = int(splits[3])

	for soup_div in soup_divs[1:]:
		if not soup_div.b:
			continue
		div_name = soup_div.b.string.strip()
		div_value = None
		for child in soup_div.children:
			if not isinstance(child, bs4.Tag):
				div_value = child.string.strip()
		if div_name == 'Category':
			categories = div_value.split(',')
			categories = [x.strip() for x in categories]
			album_info['category'] = categories[0]
			album_info['categories'] = categories
		if div_name == 'Products represented':
			album_info['products'] = []
			for soup_product in soup_div.find_all('a', recursive=False):
				product = {}
				product['link'] = utils.parse_vgmdb_link(soup_product['href'])
				if product['link'].startswith('search?'):
					# this product does not have a product page
					del product['link']
				product['names'] = utils.parse_names(soup_product)
				album_info['products'].append(product)
			text = soup_div.find('br').next
			if not isinstance(text, bs4.Tag):
				for productname in [x.strip() for x in text.split(',') if len(x.strip())>0]:
					product = {}
					product['names'] = {'en':productname}
					album_info['products'].append(product)
		if div_name == 'Platforms represented':
			album_info['platforms'] = [plat.strip() for plat in div_value.split(',')]
	return album_info

def _parse_section_related_albums(soup_div):
	albums = []
	for soup_album in soup_div.find_all('div', recursive=False):
		date = None
		if soup_album.ul:		# if there are thumbnails
			soup_rows = soup_album.ul.find_all('li', recursive=False)
			catalog = soup_rows[1].find('span', recursive=False).string.strip()
			names = utils.parse_names(soup_rows[0].a)
			album_type = soup_rows[0].a['class'][-1].split('-')[1]
			date = utils.parse_date_time(soup_rows[2].string.strip())
			link = soup_rows[0].a['href']
			link = utils.trim_absolute(link)
		else:
			catalog = unicode(soup_album.find('span', recursive=False).string)
			names = utils.parse_names(soup_album.a)
			album_type = soup_album.a['class'][-1].split('-')[1]
			link = soup_album.a['href']
			link = utils.trim_absolute(link)

		album = {}
		album['catalog'] = catalog
		album['link'] = link
		album['type'] = album_type
		album['names'] = names
		if date:
			album['date'] = date

		albums.append(album)
	return albums

def _parse_section_stores(soup_stores):
	""" Given an array of divs containing website information """
	links = []
	soup_rows = soup_stores.find_all('span', recursive=False)
	for soup_row in soup_rows:
		if soup_row.a is None:
			continue
		soup_link = soup_row.a
		link = soup_link['href']
		name = unicode(soup_link.string)
		if link[0:9] == '/redirect':
			link = utils.strip_redirect(link)
		links.append({"link":link, "name":name})
	return links

def _parse_section_websites(soup_websites):
	""" Given an array of divs containing website information """
	sites = {}
	for soup_category in soup_websites.find_all('div', recursive=False):
		category = unicode(soup_category.b.string)
		links = []
		soup_rows = soup_category.find_all('span', recursive=False)
		for soup_row in soup_rows:
			if soup_row.a is None:
				continue
			soup_link = soup_row.a
			link = soup_link['href']
			name = unicode(soup_link.string)
			if link[0:9] == '/redirect':
				link = utils.strip_redirect(link)
			links.append({"link":link, "name":name})
		sites[category] = links
	return sites

def _parse_section_covers(soup_covers):
	""" Given an array of tables """
	covers = []
	for soup_table in soup_covers.find_all('table', recursive=False):
		for soup_row in soup_table.find_all('tr'):
			for soup_cell in soup_row.find_all('td'):
				soup_link = soup_cell.a
				if not soup_link:
					continue
				medium_link = utils.force_absolute(soup_cell.a['href'])
				full_link = utils.media_full(medium_link)
				thumb_link = utils.media_thumb(medium_link)
				if soup_cell.a.h4.string:
					name = soup_cell.a.h4.string.strip()
				else:
					name = ''
				cover = {"name":name, "thumb":thumb_link, \
				         "medium":medium_link, "full":full_link}
				covers.append(cover)
	return covers

