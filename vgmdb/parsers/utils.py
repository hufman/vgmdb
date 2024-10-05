# coding=utf-8
import bs4
import string
import sys
import unicodedata
import random
import re
import time
import urllib2
import urlparse

db_parser = re.compile(r'db/([a-z]+)\.php')

def fetch_page(url, retries=2):
	try:
		request = urllib2.Request(url)
		request.add_header('User-Agent', 'VGMdb/1.0 vgmdb.info')
		data = urllib2.urlopen(request, None, 30).read()
		data = data.decode('utf-8', 'ignore')
		return data
	except urllib2.HTTPError, error:
		print >> sys.stderr, "HTTPError %s while fetching %s" % (error.code, url)
		if error.code == 503 and retries:
			time.sleep(random.randint(500, 3000)/1000.0)
			return fetch_page(url, retries-1)
		print >> sys.stderr, error.read()
		raise

def url_info_page(type, id):
	return 'https://vgmdb.net/%s/%s?perpage=99999'%(type,id)
def fetch_info_page(type, id):
	return fetch_page(url_info_page(type, id))

def url_list_page(type, id):
	page = 1
	if len(id) > 1:
		page = int(id[1:])
	return 'https://vgmdb.net/db/%s.php?ltr=%s&field=title&perpage=100&page=%s'%(type,id,page)
def fetch_list_page(type, id):
	return fetch_page(url_list_page(type, id))

def url_singlelist_page(type):
	return 'https://vgmdb.net/db/%s.php'%(type,)
def fetch_singlelist_page(type):
	return fetch_page(url_singlelist_page(type))

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

def is_english(text):
	""" Given a string, perhaps someone's name
	    guess whether the string is entirely English or probably Japanese
	"""
	def extra_normalize(char):
		if char == u'ł':
			return 'l'
		return char
	def is_english_char(char):
		return char in string.ascii_letters
	def is_letter(char):
		return unicodedata.category(char)[0] == 'L'
	decomposed = unicodedata.normalize('NFD', text)   # split off accent chars
	trimmed = filter(is_letter, decomposed)
	trimmed = [extra_normalize(char) for char in trimmed]
	count = len(trimmed)
	count_english = len(filter(is_english_char, trimmed))
	if (count == 0):
		return True	# by default
	else:
		return (count_english / count) > 0.5

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

	day_year_found = re.match('([0-9][0-9]?),? ?([12][0-9][0-9][0-9])?', time[space+1:])
	if day_year_found is not None:
		if day_year_found.group(2) is not None:
			# found day and year
			day = int(day_year_found.group(1))
			year = int(day_year_found.group(2))
		else:
			day = int(day_year_found.group(1))
			year = 0
		timepos = space + 1 + day_year_found.end() + 1
	else:
		# couldn't parse day_year
		return None

	if timepos >= len(time):		# there is not a time to parse
		return "%04d-%02d-%02d"%(year,month,day)
	else:
		hour = int(time[timepos:timepos+2])
		minute = int(time[timepos+3:timepos+5])
		ampm = time[timepos+6:timepos+8]
		if ampm == 'PM' and hour < 12:
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
		langcode = 'en'
		if not is_english(shallow_string.strip()):
			langcode = 'ja'
		info[langcode] = shallow_string.strip()
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
		ret = unicode(soup_element.string)
	else:
		bits = []
		for child in soup_element.children:
			if not isinstance(child, bs4.Tag):
				bits.append(child.string)
		ret = "".join(bits)
	ret = re.sub('\s+', ' ', ret)
	ret = ret.replace(u'\u200b', '')
	return ret

def parse_string(soup_element, _strip=True):
	"""
	Given an element, return the strings inside
	Useful for getting all the text out of something, even if it has <span> tags
	"""
	if not isinstance(soup_element, bs4.Tag):
		ret = soup_element.string
		ret = re.sub('\s+',' ', ret)
		ret = ret.replace(u'\u200b', '')
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
		ret = ret.replace(u'\u200b', '')
		return ret

def extract_background_image(style):
	found = re.match(r"background-image:\surl\('([^)]*)'\)", style)
	if found:
		return found.group(1)

def media_thumb(medium_link):
	return medium_link.replace('medium-media', 'thumb-media')
