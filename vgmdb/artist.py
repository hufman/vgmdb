import bs4

from . import utils

def parse_artist_page(html_source):
	artist_info = {}
	soup = bs4.BeautifulSoup(html_source)
	soup_profile = soup.find(id='innermain')

	soup_name = soup_profile.find_all('span', recursive=False)[1]
	artist_info['name'] = soup_name.string.strip()

	soup_profile = soup_profile.div
	(soup_profile_left,soup_profile_right) = soup_profile.find_all('div', recursive=False, limit=2)
	soup_right_column = soup.find(id='rightcolumn')

	# Determine sex
	soup_profile_sex_image = soup_profile_left.img
	if soup_profile_sex_image['src'] == '/db/icons/male.png':
		artist_info['sex'] = 'male'
	elif soup_profile_sex_image['src'] == '/db/icons/female.png':
		artist_info['sex'] = 'female'
	else:
		artist_info['sex'] = ''

	# Parse japanese name
	japan_name = soup_profile_left.span.string.strip()
	artist_info.update(_parse_full_name(japan_name))

	# Parse picture
	soup_picture = soup_profile_left.div.a
	if soup_picture:
		artist_info['picture_full'] = soup_picture['href']
		artist_info['picture_small'] = soup_picture.img['src']

	# Parse info
	artist_info['info'] = _parse_profile_info(soup_profile_left)
	artist_info.update(_promote_profile_info(artist_info['info']))

	# Parse Notes
	soup_notes = soup_profile_right.div.find_next_sibling('div').div
	artist_info['notes'] = soup_notes.contents[0].string if isinstance(soup_notes.contents[0], bs4.Tag) else soup_notes.string

	# Parse Discography
	soup_disco_table = soup_profile_right.br.find_next_sibling('div').find_next_sibling('div').div.table
	if soup_disco_table:
		artist_info['discography'] = _parse_discography(soup_disco_table)
	soup_featured_table = soup_profile_right.br.find_next_sibling('br').find_next_sibling('div').find_next_sibling('div').div.table
	if soup_featured_table:
		artist_info['featured_on'] = _parse_discography(soup_featured_table)

	# Parse for Websites
	soup_divs = soup_right_column.find_all('div', recursive=False)
	if soup_divs[0].div and soup_divs[0].div.h3 and soup_divs[0].div.h3.string == 'Websites':
		artist_info['websites'] = _parse_websites(soup_divs[1].div)

	# Parse for twitter handle
	twitters = []
	soup_twitters = soup_right_column.find_all('script')
	for soup_twitter in soup_twitters:
		widget_code = unicode(soup_twitter)
		index = widget_code.find("setUser('")
		if index > -1:
			index = index + 9
			end = widget_code.find("'", index)
			twitter = widget_code[index:end]
			twitters.append(twitter)

	if len(twitters) > 0:
		artist_info['twitter_names'] = twitters


	return artist_info

def _parse_full_name(japan_name):
	name_data = {}
	if len(japan_name) > 0:
		if japan_name.find('(') >= 0:
			(orig_name, gana_name) = japan_name.split('(',1)
			gana_name = gana_name[0:-1]	# strip )
			orig_name = orig_name.strip()
			gana_name = gana_name.strip()
			name_data['name_real'] = orig_name
			name_data['name_trans'] = gana_name
		else:
			name_data['name_real'] = japan_name
	return name_data

