#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import traceback
import vgmdb.data
import vgmdb.fetch
import vgmdb.output
import vgmdb.parsers.album
import vgmdb.parsers.artist
import vgmdb.parsers.org
import vgmdb.parsers.event
import vgmdb.parsers.product
import json
import jsonschema

if len(sys.argv) > 1:
	mode_name = sys.argv[1]
	if mode_name.endswith('s'):
		plural = mode_name
		singular = mode_name[:-1]
	else:
		singular = mode_name
		plural = mode_name + 's'
	if not getattr(vgmdb.parsers, singular, None):
		print("Invalid mode %s, must be: album, artist, org, event, product")
		sys.exit(1)
	mode = {'singular': singular, 'plural': plural}
else:
	print("Must give a mode: album, artist, org, event, product")
	sys.exit(1)


def log_exception(link):
	""" Called from the context of an exception """
	filename = "%s.txt" % (link.replace('/', '_'),)
	with open(filename, 'w') as output:
		traceback.print_exc(file=output)

def log_info(link, info):
	""" Called from the context of an exception """
	filename = "%s.json" % (link.replace('/', '_'),)
	with open(filename, 'w') as output:
		json.dump(info, output, sort_keys=True,
		indent=4, separators=(',', ': '))

def log_result(link, result):
	if result:
		print("Failure with %s: %s" % (link, result))
	with open('result.csv', 'a') as output:
		line = '%s,%s\n' % (link, result)
		output.write(line)

def try_list():
	fetch_list = getattr(vgmdb.fetch, '%slist' % mode['singular'])
	initial = fetch_list()
	if isinstance(initial[mode['plural']], dict):
		# if all the letters are provided already
		for group in initial[mode['plural']].values():
			try_list_group(group)
	else:
		# if we have to iterate through pages of letters
		for letter in initial['letters']:
			list_data = fetch_list(letter)[mode['plural']]
			try_list_group(list_data)
def try_list_group(group_of_summaries):
	for summary in group_of_summaries:
		if 'link' in summary:
			link = summary['link']
			result = try_info(link)
			log_result(link, result)
def try_info(link):
	module = getattr(vgmdb.parsers, mode['singular'])
	page_type = mode['singular']
	config = vgmdb.config.get_defaults()
	id = link.split('/')[-1]
	# fetch
	try:
		data = module.fetch_page(id)
	except KeyboardInterrupt:
		raise
	except:
		return "Failed to fetch"
	# parse
	try:
		info = module.parse_page(data)
	except KeyboardInterrupt:
		raise
	except:
		log_exception(link)
		return "Failed to parse"
	# html format
	try:
		html = vgmdb.output.name_outputters['html'](config)(page_type, dict(info))
	except KeyboardInterrupt:
		raise
	except:
		log_exception(link)
		return "Failed to format as html"
	# rdf format
	try:
		rdf = vgmdb.output.name_outputters['rdf'](config)(page_type, dict(info))
	except KeyboardInterrupt:
		raise
	except:
		log_exception(link)
		return "Failed to format as rdf"
	# schema validation
	try:
		win = try_schema(page_type, info)
	except KeyboardInterrupt:
		raise
	except:
		log_exception(link)
		log_info(link, info)
		return "Failed against json schema"
	return None

def get_draft4_validator(schema_absolute_path):
	with open(schema_absolute_path) as schema_file:
		schema = json.load(schema_file)
	resolver = jsonschema.RefResolver("file://" + schema_absolute_path, schema)
	return jsonschema.Draft4Validator(schema, resolver=resolver)

def try_schema(type, info):
	# locate the schema
	script = os.path.abspath(__file__)
	script_base = os.path.dirname(script)
	base = os.path.dirname(script_base)
	schema_base = os.path.join(base, 'schema')
	schema_path = os.path.join(schema_base, type + '.json')
	# stub out some extra data
	info['link'] = 'unknown/1'
	info['vgmdb_link'] = 'http://vgmdb.net/unknown/1'
	vgmdb.data._calculate_ttl(info)
	# try to validate
	validator = get_draft4_validator(schema_path)
	validator.validate(info)

if __name__ == '__main__':
	try_list()
