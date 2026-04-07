from re import sub

language_codes = {
	"english":"en",
	"englishgaelic":"gd",
	"gaelic":"gd",
	"japanese":"ja",
	"romaji":"ja-latn",
	"german":"de",
	"french":"fr",
	"bahasaindonesia":"id",
	"russian":"ru",
	"polish":"pl",
	"korean":"ko",
	"chinese":"zd",
	"chinesetraditional":"zh-hant",
	"chinesesimplified":"zh-hans"
}
def normalize_language_codes(language):
	language = language.replace('+','-').replace('&','-').replace(',','-')
	language = sub(r'[^A-Za-z-]', '', language)
	language = language.lower()
	language_parts = language.split('-')
	new_language_parts = []
	for part in language_parts:
		if part in language_codes:
			new_language_parts.append(language_codes[part])
		else:
			# try to find similar
			longest = ""
			for possible in language_codes.keys():
				pos_len = len(possible)
				if pos_len > len(part):
					# guess is not in part
					next
				if part[:pos_len] == possible and \
				   pos_len > len(longest):
					longest = possible
			if len(longest) > 0:
				new_language_parts.append(language_codes[longest])
			else:
				new_language_parts.append(part)
	return '-'.join(new_language_parts)

def format_duration(duration_str):
	while duration_str.count(':') < 2:
		duration_str = '00:' + duration_str
	hour, minute, second = duration_str.split(':')
	hour = int(hour)
	minute = int(minute)
	second = int(second)
	while second >= 60:
		second = second - 60
		minute = minute + 1
	while minute >= 60:
		minute = minute - 60
		hour = hour + 1
	return 'PT%02dH%02dM%02dS' % (hour, minute, second)
