import vgmdb.config
import datetime

mimetypes = ['text/html']
name = 'html'

autoescape = True

class outputter(object):
	content_type = 'text/html; charset=utf-8'

	def __init__(self):
		import jinja2
		self._templates = jinja2.Environment(loader=jinja2.PackageLoader('vgmdb.output'), trim_blocks=True, autoescape=autoescape)
		self._templates.filters['artist_type'] = artist_type
		self._templates.filters['linkhref'] = linkhref
		self._templates.filters['link'] = link
		self._templates.filters['link_artist'] = link_artist
		self._templates.filters['link_album'] = link
		self._templates.filters['lang_names'] = lang_names
		self._templates.filters['format_date'] = format_date
		self._templates.filters['format_interval'] = format_interval
		self._templates.filters['or_unavailable'] = or_unavailable
		self._templates.tests['empty'] = lambda x:len(x)==0
		global Markup
		global escape
		Markup = jinja2.Markup
		escape = jinja2.escape

	def __call__(self, type, data):
		template = self._templates.get_template('%s.djhtml'%type)
		return template.render(config=vgmdb.config, data=data)

def artist_type(artist_data):
	types = []
	if artist_data.has_key('members') and len(artist_data['members']) > 0:
		types.append('foaf:Organization')
		types.append('schema:MusicGroup')
	else:
		types.append('foaf:Person')
		types.append('schema:Person')
		types.append('schema:MusicGroup')
	return ' '.join(types)

def span_name(lang, name, rel="foaf:name"):
	if rel:
		return '<span property="%s" lang="%s" xml:lang="%s">%s</span>'%(rel, lang, lang, escape(name))
	else:
		return '<span lang="%s" xml:lang="%s">%s</span>'%(lang, lang, escape(name))
def lang_names(names, rel="foaf:name"):
	segments = []
	if isinstance(names, str) or isinstance(names, unicode):
		segments.append(span_name('en', names, rel))
	else:
		if names.has_key('en'):
			segments.append(span_name('en', names['en'], rel))
			del names['en']
		for lang in sorted(names.keys()):
			segments.append(span_name(lang, names[lang], rel))
	result = ''.join(segments)
	if autoescape:
		result = Markup(result)
	return result

def linkhref(link):
	if len(link)>0 and link[0] == '/':
		link = link[1:]
	return link

def link_artist(name, href, typeof="foaf:Person"):
	return link(name, href, typeof)
def link(name, href, typeof=None):
	text = name
	if '<span' not in name:		# isn't full of nested language spans, add the name property
		text = "<span property=\"foaf:name\">%s</span>"%name
	if typeof:
		typeof=" typeof="+typeof
	else:
		typeof=""
	if len(href)>0 and href[0] == '/':
		href = href[1:]
	if len(href) > 0:
		result = u'<a href="%s" about="%s#subject"%s>%s</a>'%(href,href,typeof,text)
	else:
		result = u'<a%s>%s</a>'%(typeof,text)
	if autoescape:
		result = Markup(result)
	return result

def format_date(date):
	if date:
		if date[0:4] == '0000':
			date = datetime.datetime.strptime(date, "0000-%m-%d")
			return date.strftime("%b %d")
		if len(date) == 4:	# only a year
			date = datetime.datetime.strptime(date, "%Y")
			return date.strftime("%Y")
		else:
			date = datetime.datetime.strptime(date, "%Y-%m-%d")
			return date.strftime("%b %d, %Y")
def format_interval(time):
	return "PT" + time

def or_unavailable(data):
	if data:
		result = data
	else:
		result = "<span class=\"unavailable\">Unavailable</span>"
		if autoescape:
			result = Markup(result)
	return result

