
import bs4

def fix_invalid_table(html_source):
	# fix missing </table>
	start = 0
	while True:
		start = html_source.find('<table', start+1)
		if start == -1:
			break
		prevtag_end = html_source.rfind('>', max(0,start-40), start)
		prevtag_start = html_source.rfind('<', max(0,start-40), prevtag_end)
		prevtag = html_source[prevtag_start:prevtag_end+1]
		if prevtag == '</tr>':
			html_source = html_source[:prevtag_end+1] + "</table>" + html_source[prevtag_end+1:]
			start = html_source.find('<table', prevtag_start)

	# fix duplicate <tr>
	start = 0
	while True:
		start = html_source.find('<tr>', start+1)
		if start == -1:
			break
		prevtag_end = html_source.rfind('>', max(0,start-40), start)
		prevtag_start = html_source.rfind('<', max(0,start-40), prevtag_end)
		prevtag = html_source[prevtag_start:prevtag_end+1]
		if prevtag == '<tr>':
			html_source = html_source[:prevtag_start] + html_source[prevtag_end+1:]
			start = prevtag_end

	# fix duplicate </tr>
	start = 0
	while True:
		start = html_source.find('</tr>', start+1)
		if start == -1:
			break
		prevtag_end = html_source.rfind('>', max(0,start-40), start)
		prevtag_start = html_source.rfind('<', max(0,start-40), prevtag_end)
		prevtag = html_source[prevtag_start:prevtag_end+1]
		if prevtag == '</tr>':
			html_source = html_source[:prevtag_start] + html_source[prevtag_end+1:]
			start = prevtag_end
	return html_source

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
	time = time.strip()
	if time == '0':
		return None
	if len(time) == 4:		# just a year
		return time
	space = time.find(' ')
	month = time[0:space]
	month = month[0:-1] if month[-1] == ',' else month
	if month in months:
		month = months.index(month) + 1
	elif month in fullmonths:
		month = fullmonths.index(month) + 1
	else:
		month = 0
	notmonth = time[space+1:].strip()
	if len(notmonth) == 4:
		return "%04d-%02d"%(int(notmonth),month)
	comma = time.find(',')
	if comma < 0 or len(time[comma:].strip())<4:	# no year
		day = int(time[space+1:])
		year = 0
	else:
		day = int(time[space+1:comma])
		year = int(time[comma+2:comma+2+4])
	timepos = comma+2+4+1
	if timepos >= len(time):		# there is not a time to parse
		return "%04d-%02d-%02d"%(year,month,day)
	else:
		hour = int(time[timepos:timepos+2])
		minute = int(time[timepos+3:timepos+5])
		ampm = time[timepos+6:timepos+8]
		if ampm == 'PM':
			hour += 12
		return "%04d-%02d-%02dT%02d:%02d"%(year,month,day,hour,minute)

def normalize_separated_date(weird_date, split):
	if not weird_date:
		return None
	elements = weird_date.split(split)
	output = [int(x) for x in elements if len(x)>0 and x[0]!='?']
	stringed_output = ["%04i"%output[0]]
	stringed_output.extend(["%02i"%x for x in output[1:]])
	return '-'.join(stringed_output)

def normalize_dotted_date(weird_date):
	""" Given a string like 2005.01.??, return 2005-01 """
	return normalize_separated_date(weird_date, '.')

def normalize_dashed_date(weird_date):
	""" Given a string like 2005-01-2 return 2005-01-02 """
	return normalize_separated_date(weird_date, '-')

def parse_names(soup_parent):
	"""
	Given an <a> with multiple span tags with different languages
	Return a dictionary with each language as a key
	   and the value being the name in that language
	"""
	info = {}
	shallow_string = parse_shallow_string(soup_parent)
	if len(shallow_string.strip())>0:
		info['en'] = shallow_string.strip()
	for soup_name in soup_parent.find_all('span', recursive=False):
		if not soup_name.has_attr('lang'):
			continue
		lang = soup_name['lang'].lower()
		name = parse_string(soup_name)
		info[lang] = name.strip()
	return info

def parse_shallow_string(soup_element):
	"""
	Given an element, return the strings inside, but not inside nested elements
	"""
	if not isinstance(soup_element, bs4.Tag):
		return soup_element.string
	else:
		bits = []
		for child in soup_element.children:
			if not isinstance(child, bs4.Tag):
				bits.append(child.string)
		return "".join(bits)
	
def parse_string(soup_element, _strip=True):
	"""
	Given an element, return the strings inside
	Useful for getting all the text out of something, even if it has <span> tags
	"""
	import re
	if not isinstance(soup_element, bs4.Tag):
		ret = soup_element.string
		ret = re.sub('\s+',' ', ret)
		return ret
	else:
		if soup_element.name == 'br':
			return '\n'
		omitted = ['em']
		if soup_element.name in omitted:
			return ''
		bits = []
		for child in soup_element.children:
			bits.append(parse_string(child, _strip=False))
		ret = "".join(bits)
		if _strip:
			ret = re.sub('\s*\n+\s*','\n', ret)
		return ret

def trim_absolute(link):
	if link[0:7]=="http://":
		link = link[len("http://vgmdb.net"):]
	return link

def parse_discography(soup_disco_table, label_type='roles'):
	"""
	Parse a discography table
	Each album has a span.label element. Set label_type to handle that element differently.
	On artist pages, pass label_type='roles'
	On product pages, pass label_type='classification'
	"""
	albums = []
	if soup_disco_table == None:
		return albums
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
			roles_str = parse_string(soup_album_info[1])
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

			reprint = False
			for soup_tag in soup_cells[1].find_all('img', recursive=False):
				if soup_tag.has_attr('alt') and \
				   soup_tag['alt'] == 'This album is a reprint':
					reprint = True

			album_info = {
			    "date": date,
			    label_type: roles,
			    "titles": titles,
			    "catalog": catalog,
			    "link": link,
			    "type": album_type
			}
			if reprint:
				album_info['reprint'] = True

			albums.append(album_info)
	albums = sorted(albums, key=lambda e:e['date'])
	return albums

def parse_meta(soup_meta_section):
	meta_info = {}
	soup_divs = soup_meta_section.find_all('div', recursive=False)
	for soup_div in soup_divs:
		label = soup_div.b.string.strip()
		if label == 'Added':
			date = soup_div.br.next_sibling.string.strip()
			time = soup_div.span.string.strip()
			time = parse_date_time("%s %s"%(date, time))
			meta_info['added_date'] = time
		if label == 'Added by':
			name = soup_div.b.next_sibling.string.strip()
			date = soup_div.br.next_sibling.string.strip()
			time = soup_div.span.string.strip()
			time = parse_date_time("%s %s"%(date, time))
			meta_info['added_user'] = name
			meta_info['added_date'] = time
		if label == 'Edited':
			date = soup_div.br.next_sibling.string.strip()
			time = soup_div.span.string.strip()
			time = parse_date_time("%s %s"%(date, time))
			meta_info['edited_date'] = time
		if label == 'Edited by':
			name = soup_div.b.next_sibling.string.strip()
			date = soup_div.br.next_sibling.string.strip()
			time = soup_div.span.string.strip()
			time = parse_date_time("%s %s"%(date, time))
			meta_info['edited_user'] = name
			meta_info['edited_date'] = time
		if label == 'Page traffic':
			soup_rows = soup_div.find_all('span', recursive=False)
			try:
				meta_info['visitors'] = int(soup_rows[0].string.strip())
				meta_info['freedb'] = int(soup_rows[1].string.strip())
			except:
				pass	# who puts a not-number in a page counter?
	return meta_info

