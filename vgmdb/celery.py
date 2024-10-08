from __future__ import absolute_import

from celery import Celery
from celery.signals import celeryd_init
from . import config

import logging
logging.basicConfig(level=logging.INFO)

broker = config.CELERY_BROKER
result = config.CELERY_RESULT_BACKEND
cache = config.CELERY_CACHE_BACKEND

celery = Celery('vgmdb.celery',
                broker=broker,
                backend=result,
                include=['vgmdb._tasks', 'vgmdb.sellers._tasks'])
celery.conf.update(
	CELERY_CACHE_BACKEND=cache
)

@celeryd_init.connect
def generate_search_index(*args, **kwargs):
	if config.SEARCH_INDEX:
		import vgmdb.search_index
		vgmdb.search_index.generate_search_index()

if __name__ == '__main__':
	celery.start()
