
import bs4

def parse_date_time(time):
	"""
	Receives a string like Mar 23, 1223
	Returns 1223-03-23

	Receives a string like Mar 23, 1223 01:33 PM
	Returns 1223-03-23T13:33
	"""
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', \
	          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	fullmonths = ['January', 'February', 'March', 'April', \
	              'May', 'June', 'July', 'August', \
	              'September', 'October', 'November', 'December']
	space = time.find(' ')
	month = time[0:space]
	if month in months:
		month = months.index(month) + 1
	elif month in fullmonths:
		month = fullmonths.index(month) + 1
	else:
		month = 0
	comma = time.find(',')
	day = int(time[space+1:comma])
	year = int(time[comma+2:comma+2+4])
	timepos = comma+2+4+1
	if timepos >= len(time):		# there is not a time to parse
		return "%02d-%02d-%02d"%(year,month,day)
	else:
		hour = int(time[timepos:timepos+2])
		minute = int(time[timepos+3:timepos+5])
		ampm = time[timepos+6:timepos+8]
		if ampm == 'PM':
			hour += 12
		return "%02d-%02d-%02dT%02d:%02d"%(year,month,day,hour,minute)

def normalize_dotted_date(weird_date):
	""" Given a string like 2005.01.??, return 2005-01 """
	elements = weird_date.split('.')
	output = [x for x in elements if len(x)>0 and x[0]!='?']
	return '-'.join(output)

def parse_names(soup_parent):
	"""
	Given an <a> with multiple span tags with different languages
	Return a dictionary with each language as a key
	   and the value being the name in that language
	"""
	info = {}
	if not soup_parent.span:
		info['en'] = soup_parent.string.strip()
	for soup_name in soup_parent.find_all('span', recursive=False):
		if not soup_name.has_key('lang'):
			continue
		lang = soup_name['lang'].lower()
		for child in soup_name.children:
			if not isinstance(child, bs4.Tag):
				name = child.string.strip()
		if soup_name.i:		# title has weird format
			name = soup_name.i.string.strip()
		info[lang] = name
	return info

def parse_discography(soup_disco_table):
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
			date = normalize_dotted_date("%s.%s"%(year, month_day))

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

