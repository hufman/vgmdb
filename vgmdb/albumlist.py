import bs4

from . import utils

fetch_albumlist_page = utils.fetch_page

def parse_albumlist_page(html_source):
	albumlist_info = {}
	albumlist_info['albums'] = []
	html_source = utils.fix_invalid_table(html_source)
	soup = bs4.BeautifulSoup(html_source)
	soup_innermain = soup.find(id='innermain')
	if soup_innermain == None:
		return None	# info not found

	# parse album list
	soup_table = soup_innermain.div.table
	for soup_row in soup_table.find_all('tr')[1:]:
		soup_cells = soup_row.find_all('td')
		soup_catalog = soup_cells[0]
		soup_badges = soup_cells[1]
		soup_title = soup_cells[2]
		soup_date = soup_cells[3]

		# parse catalog
		soup_span = soup_catalog.span
		album_catalog = soup_span.string

		# parse title
		soup_link = soup_title.a
		album_type = soup_link['class'][-1].split('-')[1]
		album_link = soup_link['href']
		album_link = utils.trim_absolute(album_link)
		album_titles = utils.parse_names(soup_link)

		# parse date
		if soup_date.a:
			soup_date = soup_date.a
		album_date = utils.parse_date_time(soup_date.string)

		item = {'catalog': album_catalog,
		        'type': album_type,
		        'link': album_link,
		        'titles': album_titles,
		        'release_date': album_date
		}
		albumlist_info['albums'].append(item)
	
	# parse page meat
	albumlist_info['meta'] = {}
	soup_navbar = soup_innermain.parent.div
	soup_metadata = soup_navbar.div
	albumlist_info['meta']['time'] = soup_metadata.b.string
	soup_letters = soup_navbar.ul
	albumlist_info['letters'] = []
	for soup_letter in soup_letters.find_all('li'):
		letter = soup_letter.a.h3.string
		albumlist_info['letters'].append(letter)
	
	return albumlist_info