def media_full(medium_link):
	return medium_link.replace('medium-media', 'media')

def product_color_type(soup_element):
	product_colors = {
		'#CEFFFF': 'Game',
		'yellowgreen': 'Animation',
		'silver': 'Radio & Drama',
		'white': 'Print Publication',
		'violet': 'Goods',
		'yellow': 'Franchise',
		'orange': 'Meta-franchise'
	}
	if soup_element:
		style = soup_element['style']
		if 'color:' in style:
			color = style.split(':')[1]
			if color in product_colors:
				return product_colors[color]
	return 'Other'

def next_tag(soup_element):
	next_element = soup_element.next_element
	while next_element and not isinstance(next_element, bs4.Tag):
		next_element = next_element.next_element
	return next_element

def next_sibling_tag(soup_element):
	next_element = soup_element.next_sibling
	while next_element and not isinstance(next_element, bs4.Tag):
		next_element = next_element.next_sibling
	return next_element

def trim_absolute(link):
	if link[0:17]=="http://vgmdb.net/":
		link = link[len("http://vgmdb.net/"):]
	if link[0:18]=="https://vgmdb.net/":
		link = link[len("https://vgmdb.net/"):]
	if len(link) > 0 and link[0] == '/':
		link = link[1:]
	return link
def force_absolute(link):
	if link.startswith('http://') or link.startswith('https://'):
		return link
	return urlparse.urljoin('https://vgmdb.net/', link)

def parse_vgmdb_link(link):
	vgmdb_link_types = {}

	link = trim_absolute(link)
	parsed_link = urlparse.urlparse(link)
	maybe_db = db_parser.match(parsed_link[2])
	if maybe_db:
		db_type = maybe_db.group(1)
		item_type = vgmdb_link_types.get(db_type, db_type)
		parsed_qs = urlparse.parse_qs(parsed_link[4])
		item_ids = parsed_qs.get('id', None)
		if item_ids:
			return "%s/%s"%(item_type, item_ids[0])
		else:
			return item_type
	else:
		return link

def strip_redirect(link):
	link = force_absolute(link)
	index = -1
	if link.startswith('http://vgmdb.net/redirect'):
		# skip the number
		index = link.find('/', len('http://vgmdb.net/redirect/'))
	if link.startswith('https://vgmdb.net/redirect'):
		# skip the number
		index = link.find('/', len('https://vgmdb.net/redirect/'))
	if index > 0:
		# get the link from the end of the redirect
		link = link[index+1:]
		if not (link.startswith('http://') or link.startswith('https://')):
			link = 'http://' + link
		return strip_redirect(link)   # handle nested redirects
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
		year = unicode(soup_rows[0].find('h3').string)
		for soup_album_tr in soup_rows[1:]:
			soup_cells = soup_album_tr.find_all('td')
			month_day = unicode(soup_cells[0].string)
			soup_album = soup_cells[1].a
			link = soup_album['href']
			link = trim_absolute(link)
			album_type = soup_album['class'][1].split('-')[1]
			soup_album_info = soup_cells[1].find_all('span', recursive=False)
			catalog = unicode(soup_album_info[0].string)
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
			album_info['reprint'] = reprint

			albums.append(album_info)
	albums = sorted(albums, key=lambda e:e['date'])
	return albums

def pagination_last_page(soup_pagination):
	""" soup_pagination = soup_innermain.find('div', {'class': 'pagenav'}, recursive=True) """
	last_page = 1
	control = soup_pagination.find('td', {'class': 'vbmenu_control'})
	if control:
		last_page = int(control.string.strip().split()[-1])
	return last_page

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

# conversion between category and type
_category_type = {
	"Game": "game", "Animation": "anime",
	"Publication": "print", "Audio Drama": "drama",
	"Live": "live", "Tokusatsu/Puppetry": "toku",
	"Multimedia Franchise": "mult",
	"Demo Scene": "demo", "Other Works": "works",
	"Enclosure/Promo": "bonus", "Doujin/Fanmade": "doujin",
	"Delayed/Cancelled": "cancel", "Bootleg": "bootleg"
}
_type_category = dict((v,k) for (k,v) in _category_type.iteritems())

category_type = lambda k: _category_type.get(k)
type_category = lambda k: _type_category.get(k)
