import BeautifulSoup

def parse_artist_page(html_source):
	artist_info = {}
	soup = BeautifulSoup.BeautifulSoup(html_source)
	soup_profile = soup.findAll(id='innermain')[0]

	soup_name = soup_profile.findAll('span', recursive=False)[1]
	artist_info['name'] = soup_name.string.strip()

	soup_profile = soup_profile.div
	(soup_profile_left,soup_profile_right) = soup_profile.findAll('div', recursive=False, limit=2)

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

	return artist_info

def _parse_full_name(japan_name):
	name_data = {}
	if len(japan_name) > 0:
		if japan_name.find('('):
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
	for soup_item in soup_profile_left.findAll('div', recursive=False)[1:]:
		item_name = soup_item.b.string.strip()
		item_list = []
		list_item_pre = soup_item.br
		while list_item_pre:
			soup_item_data = list_item_pre.next
			if isinstance(soup_item_data, BeautifulSoup.NavigableString):
				texts = []
				while isinstance(soup_item_data, BeautifulSoup.NavigableString):
					texts.append(unicode(soup_item_data))
					soup_item_data = soup_item_data.next
				text = ''.join(texts).strip()
				if len(text) > 0:
					item_list.append(text)
			if isinstance(soup_item_data, BeautifulSoup.Tag):
				item_data = {}
				if soup_item_data.name == 'a':
					item_data['link'] = soup_item_data['href']
					item_data['name'] = soup_item_data.string
					pic_tag = soup_item_data.findNextSibling('img')
					if pic_tag:
						if pic_tag['src'] == 'http://media.vgmdb.net/img/owner.gif':
							item_data['owner'] = 'true'
					item_list.append(item_data)
				if soup_item_data.name == 'div' and \
				  soup_item_data.has_key('class') and \
				  'star' in soup_item_data['class']:
					total_stars = soup_item.findAll('div', 'star')
					stars = soup_item.findAll('div', 'star_on')
					item_list.append('%s/%s'%(len(stars),len(total_stars)))
					soup_votes = soup_item.findAll('div')[-1]
					ret['Album Votes'] = soup_votes.contents[0].string + \
					  soup_votes.contents[1] + \
					  soup_votes.contents[2].string + \
					  soup_votes.contents[3]
				if soup_item_data.name == 'span' and \
				  soup_item_data.has_key('class') and \
				  'time' in soup_item_data['class']:
					item_list.append(soup_item_data.string + soup_item_data.nextSibling)
					

			list_item_pre = list_item_pre.findNextSibling('br')
		if len(item_list) == 0:
			continue
		if len(item_list) == 1:
			ret[item_name] = item_list[0]
		if len(item_list) > 1:
			ret[item_name] = item_list
	return ret



