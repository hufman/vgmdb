import bs4

from operator import itemgetter
from . import utils

fetch_url = lambda id=None: utils.url_singlelist_page('events')
fetch_page = lambda id=None: utils.fetch_singlelist_page('events')

def parse_page(html_source):
	eventlist_info = {}
	eventlist_info['events'] = {}
	eventlist_info['years'] = []
	html_source = utils.fix_invalid_table(html_source)
	soup = bs4.BeautifulSoup(html_source)
	soup_pref = soup.find(id='pref')
	soup_innermain = soup_pref.parent
	if soup_innermain == None:
		return None	# info not found

	# parse event list
	soup_table = soup_innermain.find('table')
	for soup_cell in soup_table.find_all('td'):
		for soup_year in soup_cell.find_all('h3', recursive=False):
			year = unicode(soup_year.string)
			if year not in eventlist_info['years']:
				eventlist_info['years'].append(year)
			if not eventlist_info['events'].has_key(year):
				eventlist_info['events'][year] = []
			if not soup_year.find_next('ul'):
				import ipdb; ipdb.set_trace()
			year_eventlist = _parse_eventlist(soup_year.find_next('ul'))
			eventlist_info['events'][year].extend(year_eventlist)
			eventlist_info['events'][year].sort(key=itemgetter('startdate'))
	eventlist_info['years'].sort()
	
	# parse page meat
	eventlist_info['meta'] = {}
	
	return eventlist_info

def _parse_eventlist(soup_list):
	eventlist = []
	for soup_event in soup_list.find_all('div', recursive=False):
		eventlist.append(_parse_event(soup_event))
	return eventlist

def _parse_event(soup_event):
	# parse title
	if not soup_event.h3:
		import ipdb; ipdb.set_trace()
	if soup_event.h3 and not soup_event.h3.a:
		import ipdb; ipdb.set_trace()
	soup_link = soup_event.h3.a
	info = _parse_eventlink(soup_link)
	soup_short = soup_event.find('a', recursive=False)	# optional shorttag
	if soup_short:
		info['shortname'] = unicode(soup_short.span.string)
	soup_date = soup_event.div
	if soup_date:
		dates = soup_date.string.split('to')
		info['startdate'] = utils.parse_date_time(dates[0])
		if len(dates)>1:
			info['enddate'] = utils.parse_date_time(dates[1])
		else:
			info['enddate'] = info['startdate']
	return info

def _parse_eventlink(soup_link):
	event_link = soup_link['href']
	event_link = utils.trim_absolute(event_link)
	info = {'link': event_link,
	        'names': utils.parse_names(soup_link)}
	return info
