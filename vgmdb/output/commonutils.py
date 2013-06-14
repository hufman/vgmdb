from re import sub

language_codes = {
	"English":"en",
	"English (iTunes)":"en",
	"English (Literal)":"en",
	"English (Official)":"en",
	"English (Translated)":"en",
	"English (Localized)":"en",
	"English PS1 Sound Test":"en",
	"Japanese":"ja",
	"German":"de",
	"Romaji":"ja-latn",
	"English / Japanese":"en-ja",
	"English / German":"en-de",
	"Italian/English/Japanese":"it-en-ja",
	"Chinese (Traditional)":"zh-hant",
	"Chinese (Simplified)":"zh-hans",
	"English Gaelic / Japanese":"gd-ja",
	"English / Gaelic":"en-gd",
	"English / Gaelic / Japanese":"en-gd-ja",
	"English / Bahasa Indonesia":"id",
	"English / French":"en-fr",
	"Japanese/Russian":"ja-ru",
	"German, English":"de-en",
	"French / Japanese / Russian / Polish":"fr-ja-ru-pl",
	"Japanese + Chinese":"ja-zh"
}
def normalize_language_codes(language):
	if language_codes.has_key(language):
		return language_codes[language]
	language = sub(r'[ /\+\(\[\[\)]', '', language)
	return language
