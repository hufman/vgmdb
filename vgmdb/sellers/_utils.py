import re
import difflib

notislettermatcher = re.compile('[^A-Za-z0-9]')
def squash_str(value):
	return notislettermatcher.sub(value.lower().strip(), '_')

def find_best_match(query, matches, threshold=0.7, key=lambda x:x):
	best = 0
	best_result = None
	for result in matches:
		s = difflib.SequenceMatcher(None, query, key(result))
		score = s.ratio()
		if score > best and score > threshold:
			best = score
			best_result = result
	return best_result

