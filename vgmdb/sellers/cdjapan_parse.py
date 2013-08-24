import urllib
import urlparse
import bs4


BASE_URL = 'http://www.cdjapan.co.jp/search3.html?q=%s&media=cd&r=any&step=20&order=score'

def search(query):
	html = load_search_html(query)
	data = parse_search_html(html)
	return data

def get_search_url(query):
	return BASE_URL%(urllib.quote(query),)

def load_search_html(query):
	url = get_search_url(query)
	return urllib.urlopen(url).read()

def parse_search_html(html):
	soup = bs4.BeautifulSoup(html)
	soup_results = soup.find('table', class_='result')
	results = parse_search_results(soup_results)
	return results

def parse_search_results(soup_results):
	results = []
	for soup_row in soup_results.find_all('tr', recursive=False):
		result = parse_search_result(soup_row)
		if result:
			results.append(result)
	return results

def parse_search_result(soup_row):
	info = {}
	soup_cells = soup_row.find_all('td', recursive=False)
	if len(soup_cells)<3:
		return None
	soup_cell_pic = soup_cells[0]
	soup_cell_desc = soup_cells[1]
	soup_cell_form = soup_cells[2]

	soup_link = soup_cell_pic.find('a')
	info['link'] = urlparse.urljoin(BASE_URL, soup_link['href'])
	soup_image = soup_link.find('img')
	info['image'] = urlparse.urljoin(BASE_URL, soup_image['src'])

	soup_parts = soup_cell_desc.find_all('div', recursive=False)
	soup_title = soup_cell_desc.h2.a
	info['title'] = soup_title.string
	soup_artist = soup_parts[0]
	info['artist'] = soup_artist.string
	soup_caption = soup_parts[1]
	info['caption'] = soup_caption.string

	soup_form = soup_cell_form.form
	soup_form_parts = soup_form.find_all('input', recursive=False)
	soup_prodkey = soup_form_parts[0]
	info['product_key'] = soup_prodkey['value']

	return info

if __name__ == "__main__":
	import pprint
	pprint.pprint(search('nobuo uematsu'))
