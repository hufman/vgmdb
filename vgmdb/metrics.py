import logging
logger = logging.getLogger(__name__)

client = None

def initialize(server, port):
	try:
		from statsd import StatsClient
		global client
		client = StatsClient(server, port, prefix='vgmdb')
		logger.info("Initialized StatsClient to %s:%s"%(server, port))
	except:
		logger.exception("Failed to connect StasClient to %s:%s"%(server, port))

# https://chase-seibert.github.io/blog/2013/12/17/python-decorator-optional-parameter.html
def instrumented(*args, **dec_kwargs):
	wrapped_func = None
	if len(args) == 1 and callable(args[0]):
		wrapped_func = args[0]

	def wrapper(func):
		from functools import wraps
		@wraps(func)
		def hook(*args, **kwargs):
			if client is None:
				return func(*args, **kwargs)

			module = dec_kwargs.get('module', func.__module__.split('.')[-1])
			name = dec_kwargs.get('name', func.__name__)
			page_type = dec_kwargs.get('page_type',
			                kwargs.get('page_type',
			                kwargs.get('type',
			                (args + (None,))[0]
			)))
			tags = {'method': name}
			if page_type:
				tags['page_type'] = page_type
			with timed(module, tags):
				return func(*args, **kwargs)
		return hook
	return wrapper(wrapped_func) if wrapped_func else wrapper

class timed(object):
	def __init__(self, name, tags):
		self.name = name
		self.tags = tags
		self.timer = None

		if client:
			# workaround for Granitosaurus/statsd-telegraf#2
			from statsd.client import Timer
			self.timer = Timer(client, "%s.timing"%(self.name,), rate=1, tags=self.tags)

	def __enter__(self):
		if self.timer:
			self.timer.start()
			client.incr("%s.count"%(self.name,), tags=self.tags)
			client.incr("%s.exceptions"%(self.name,), count=0, tags=self.tags)

	def __exit__(self, typ, value, tb):
		if self.timer:
			self.timer.stop()
			if typ:
				client.incr("%s.exceptions"%(self.name,), tags=self.tags)
		# bubble any exception

def incr(name, count=1, tags=None):
	if client:
		client.incr(name, count=count, tags=tags)

def decr(name, count=1, tags=None):
	if client:
		client.decr(name, count=count, tags=tags)

def gauge(name, value, delta=False, tags=None):
	if client:
		client.gauge(name, value, delta=delta, tags=tags)

def set(name, value, tags=None):
	if client:
		client.set(name, value, tags=tags)
