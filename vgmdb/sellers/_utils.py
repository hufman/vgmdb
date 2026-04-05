import re
import difflib
import logging

logger = logging.getLogger(__name__)

notislettermatcher = re.compile('[^A-Za-z0-9]')
def squash_str(value):
	return notislettermatcher.sub(' ', value.lower().strip())

def find_best_match(query, matches, threshold=0.7, key=lambda x:x):
	best = 0
	best_result = None
	for result in matches:
		s = difflib.SequenceMatcher(None, query, key(result))
		score = s.ratio()
		if score > best:
			best = score
			best_result = result
	if best > threshold:
		return best_result
	elif len(matches) > 0:
		logger.debug("Closest match to %s was %s score %s"%(query, key(best_result), best))

def primary_name(names):
	""" Given a dict of lang->names, return a default one """
	langs = list(names.keys())
	if 'en' in langs:
		return names['en']
	return names[langs[0]]
