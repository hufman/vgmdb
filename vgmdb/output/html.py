from .commonutils import normalize_language_codes
import urlparse
import datetime

mimetypes = ['text/html']
name = 'html'

autoescape = True

class outputter(object):
	content_type = 'text/html; charset=utf-8'

	def __init__(self, config):
		import jinja2
		self._config = config
		self._templates = jinja2.Environment(loader=jinja2.PackageLoader('vgmdb.output'), trim_blocks=True, autoescape=autoescape)
		self._templates.filters['artist_type'] = self.artist_type
		self._templates.filters['absolute_linkhref'] = self.absolute_linkhref
		self._templates.filters['resource_attr'] = self.resource_attr
		self._templates.filters['link_subject'] = self.link_subject
		self._templates.filters['linkhref'] = self.linkhref
		self._templates.filters['link'] = self.link
		self._templates.filters['link_artist'] = self.link_artist
		self._templates.filters['link_album'] = self.link
		self._templates.filters['lang_names'] = self.lang_names
		self._templates.filters['format_date'] = self.format_date
		self._templates.filters['format_interval'] = self.format_interval
		self._templates.filters['or_unavailable'] = self.or_unavailable
		self._templates.tests['empty'] = lambda x:len(x)==0
		self._templates.tests['linktype'] = self.linktype
		self._Markup = jinja2.Markup
		self._escape = jinja2.escape

	def __call__(self, type, data, filterkey=None):
		template = self._templates.get_template('%s.djhtml'%type)
		return template.render(config=self._config, data=data, filterkey=filterkey)

	def artist_type(self, artist_data):
		types = []
		if artist_data.has_key('members') and len(artist_data['members']) > 0:
			types.append('foaf:Organization')
			types.append('schema:MusicGroup')
		else:
			types.append('foaf:Person')
			types.append('schema:Person')
			types.append('schema:MusicGroup')
		return ' '.join(types)

	def span_name(self, lang, name, rel="foaf:name"):
		lang = normalize_language_codes(lang)
		if rel:
			return '<span property="%s" lang="%s" xml:lang="%s">%s</span>'%(rel, lang, lang, self._escape(name))
		else:
			return '<span lang="%s" xml:lang="%s">%s</span>'%(lang, lang, self._escape(name))
	def lang_names(self, names, rel="foaf:name"):
		segments = []
		if isinstance(names, str) or isinstance(names, unicode):
			segments.append(self.span_name('en', names, rel))
		else:
			names = dict(names)
			if names.has_key('en'):
				segments.append(self.span_name('en', names['en'], rel))
				del names['en']
			for lang in sorted(names.keys()):
				segments.append(self.span_name(lang, names[lang], rel))
		result = ''.join(segments)
		if autoescape:
			result = self._Markup(result)
		return result

	def linkhref(self, link):
		if len(link)>0 and link[0] == '/':
			link = link[1:]
		return link
	def absolute_linkhref(self, link):
		return urlparse.urljoin(self._config.BASE_URL, self.linkhref(link))

	def resource_attr(self, href, type='resource', hash="subject"):
		if href != None and len(href)>0:
			return self._Markup("%s=\"%s\""%(type,self.link_subject(href, hash)))
		return ''
	def link_subject(self, href, hash="subject"):
		if href != None and len(href)>0:
			return self.linkhref(href) + "#" + hash
		return ''
	def link_artist(self, name, href, typeof="foaf:Person"):
		return self.link(name, href, typeof)
	def link(self, name, href, typeof=None, hide_empty_link=False):
		text = name
		if hide_empty_link and not href:
			return text
		if typeof:
			typeof=" typeof=\"%s\""%typeof
		else:
			typeof=""
		if len(href)>0 and href[0] == '/':
			href = href[1:]
		if len(href) > 0:
			result = u'<a href="%s" about="%s#subject"%s>%s</a>'%(href,href,typeof,text)
		else:
			result = u'<a%s>%s</a>'%(typeof,text)
		if autoescape:
			result = self._Markup(result)
		return result

	def format_date(self, date):
		def minyear(date):
			while date.year < 1900:
				date = date.replace(year=date.year+100)
			return date
		if date:
			year = date[0:4]
			if date[5:7] == '02' and len(date)>8 and int(date[8:10])>29:
				date = date[0:8] + "28" + date[10:]
			if date[0:4] == '0000':
				date = datetime.datetime.strptime(date, "0000-%m-%d")
				return date.strftime("%b %d")
			elif len(date) == 4:	# only a year
				date = datetime.datetime.strptime(date, "%Y")
				date = minyear(date)
				return date.strftime("%s"%year)
			elif len(date) == 7:	# YYYY-MM
				date = datetime.datetime.strptime(date, "%Y-%m")
				date = minyear(date)
				return date.strftime("%%b %s"%year)
			elif len(date) == 10:	# YYYY-MM-DD
				date = datetime.datetime.strptime(date, "%Y-%m-%d")
				date = minyear(date)
				return date.strftime("%%b %%d, %s"%year)
			else:
				return date
	def format_interval(self, time):
		if time:
			return "PT" + time
		else:
			return ''

	def or_unavailable(self, data):
		if data:
			result = data
		else:
			result = "<span class=\"unavailable\">Unavailable</span>"
			if autoescape:
				result = self._Markup(result)
		return result

	def linktype(self, link, is_type):
		qual_type = is_type + "/"
		if len(link) > len(qual_type) and \
		   link[:len(qual_type)] == qual_type:
			return True
		return False
