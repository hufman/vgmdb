import bs4

from . import utils

fetch_url = lambda id: utils.url_list_page('product', id)
fetch_page = lambda id: utils.fetch_list_page('product', id)

def parse_page(html_source):
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
	
	# pagination row after the table
	page_count = 1
	soup_pagination = soup_innermain.find('div', {'class': 'pagenav'}, recursive=True)
	if soup_pagination:
		page_count = utils.pagination_last_page(soup_pagination)
	
	# parse page meta
	productlist_info['meta'] = {}
	soup_navbar = soup_innermain.find_all('div', recursive=False)[1]
	soup_sections = soup_navbar.find_all('div', recursive=False)
	soup_metadata = soup_sections[0]
	productlist_info['meta']['time'] = unicode(soup_metadata.div.b.string)
	soup_letters = soup_sections[1]
	productlist_info['letters'] = []
	for soup_letter in soup_letters.find_all('td'):
		if soup_letter.a:
			letter = unicode(soup_letter.a.string)
		if soup_letter.strong:
			letter = unicode(soup_letter.strong.string)
		productlist_info['letters'].append(letter)
	productlist_info['pagination'] = {'last': page_count}
	
	return productlist_info

def _parse_product(soup_row):
	soup_cells = soup_row.find_all('td')
	soup_type = soup_cells[0]
	soup_name = soup_cells[1]

	# parse type
	soup_span = soup_type.span
	product_type = unicode(soup_span.string)

	# parse title
	soup_link = soup_name.a
	product_link = soup_link['href']
	product_link = utils.trim_absolute(product_link)
	product_name = unicode(soup_link.string)

	return {'link':product_link,
	        'type': product_type,
	        'names': {'en':product_name}}

