
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

