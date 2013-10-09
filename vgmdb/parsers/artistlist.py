import bs4

from . import utils

fetch_url = lambda id: utils.url_list_page('artists', id)
fetch_page = lambda id: utils.fetch_list_page('artists', id)

def parse_page(html_source):
	artistlist_info = {}
	artistlist_info['artists'] = []
	html_source = utils.fix_invalid_table(html_source)
	soup = bs4.BeautifulSoup(html_source)
	soup_innermain = soup.find(id='innermain')
	if soup_innermain == None:
		return None	# info not found

	# parse artist list
	artist_columns = [[],[],[]]
	soup_table = soup_innermain.div.table
	for soup_row in soup_table.find_all('tr'):
		soup_cells = soup_row.find_all('td')
		_parse_artist_info(soup_cells[0], artist_columns[0])
		_parse_artist_info(soup_cells[1], artist_columns[1])
		_parse_artist_info(soup_cells[2], artist_columns[2])
	for column in artist_columns:
		artistlist_info['artists'].extend(column)

	# parse page meat
	artistlist_info['meta'] = {}
	soup_navbar = soup_innermain.parent.div
	soup_metadata = soup_navbar.div
	artistlist_info['meta']['time'] = unicode(soup_metadata.b.string)
	soup_letters = soup_navbar.ul
	artistlist_info['letters'] = []
	for soup_letter in soup_letters.find_all('li'):
		letter = unicode(soup_letter.a.h3.string)
		artistlist_info['letters'].append(letter)

	return artistlist_info

def _parse_artist_info(soup_cell, append_target):
	if soup_cell.a:
		soup_artist = soup_cell.a
		link = soup_artist['href']
		name = unicode(soup_artist.string)
		artist_info = {'link':utils.trim_absolute(link),
		               'names':{'en':name}}
		if soup_cell.span:
			name_real = unicode(soup_cell.span.string)
			artist_info['name_real'] = name_real
		append_target.append(artist_info)
