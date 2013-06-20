import bs4

from . import utils

def parse_productlist_page(html_source):
	productlist_info = {}
	productlist_info['products'] = []
	html_source = utils.fix_invalid_table(html_source)
	soup = bs4.BeautifulSoup(html_source)
	soup_pref = soup.find(id='pref')
	soup_innermain = soup_pref.parent
	if soup_innermain == None:
		return None	# info not found

	# parse product list
	soup_table = soup_innermain.find('table', recursive=False)
	soup_table = soup_table.find('table')
	for soup_row in soup_table.find_all('tr')[1:]:
		productlist_info['products'].append(_parse_product(soup_row))
	
	# parse page meat
	productlist_info['meta'] = {}
	soup_navbar = soup_innermain.find_all('div', recursive=False)[1]
	soup_sections = soup_navbar.find_all('div', recursive=False)
	soup_metadata = soup_sections[0]
	productlist_info['meta']['time'] = soup_metadata.div.b.string
	soup_letters = soup_sections[1]
	productlist_info['letters'] = []
	for soup_letter in soup_letters.find_all('td'):
		if soup_letter.a:
			letter = soup_letter.a.string
		if soup_letter.strong:
			letter = soup_letter.strong.string
		productlist_info['letters'].append(letter)
	
	return productlist_info

def _parse_product(soup_row):
	soup_cells = soup_row.find_all('td')
	soup_type = soup_cells[0]
	soup_name = soup_cells[1]

	# parse type
	soup_span = soup_type.span
	product_type = soup_span.string

	# parse title
	soup_link = soup_name.a
	product_link = soup_link['href']
	if product_link[0:7]=="http://":
		product_link = product_link[len("http://vgmdb.net"):]
	product_name = soup_link.string

	return {'link':product_link,
	        'type': product_type,
	        'name': product_name}

