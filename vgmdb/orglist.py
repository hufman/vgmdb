import bs4

from . import utils

import re
islettermatcher = re.compile('[#A-Z]')

fetch_page = lambda id=None: utils.fetch_singlelist_page('org')

def parse_page(html_source):
	orglist_info = {}
	orglist_info['orgs'] = {}
	orglist_info['letters'] = []
	html_source = utils.fix_invalid_table(html_source)
	soup = bs4.BeautifulSoup(html_source)
	soup_pref = soup.find(id='pref')
	soup_innermain = soup_pref.parent
	if soup_innermain == None:
		return None	# info not found

	# parse org list
	soup_table = soup_innermain.find('table')
	for soup_cell in soup_table.find_all('td'):
		for soup_letter in soup_cell.find_all('h3'):
			letter = soup_letter.string
			if not letter or \
			   not islettermatcher.match(letter):
				letter = '#'
			if letter not in orglist_info['letters']:
				orglist_info['letters'].append(letter)
			if not orglist_info['orgs'].has_key(letter):
				orglist_info['orgs'][letter] = []
			letter_orglist = _parse_orglist(soup_letter.find_next('ul'))
			orglist_info['orgs'][letter].extend(letter_orglist)
	
	# parse page meat
	orglist_info['meta'] = {}
	
	return orglist_info

def _parse_orglist(soup_list):
	orglist = []
	for soup_org in soup_list.find_all('li'):
		orglist.append(_parse_org(soup_org))
	return orglist

def _parse_org(soup_org):
	# parse title
	soup_link = soup_org.a
	info = _parse_orglink(soup_link)

	for soup_extra in soup_org.find_all('div', recursive=False):
		extra_type = soup_extra.next_element
		extra_type = extra_type.split(':')[0].lower()
		extra_list = []
		for soup_link in soup_extra.find_all('a'):
			extra_list.append(_parse_orglink(soup_link))
		info[extra_type] = extra_list
	return info

def _parse_orglink(soup_link):
	org_link = soup_link['href']
	org_link = utils.trim_absolute(org_link)
	org_name = soup_link.string
	return {'link': org_link,
	        'names': {'en':org_name}}
