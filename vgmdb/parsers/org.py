import bs4

from . import utils

fetch_url = lambda id: utils.url_info_page('org', id)
fetch_page = lambda id: utils.fetch_info_page('org', id)

def parse_page(html_source):
	org_info = {}
	html_source = utils.fix_invalid_table(html_source)
	soup = bs4.BeautifulSoup(html_source)
	soup_profile = soup.find(id='innermain')
	soup_right_column = soup.find(id='rightcolumn')
	if soup_profile == None:
		return None	# info not found

	soup_divs = soup_profile.find_all('div', recursive=False)
	soup_pic_div = soup_divs[0]
	soup_info_div = soup_divs[1]
	soup_table = soup_profile.table

	soup_name = soup_profile.find_previous_sibling('div')
	if soup_name.h1 and soup_name.h1.string:
		org_info['name'] = soup_name.h1.string.strip()
	else:
		org_info['name'] = ''

	if soup_pic_div.a and soup_pic_div.a.img:
		full_link = soup_pic_div.a['href']
		medium_link = soup_pic_div.a.img['src']
		org_info['picture_full'] = utils.force_absolute(full_link)
		org_info['picture_small'] = utils.force_absolute(medium_link)
	org_info.update(_parse_org_info(soup_info_div.div.div.dl))

	org_info['releases'] = _parse_org_releases(soup_table)

	# Parse websites
	soup_divs = soup_right_column.find_all('div', recursive=False)
	if soup_divs[0].div and soup_divs[0].div.h3 and soup_divs[0].div.h3.string == 'Websites':
		org_info['websites'] = _parse_websites(soup_divs[1].div)
	org_info['meta'] = utils.parse_meta(soup_divs[-1].div)

	return org_info

def _parse_org_info(soup_profile_info):
	""" Receives a dl list from a org's info box """
	org_info = {}
	name = None
	value = None
	for soup_child in soup_profile_info:
		if not isinstance(soup_child, bs4.Tag):
			continue
		if soup_child.name == 'dt':
			name = unicode(soup_child.b.string)
			value = None
		if soup_child.name == 'dd':
			if soup_child.a:
				value = []
				for soup_child_link in soup_child.find_all('a', recursive=False):
					item = {}
					item['names'] = utils.parse_names(soup_child_link)
					link = soup_child_link['href']
					link = utils.trim_absolute(link)
					item['link'] = link
					item['owner'] = False

					sibling = soup_child_link.next_sibling
					if sibling and not isinstance(sibling, bs4.Tag):
						sibling = sibling.next_sibling
					if sibling and isinstance(sibling, bs4.Tag) and sibling.name == 'img':
						if sibling['title'] == 'Owner, Leader or Representative':
							item['owner'] = True
					value.append(item)
			else:
				value = unicode(soup_child.string)

			if name == 'Type':
				org_info['type'] = value
			if name == 'Region':
				org_info['region'] = value
			if name == 'Staff' and isinstance(value, list):
				org_info['staff'] = value
			if name == 'Description':
				if soup_child.span:
					org_info['description'] = unicode(soup_child.span.string)
				else:
					org_info['description'] = value
	return org_info

def _parse_org_releases(table):
	releases = []
	if not table:
		return releases
	soup_rows = table.find_all('tr', recursive=False)
	if len(soup_rows) < 1:
		return releases

	for soup_row in soup_rows[1:]:
		release = {}
		soup_cells = soup_row.find_all('td')
		if len(soup_cells)<6:
			continue

		release['role'] = unicode(soup_cells[0].span.string)
		release['catalog'] = unicode(soup_cells[1].span.string)
		if soup_cells[2].img:
			release['reprint'] = True

		if soup_cells[4].a:		# event link
			link = soup_cells[4].a['href']
			link = utils.trim_absolute(link)
			event = {}
			event['link'] = link
			event['name'] = soup_cells[4].a['title']
			event['shortname'] = unicode(soup_cells[4].a.span.string)
			release['event'] = event

		if soup_cells[5].span.a:
			release['date'] = utils.parse_date_time(soup_cells[5].span.a.string)
		else:
			release['date'] = utils.parse_date_time(soup_cells[5].span.string)

		soup_album = soup_cells[3]
		if soup_album.a:
			link = soup_album.a['href']
			link = utils.trim_absolute(link)
			release['link'] = link
			release['titles'] = utils.parse_names(soup_album.a)
			release['type'] = soup_album.a['class'][1].split('-')[1]
		else:
			release['titles'] = {"en":soup_album.string.strip()}
		releases.append(release)
	releases = sorted(releases, key=lambda e:"{0[date]:0<14}".format(e))
	return releases

def _parse_websites(soup_websites):
	""" Given an array of divs containing website information """
	sites = {}
	for soup_category in soup_websites.find_all('div', recursive=False):
		category = unicode(soup_category.b.string)
		soup_links = soup_category.find_all('a', recursive=False)
		links = []
		for soup_link in soup_links:
			link = soup_link['href']
			name = unicode(soup_link.string)
			if link[0:9] == '/redirect':
				slashpos = link.find('/', 10)
				link = 'http://'+link[slashpos+1:]
			links.append({"link":utils.trim_absolute(link),"name":name})
		sites[category] = links
	return sites