def _parse_profile_info(soup_profile_left):
	ret = {}
	for soup_item in soup_profile_left.find_all('div', recursive=False)[1:]:
		item_name = soup_item.b.string.strip()
		item_list = []
		list_item_pre = soup_item.br
		while list_item_pre:
			soup_item_data = list_item_pre.next
			if isinstance(soup_item_data, bs4.NavigableString):
				texts = []
				while isinstance(soup_item_data, bs4.NavigableString):
					texts.append(unicode(soup_item_data))
					soup_item_data = soup_item_data.next
				text = ''.join(texts).strip()
				if len(text) > 0:
					item_list.append(text)
			if isinstance(soup_item_data, bs4.Tag):
				item_data = {}
				if soup_item_data.name == 'a':
					item_data['link'] = soup_item_data['href']
					item_data['name'] = soup_item_data.string
					pic_tag = soup_item_data.find_next_sibling('img')
					if pic_tag:
						if pic_tag['src'] == 'http://media.vgmdb.net/img/owner.gif':
							item_data['owner'] = 'true'
					soup_names = soup_item_data.find_all('span', "artistname")
					if len(soup_names) > 0:
						del item_data['name']
						names = {}
						for soup_name in soup_names:
							lang = soup_name['lang']
							name = soup_name.string
							names[lang] = name
						item_data['names'] = names
					item_list.append(item_data)
				if soup_item_data.name == 'div' and \
				  soup_item_data.has_key('class') and \
				  'star' in soup_item_data['class']:
					total_stars = soup_item.find_all('div', 'star')
					stars = soup_item.find_all('div', 'star_on')
					item_list.append('%s/%s'%(len(stars),len(total_stars)))
					soup_votes = soup_item.find_all('div')[-1]
					ret['Album Votes'] = soup_votes.contents[0].string + \
					  soup_votes.contents[1] + \
					  soup_votes.contents[2].string + \
					  soup_votes.contents[3]
				if soup_item_data.name == 'span' and \
				  soup_item_data.has_key('class') and \
				  'time' in soup_item_data['class']:
					item_list.append(soup_item_data.string + soup_item_data.next_sibling)
					

			list_item_pre = list_item_pre.find_next_sibling('br')
		if len(item_list) == 0:
			continue
		if len(item_list) == 1 and isinstance(item_list[0], unicode):
			ret[item_name] = item_list[0]
		else:
			ret[item_name] = item_list
	return ret

def _promote_profile_info(profile_info):
	artist_info = {}
	if profile_info.has_key('Birthdate'):
		artist_info['birthdate'] = utils.parse_date_time(profile_info['Birthdate']);
	promote_types = {'aliases':'Aliases',
	                 'members':'Members',
	                 'units':'Units',
	                 'organizations':'Organizations'}
	for promote_key, info_key in promote_types.items():
		if not profile_info.has_key(info_key):
			continue
		artist_info[promote_key] = []
		for improper in profile_info[info_key]:
			proper = {}
			if isinstance(improper,basestring):
				proper['name'] = improper
			else:
				proper = improper
			artist_info[promote_key].append(proper)
	return artist_info

def _parse_discography(soup_disco_table):
	albums = []
	for soup_tbody in soup_disco_table.find_all("tbody", recursive=False):
		soup_rows = soup_tbody.find_all("tr", recursive=False)
		year = soup_rows[0].find('h3').string
		for soup_album_tr in soup_rows[1:]:
			soup_cells = soup_album_tr.find_all('td')
			month_day = soup_cells[0].string
			soup_album = soup_cells[1].a
			link = soup_album['href']
			link = link[len("http://vgmdb.net"):] if link[0:7]=="http://" else link
			album_type = soup_album['class'][1].split('-')[1]
			soup_album_info = soup_cells[1].find_all('span', recursive=False)
			catalog = soup_album_info[0].string
			roles_str = ''
			for soup_node in soup_album_info[1].children:
				if isinstance(soup_node, bs4.Tag):
					roles_str += soup_node.string
				else:
					roles_str += unicode(soup_node)
			roles = roles_str.split(',')
			roles = [x.strip() for x in roles]
			date = _normalize_date("%s.%s"%(year, month_day))

			titles = {}
			for soup_title in soup_album.find_all('span', recursive=False):
				title_lang = soup_title['lang'].lower()
				title_text = ""
				for child in soup_title.children:
					if isinstance(child, bs4.Tag):
						continue
					title_text = unicode(child)
					title_text = title_text.strip().strip('"')
				if title_lang and title_text:
					titles[title_lang] = title_text

			album_info = {
			    "date": date,
			    "roles": roles,
			    "titles": titles,
			    "catalog": catalog,
			    "link": link,
			    "type": album_type
			}
			albums.append(album_info)
	return albums

def _normalize_date(weird_date):
	""" Given a string like 2005.01.??, return 2005-01 """
	elements = weird_date.split('.')
	output = [x for x in elements if len(x)>0 and x[0]!='?']
	return '-'.join(output)

def _parse_websites(soup_websites):
	""" Given an array of divs containing website information """
	sites = {}
	for soup_category in soup_websites.find_all('div', recursive=False):
		category = soup_category.b.string
		soup_links = soup_category.find_all('a', recursive=False)
		links = []
		for soup_link in soup_links:
			link = soup_link['href']
			name = soup_link.string
			if link[0:9] == '/redirect':
				slashpos = link.find('/', 10)
				link = 'http://'+link[slashpos+1:]
			links.append({"link":link,"name":name})
		sites[category] = links
	return sites
