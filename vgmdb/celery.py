from __future__ import absolute_import

from celery import Celery
from . import config

broker = config.CELERY_BROKER
result = config.CELERY_RESULT_BACKEND
cache = config.CELERY_CACHE_BACKEND

celery = Celery('vgmdb.celery',
                broker=broker,
                backend=result,
                include=['vgmdb.sellers._tasks'])
celery.conf.update(
	CELERY_CACHE_BACKEND=cache
)

if __name__ == '__main__':
	celery.start()
