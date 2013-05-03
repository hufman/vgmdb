from vgmdb.accept import parse_accept_header

# import submodules
import html
import json
import yaml

# As output modules are loaded the name_outputters and
# add_name_handler will be populated
name_outputters = {}	# store a list of outputter objects
mime_names = {}		# map mimetypes to names

def add_mime_name(mime, name):
	mime_names[mime] = name
def add_name_handler(name, outputter):
	name_outputters[name] = outputter

def load_plugins():
	from types import ModuleType
	for module in globals().values():
		if isinstance(module, ModuleType) and \
		   getattr(module, 'name') and \
		   getattr(module, 'mimetypes') and \
		   getattr(module, 'outputter'):
			name = module.name
			try:
				# try to create the outputter
				# Skip the plugin if any errors happen
				outputter = module.outputter()
				for type in module.mimetypes:
					add_mime_name(type, name)
				add_name_handler(name, outputter)
			except:
				# couldn't load plugin
				pass

def decide_format(forced, accept):
	format = "json"
	all_accepts = parse_accept_header(accept) or []
	for accepts in all_accepts:
		if accepts[0] in mime_names.keys():
			format = mime_names[accepts[0]]
			break
	if forced in mime_names.values():
		format = forced
	return format

def get_outputter(forced, accept):
	format = decide_format(forced, accept)
	return name_outputters[format]

load_plugins()
