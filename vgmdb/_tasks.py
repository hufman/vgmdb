from . import data
from . import celery
celery = celery.celery

# Load up the available request functions
for name in dir(data):
	if name[0] == '_':
		continue
	attr = getattr(data, name)
	if not hasattr(attr, '__call__'):
		continue
	stubmaker = lambda attr: lambda *args,**kwargs: attr(*args,**kwargs)
	stub = stubmaker(attr)
	stub.__name__ = name
	wrapped = celery.task(default_retry_delay=5)(stub)
	locals()[name] = wrapped
