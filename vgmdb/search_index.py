from itertools import combinations
import logging
import os
import re
import time
from . import cache

from bloom_filter import BloomFilter

logger = logging.getLogger(__name__)

BLOOM_INDEX = {}
SEARCH_INDEX = {}


# Bloom Filter Helpers
def _copy_filter(src, dst):
	assert src.backend.num_bits == dst.backend.num_bits
	logger.info("Loading %s bits"%(src.backend.num_bits,))
	count = 0
	for bitno in xrange(src.backend.num_bits):
		if src.backend.is_set(bitno):
			count += 1
			#dst.backend.set(bitno)
		#else:
		#	dst.backend.clear(bitno)
	logger.info("Loaded %s/%s=%s bits"%(count, src.backend.num_bits, count/src.backend.num_bits))
def _load_filter(name, capacity):
	result = BloomFilter(max_elements=capacity, error_rate=0.1)
	try:
		source = BloomFilter(max_elements=capacity, error_rate=0.1, filename='/data/%s.blm'%(name,))
		_copy_filter(source, result)
	except:
		raise
		if os.path.exists('/data/%s.blm'%(name,)):
			logger.error("Failed to load bloom filter /data/%s.blm"%(name,))
	return result
def _save_filter(name, filter):
	try:
		output = BloomFilter(max_elements=filter.max_elements, error_rate=filter.error_rate, filename='/data/%s.blm'%(name,))
		_copy_filter(filter, output)
	except:
		raise
		logger.error("Failed to save bloom filter /data/%s.blm"%(name,))

def _add_keyword(bloom_filter, keyword):
	keyword = keyword.lower()
	length = len(keyword)
	for start, end in combinations(range(length), r=2):
		if start + 2 >= end:  # a string of length <=3
			continue
		if start + 15 < end:  # a string of length >= 16
			continue
		bloom_filter.add(keyword[start:end+1].encode('utf-8'))
def _add_keywords(bloom_filter, phrase):
	for piece in phrase.split():
		_add_keyword(bloom_filter, piece)
def _add_items(bloom_filter, items):
	for item in items:
		for title in set(item.get('titles', {}).values()):
			_add_keywords(bloom_filter, title)
		for name in set(item.get('names', {}).values()):
			_add_keywords(bloom_filter, name)
		if 'name_real' in item:
			_add_keywords(bloom_filter, item['name_real'])

def generate_search_index():
	import vgmdb.fetch
	logger.info("Starting to build search index")
	start = time.time()

	# use a local file cache
	orig_cache = cache.cache
	cache.cache = cache.MultiCache([cache.cache, cache.FileCache('/data')])

	for list, section in (('albumlist', 'albums'), ('artistlist', 'artists'), ('productlist', 'products')):
		bloom_elements = 100000000 if section == 'albums' else 1000000
		BLOOM_INDEX[section] = _load_filter(section, bloom_elements)
		SEARCH_INDEX[section] = []
		for letter in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
			id = letter + '1'
			while id:
				logger.info('... %s/%s' % (list, id))
				data = vgmdb.fetch.list(list, id, use_celery=False)
				SEARCH_INDEX[section].extend(data[section])
				_add_items(BLOOM_INDEX[section], data[section])
				id = data['pagination'].get('link_next', '/').split('/')[-1]  # next page
		_save_filter(section, BLOOM_INDEX[section])

	data = vgmdb.fetch.list('orglist', '', use_celery=False)
	SEARCH_INDEX['orgs'] = []
	for letter_data in data['orgs'].values():
		SEARCH_INDEX['orgs'].extend(letter_data)
	# insert into bloom filter
	BLOOM_INDEX['orgs'] = _load_filter('orgs', 100000)
	_add_items(BLOOM_INDEX['orgs'], SEARCH_INDEX['orgs'])
	_save_filter('orgs', BLOOM_INDEX['orgs'])

	cache.cache = orig_cache

	count = 0
	for section_data in SEARCH_INDEX.values():
		count += len(section_data)
	logger.info("Building index of %s items took %s" % (count, time.time() - start))

def search_locally(query):
	sections = {'albums':[],
	            'artists':[],
	            'orgs':[],
	            'products':[]}

	start = time.time()
	pieces = [p.decode('utf-8').lower() for p in query.split() if len(p) >= 3]
	substrings = ["(?=.*%s)"%(re.escape(p),) for p in pieces]
	needle = re.compile("".join(substrings), re.I)
	for section, data in SEARCH_INDEX.iteritems():
		# check if this section has this set of keywords
		if not all(piece[:16].encode('utf-8') in BLOOM_INDEX[section] for piece in pieces):
			logger.debug("%s not found in %s" % (pieces, section))
			continue  # and skip if not
		for item in data:
			# albums
			if any(needle.match(t) for t in item.get('titles', {}).values()):
				sections[section].append(item)
			# others
			elif any(needle.match(t) for t in item.get('names', {}).values()):
				sections[section].append(item)
			elif needle.match(item.get('name_real', '')):
				sections[section].append(item)
	logger.debug("Searching for %s locally took %s" % (pieces, time.time() - start,))
	fake = {
	    "meta":{},
	    "query":query,
	    "results":sections,
	    "sections":sorted(sections.keys())
	}
	return fake

