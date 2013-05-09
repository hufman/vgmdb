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
		self._templates.filters['linkhref'] = linkhref
		self._templates.filters['link_artist'] = link
		self._templates.filters['link_album'] = link
		self._templates.filters['lang_names'] = lang_names
		self._templates.filters['format_date'] = format_date
		self._templates.filters['or_unavailable'] = or_unavailable
		self._templates.tests['empty'] = lambda x:len(x)==0
		global Markup
		global escape
		Markup = jinja2.Markup
		escape = jinja2.escape

	def __call__(self, type, data):
		template = self._templates.get_template('%s.djhtml'%type)
		return template.render(config=vgmdb.config, data=data)

def span_name(lang, name):
	return '<span property="foaf:name" lang="%s" xml:lang="%s">%s</span>'%(lang, lang, escape(name))
def lang_names(names):
	segments = []
	if names.has_key('en'):
		segments.append(span_name('en', names['en']))
		del names['en']
	for lang in sorted(names.keys()):
		segments.append(span_name(lang, names[lang]))
	result = ''.join(segments)
	if autoescape:
		result = Markup(result)
	return result

def linkhref(link):
	if len(link)>0 and link[0] == '/':
		link = link[1:]
	return link

def link(name, link):
	if len(link)>0 and link[0] == '/':
		link = link[1:]
	result = u'<a href="%s" about="%s#subject">%s</a>'%(link,link,name)
	if '<span' not in name:		# isn't full of nested language spans, add the name property
		result = u'<a href="%s" about="%s#subject" property="foaf:name">%s</a>'%(link,link,name)
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
def or_unavailable(data):
	if data:
		result = data
	else:
		result = "<span class=\"unavailable\">Unavailable</span>"
		if autoescape:
			result = Markup(result)
	return result

